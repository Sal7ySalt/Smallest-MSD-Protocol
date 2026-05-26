import os
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
from qiskit_aer import AerSimulator
from qiskit_aer.library import SaveStatevector
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit.circuit.library import HGate, UnitaryGate, CXGate, RYGate, XGate, ZGate


# Define the exotic magic-state angle.
theta = np.arctan(np.sqrt((np.sqrt(5) - 1) / 2))

# Define custom gate labels so noise can be attached by gate name.
H_matrix = HGate().to_matrix()
hadamard_custom = UnitaryGate(H_matrix, label='hadamard_custom')

CX_matrix = CXGate().to_matrix()
cx_custom = UnitaryGate(CX_matrix, label='cx_custom')

RY_matrix = RYGate(theta).to_matrix()
ry_custom = UnitaryGate(RY_matrix, label='ry_custom')

X_matrix = XGate().to_matrix()
x_custom = UnitaryGate(X_matrix, label='x_custom')

Z_matrix = ZGate().to_matrix()
z_custom = UnitaryGate(Z_matrix, label='z_custom')


def encoding(qc: QuantumCircuit, start: int):
    # Encode one logical qubit into a 7-qubit Steane block.
    for i in [2, 3, 5]:
        qc.h(start + i)
    
    cx_list = [
        [0, 4], [0, 1], [2, 6], [2, 4], [2, 0],
        [5, 6], [5, 1], [5, 0], [3, 6], [3, 1], [3, 4]
    ]

    for cx in cx_list:
        cx[0] += start
        cx[1] += start
        qc.cx(cx[0], cx[1])


def ideal_syndrome_meas(qc, start, ancillas_start, x_syndrome, z_syndrome):
    # Measure the three X-type stabilizers using ancillas in the X basis.
    for i in range(3):
        qc.append(hadamard_custom, [ancillas_start + i])
    
    for i in [0, 1, 2, 3]:
        qc.append(cx_custom, [ancillas_start, start + i])
    for i in [1, 2, 4, 5]:
        qc.append(cx_custom, [ancillas_start + 1, start + i])
    for i in [2, 3, 5, 6]:
        qc.append(cx_custom, [ancillas_start + 2, start + i])
        
    for i in range(3):
        qc.append(hadamard_custom, [ancillas_start + i])
    
    qc.measure([ancillas_start + i for i in range(3)], x_syndrome)
    qc.reset([ancillas_start + i for i in range(3)])
    
    # Measure the three Z-type stabilizers using ancillas in the computational basis.
    for i in [0, 1, 2, 3]:
        qc.append(cx_custom, [start + i, ancillas_start])
    for i in [1, 2, 4, 5]:
        qc.append(cx_custom, [start + i, ancillas_start + 1])
    for i in [2, 3, 5, 6]:
        qc.append(cx_custom, [start + i, ancillas_start + 2])
        
    qc.measure([ancillas_start + i for i in range(3)], z_syndrome)
    qc.reset([ancillas_start + i for i in range(3)])
    

def ideal_recovery(qc: QuantumCircuit, start: int, x_syndrome: ClassicalRegister, z_syndrome: ClassicalRegister):
    # Apply Z corrections based on the X-type syndrome.
    with qc.if_test((x_syndrome, 0b001)):
        qc.append(z_custom, [start])
    with qc.if_test((x_syndrome, 0b010)):
        qc.append(z_custom, [start + 4])
    with qc.if_test((x_syndrome, 0b011)):
        qc.append(z_custom, [start + 1])
    with qc.if_test((x_syndrome, 0b100)):
        qc.append(z_custom, [start + 6])
    with qc.if_test((x_syndrome, 0b101)):
        qc.append(z_custom, [start + 3])
    with qc.if_test((x_syndrome, 0b110)):
        qc.append(z_custom, [start + 5])
    with qc.if_test((x_syndrome, 0b111)):
        qc.append(z_custom, [start + 2])
        
    # Apply X corrections based on the Z-type syndrome.
    with qc.if_test((z_syndrome, 0b001)):
        qc.append(x_custom, [start])
    with qc.if_test((z_syndrome, 0b010)):
        qc.append(x_custom, [start + 4])
    with qc.if_test((z_syndrome, 0b011)):
        qc.append(x_custom, [start + 1])
    with qc.if_test((z_syndrome, 0b100)):
        qc.append(x_custom, [start + 6])
    with qc.if_test((z_syndrome, 0b101)):
        qc.append(x_custom, [start + 3])
    with qc.if_test((z_syndrome, 0b110)):
        qc.append(x_custom, [start + 5])
    with qc.if_test((z_syndrome, 0b111)):
        qc.append(x_custom, [start + 2])
        

# Construct the ideal encoded output state for fidelity comparisons.
ideal = QuantumCircuit(7)
ideal.ry(theta, 0)
encoding(ideal, 0)
ideal_sv = Statevector.from_instruction(ideal)
        
        
def logical_msd_all_errors(num_shots, p1, p2, spam0, spam1):
    # Logical MSD with noise on 1Q gates, 2Q gates, and measurements.
    circuit = QuantumCircuit(21, 14)

    # Prepare and encode three logical input magic states.
    for i in [0, 7, 14]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)
    encoding(circuit, 14)

    # Apply the logical three-qubit MSD circuit transversally.
    for i in range(7):
        circuit.cz(i, i + 7)
        circuit.h(i + 14)

    for i in range(7):
        circuit.cz(i + 7, i + 14)
        
    for i in range(14):
        circuit.h(i)
    
    # Build the full circuit-level noise model.
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['h'])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['ry'])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cz'])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cx']) 
    
    readout_err = ReadoutError([
        [1 - spam0, spam0],
        [spam1, 1 - spam1]
    ])
    
    for q in range(14):
        noise_model.add_readout_error(readout_err, [q])
    
    # Measure the first two logical blocks for post-selection.
    circuit.measure([i for i in range(14)], [i for i in range(14)]) 
    circuit.reset([q for q in range(3)])
    
    # Perfect final syndrome measurement and recovery on the output block.
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)

    ideal_syndrome_meas(circuit, 14, 0, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 14, x_syndrome, z_syndrome)
    
    # Save post-measurement statevectors conditioned on classical outcomes.
    circuit.append(
        SaveStatevector(num_qubits=21, label="state_post", conditional=True, pershot=True),
        circuit.qubits
    )

    backend = AerSimulator(
        noise_model=noise_model,
        method='statevector',
        max_parallel_threads=os.cpu_count(),
        max_parallel_experiments=1,
        max_parallel_shots=0
    )

    job = backend.run(circuit, shots=num_shots)
    result = job.result()
    res_statevectors = result.data()['state_post']
    
    # Trace out the two measured blocks and average fidelity over accepted shots.
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        binary_string = format(int(key, 16), 'b').zfill(14)
        
        block1_syndrome = str(binary_string)[0:7]
        block2_syndrome = str(binary_string)[7:14]
        
        # Check stabilizer and logical parities for the first block.
        block1_parity1 = (
            int(block1_syndrome[-1]) + int(block1_syndrome[-2])
            + int(block1_syndrome[-3]) + int(block1_syndrome[-4])
        ) % 2
        block1_parity2 = (
            int(block1_syndrome[-2]) + int(block1_syndrome[-3])
            + int(block1_syndrome[-5]) + int(block1_syndrome[-6])
        ) % 2
        block1_parity3 = (
            int(block1_syndrome[-3]) + int(block1_syndrome[-4])
            + int(block1_syndrome[-6]) + int(block1_syndrome[-7])
        ) % 2
        block1_logical_op = (
            int(block1_syndrome[-1]) + int(block1_syndrome[-2])
            + int(block1_syndrome[-5])
        ) % 2 
        
        # Check stabilizer and logical parities for the second block.
        block2_parity1 = (
            int(block2_syndrome[-1]) + int(block2_syndrome[-2])
            + int(block2_syndrome[-3]) + int(block2_syndrome[-4])
        ) % 2
        block2_parity2 = (
            int(block2_syndrome[-2]) + int(block2_syndrome[-3])
            + int(block2_syndrome[-5]) + int(block2_syndrome[-6])
        ) % 2
        block2_parity3 = (
            int(block2_syndrome[-3]) + int(block2_syndrome[-4])
            + int(block2_syndrome[-6]) + int(block2_syndrome[-7])
        ) % 2
        block2_logical_op = (
            int(block2_syndrome[-1]) + int(block2_syndrome[-2])
            + int(block2_syndrome[-5])
        ) % 2
        
        parity_list = [
            block1_parity1, block1_parity2, block1_parity3, block1_logical_op,
            block2_parity1, block2_parity2, block2_parity3, block2_logical_op
        ]

        # Accept only runs with trivial stabilizer and logical parity checks.
        if parity_list == [0, 0, 0, 0, 0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                red_sv = partial_trace(sv, trace_list)
                sumfid += state_fidelity(ideal_sv, red_sv)
                
    if accepted == 0:
        return 0.0, 0.0

    return sumfid, accepted
    
    
# Logical MSD with ideal error correction in the end. No depolarizing noise added
def logical_msd_no_errors(num_shots, p1):
    circuit = QuantumCircuit(21,14)
    # State encoding on each Steane code block
    for i in [0,7,14]:
        circuit.ry(theta, i)
    encoding(circuit, 0)
    encoding(circuit, 7)
    encoding(circuit, 14)
    # Logical MSD circuit
    for i in range(7):
        circuit.cz(i, i+7)
        circuit.h(i+14)

    for i in range(7):
        circuit.cz(i+7, i+14)
        
    for i in range(14):
        circuit.h(i)
    

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['ry'])
    
    # Measure first two code blocks and reset first three qubits for stabilizer measurements
    circuit.measure([i for i in range(14)], [i for i in range(14)]) 
    circuit.reset([q for q in range(3)])
    
    # Measuring stabilizer measurements and applying correction
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)
    ideal_syndrome_meas(circuit, 14, 0, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 14, x_syndrome, z_syndrome)
    
    circuit.append(SaveStatevector(num_qubits=21, label="state_post", conditional=True, pershot=True), circuit.qubits)

    backend = AerSimulator(noise_model=noise_model, method='statevector', max_parallel_threads=os.cpu_count(), max_parallel_experiments=1, max_parallel_shots=0)
    job = backend.run(circuit, shots=num_shots)
    result = job.result()
    res_statevectors = result.data()['state_post']
    
    # Iterating through all unqiue measurement strings
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        binary_string = format(int(key, 16), 'b').zfill(14)
        
        block1_syndrome = str(binary_string)[0:7]
        block2_syndrome = str(binary_string)[7:14]
        
        block1_parity1 = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-4])) % 2
        block1_parity2 = (int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-5]) + int(block1_syndrome[-6])) % 2
        block1_parity3 = (int(block1_syndrome[-3]) + int(block1_syndrome[-4]) + int(block1_syndrome[-6]) + int(block1_syndrome[-7])) % 2
        block1_logical_op = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-5])) % 2 
        
        block2_parity1 = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-4])) % 2
        block2_parity2 = (int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-5]) + int(block2_syndrome[-6])) % 2
        block2_parity3 = (int(block2_syndrome[-3]) + int(block2_syndrome[-4]) + int(block2_syndrome[-6]) + int(block2_syndrome[-7])) % 2
        block2_logical_op = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-5])) % 2
        
        parity_list = [block1_parity1, block1_parity2, block1_parity3, block1_logical_op, block2_parity1, block2_parity2, block2_parity3, block2_logical_op]
        # Keep runs with all even parities on stabilizer and logical operator measurements
        if (parity_list == [0,0,0,0,0,0,0,0]):
            accepted += len(sv_list)
            for sv in sv_list:
                red_sv = partial_trace(sv, trace_list)
                sumfid += state_fidelity(ideal_sv, red_sv)
                
    if accepted == 0:
        return 0.0, 0.0
    else:
        return sumfid, accepted


# Logical MSD with ideal error correction in the end. Depolarizing noise added to only measurements
def logical_msd_meas_errors(num_shots, p1, p2, spam0, spam1):
    circuit = QuantumCircuit(21,14)
    # State encoding on each Steane code block
    for i in [0,7,14]:
        circuit.ry(theta, i)
    encoding(circuit, 0)
    encoding(circuit, 7)
    encoding(circuit, 14)
    # Logical MSD circuit
    for i in range(7):
        circuit.cz(i, i+7)
        circuit.h(i+14)

    for i in range(7):
        circuit.cz(i+7, i+14)
        
    for i in range(14):
        circuit.h(i)
    

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['ry'])
    
    readout_err = ReadoutError([[1-spam0, spam0],  # P(0|0), P(1|0)
                            [spam1, 1-spam1]]) # P(0|1), P(1|1)
    
    for q in range(14):
        noise_model.add_readout_error(readout_err, [q])
    
    # Measure first two code blocks and reset first three qubits for stabilizer measurements
    circuit.measure([i for i in range(14)], [i for i in range(14)]) 
    circuit.reset([q for q in range(3)])
    
    # Measuring stabilizer measurements and applying correction
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)
    ideal_syndrome_meas(circuit, 14, 0, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 14, x_syndrome, z_syndrome)
    
    circuit.append(SaveStatevector(num_qubits=21, label="state_post", conditional=True, pershot=True), circuit.qubits)

    backend = AerSimulator(noise_model=noise_model, method='statevector', max_parallel_threads=os.cpu_count(), max_parallel_experiments=1, max_parallel_shots=0)
    job = backend.run(circuit, shots=num_shots)
    result = job.result()
    res_statevectors = result.data()['state_post']
    
    # Iterating through all unqiue measurement strings
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        binary_string = format(int(key, 16), 'b').zfill(14)
        
        block1_syndrome = str(binary_string)[0:7]
        block2_syndrome = str(binary_string)[7:14]
        
        block1_parity1 = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-4])) % 2
        block1_parity2 = (int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-5]) + int(block1_syndrome[-6])) % 2
        block1_parity3 = (int(block1_syndrome[-3]) + int(block1_syndrome[-4]) + int(block1_syndrome[-6]) + int(block1_syndrome[-7])) % 2
        block1_logical_op = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-5])) % 2 
        
        block2_parity1 = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-4])) % 2
        block2_parity2 = (int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-5]) + int(block2_syndrome[-6])) % 2
        block2_parity3 = (int(block2_syndrome[-3]) + int(block2_syndrome[-4]) + int(block2_syndrome[-6]) + int(block2_syndrome[-7])) % 2
        block2_logical_op = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-5])) % 2
        
        parity_list = [block1_parity1, block1_parity2, block1_parity3, block1_logical_op, block2_parity1, block2_parity2, block2_parity3, block2_logical_op]
        # Keep runs with all even parities on stabilizer and logical operator measurements
        if (parity_list == [0,0,0,0,0,0,0,0]):
            accepted += len(sv_list)
            for sv in sv_list:
                red_sv = partial_trace(sv, trace_list)
                sumfid += state_fidelity(ideal_sv, red_sv)
                
    if accepted == 0:
        return 0.0, 0.0
    else:
        return sumfid, accepted
    
    
# Logical MSD with ideal error correction in the end. Depolarizing noise added to only 2-qubit gates
def logical_msd_2q_errors(num_shots, p1, p2, spam0, spam1):
    circuit = QuantumCircuit(21,14)
    # State encoding on each Steane code block
    for i in [0,7,14]:
        circuit.ry(theta, i)
    encoding(circuit, 0)
    encoding(circuit, 7)
    encoding(circuit, 14)
    # Logical MSD circuit
    for i in range(7):
        circuit.cz(i, i+7)
        circuit.h(i+14)

    for i in range(7):
        circuit.cz(i+7, i+14)
        
    for i in range(14):
        circuit.h(i)
    

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['ry'])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cz'])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cx']) 
    
    # Measure first two code blocks and reset first three qubits for stabilizer measurements
    circuit.measure([i for i in range(14)], [i for i in range(14)]) 
    circuit.reset([q for q in range(3)])
    
    # Measuring stabilizer measurements and applying correction
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)
    ideal_syndrome_meas(circuit, 14, 0, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 14, x_syndrome, z_syndrome)
    
    circuit.append(SaveStatevector(num_qubits=21, label="state_post", conditional=True, pershot=True), circuit.qubits)

    backend = AerSimulator(noise_model=noise_model, method='statevector', max_parallel_threads=os.cpu_count(), max_parallel_experiments=1, max_parallel_shots=0)
    job = backend.run(circuit, shots=num_shots)
    result = job.result()
    res_statevectors = result.data()['state_post']
    
    # Iterating through all unqiue measurement strings
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        binary_string = format(int(key, 16), 'b').zfill(14)
        
        block1_syndrome = str(binary_string)[0:7]
        block2_syndrome = str(binary_string)[7:14]
        
        block1_parity1 = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-4])) % 2
        block1_parity2 = (int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-5]) + int(block1_syndrome[-6])) % 2
        block1_parity3 = (int(block1_syndrome[-3]) + int(block1_syndrome[-4]) + int(block1_syndrome[-6]) + int(block1_syndrome[-7])) % 2
        block1_logical_op = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-5])) % 2 
        
        block2_parity1 = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-4])) % 2
        block2_parity2 = (int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-5]) + int(block2_syndrome[-6])) % 2
        block2_parity3 = (int(block2_syndrome[-3]) + int(block2_syndrome[-4]) + int(block2_syndrome[-6]) + int(block2_syndrome[-7])) % 2
        block2_logical_op = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-5])) % 2
        
        parity_list = [block1_parity1, block1_parity2, block1_parity3, block1_logical_op, block2_parity1, block2_parity2, block2_parity3, block2_logical_op]
        # Keep runs with all even parities on stabilizer and logical operator measurements
        if (parity_list == [0,0,0,0,0,0,0,0]):
            accepted += len(sv_list)
            for sv in sv_list:
                red_sv = partial_trace(sv, trace_list)
                sumfid += state_fidelity(ideal_sv, red_sv)
                
    if accepted == 0:
        return 0.0, 0.0
    else:
        return sumfid, accepted
    
    
# Logical MSD with ideal error correction in the end. Depolarizing noise added to only 1-qubit gates 
def logical_msd_1q_errors(num_shots, p1, p2, spam0, spam1):
    circuit = QuantumCircuit(21,14)
    # State encoding on each Steane code block
    for i in [0,7,14]:
        circuit.ry(theta, i)
    encoding(circuit, 0)
    encoding(circuit, 7)
    encoding(circuit, 14)
    # Logical MSD circuit
    for i in range(7):
        circuit.cz(i, i+7)
        circuit.h(i+14)

    for i in range(7):
        circuit.cz(i+7, i+14)
        
    for i in range(14):
        circuit.h(i)
    

    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['h'])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1, 1), ['ry'])
    
    # Measure first two code blocks and reset first three qubits for stabilizer measurements
    circuit.measure([i for i in range(14)], [i for i in range(14)]) 
    circuit.reset([q for q in range(3)])
    
    # Measuring stabilizer measurements and applying correction
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)
    ideal_syndrome_meas(circuit, 14, 0, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 14, x_syndrome, z_syndrome)
    
    circuit.append(SaveStatevector(num_qubits=21, label="state_post", conditional=True, pershot=True), circuit.qubits)

    backend = AerSimulator(noise_model=noise_model, method='statevector', max_parallel_threads=os.cpu_count(), max_parallel_experiments=1, max_parallel_shots=0)
    job = backend.run(circuit, shots=num_shots)
    result = job.result()
    res_statevectors = result.data()['state_post']
    
    # Iterating through all unqiue measurement strings
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        binary_string = format(int(key, 16), 'b').zfill(14)
        
        block1_syndrome = str(binary_string)[0:7]
        block2_syndrome = str(binary_string)[7:14]
        
        block1_parity1 = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-4])) % 2
        block1_parity2 = (int(block1_syndrome[-2]) + int(block1_syndrome[-3]) + int(block1_syndrome[-5]) + int(block1_syndrome[-6])) % 2
        block1_parity3 = (int(block1_syndrome[-3]) + int(block1_syndrome[-4]) + int(block1_syndrome[-6]) + int(block1_syndrome[-7])) % 2
        block1_logical_op = (int(block1_syndrome[-1]) + int(block1_syndrome[-2]) + int(block1_syndrome[-5])) % 2 
        
        block2_parity1 = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-4])) % 2
        block2_parity2 = (int(block2_syndrome[-2]) + int(block2_syndrome[-3]) + int(block2_syndrome[-5]) + int(block2_syndrome[-6])) % 2
        block2_parity3 = (int(block2_syndrome[-3]) + int(block2_syndrome[-4]) + int(block2_syndrome[-6]) + int(block2_syndrome[-7])) % 2
        block2_logical_op = (int(block2_syndrome[-1]) + int(block2_syndrome[-2]) + int(block2_syndrome[-5])) % 2
        
        parity_list = [block1_parity1, block1_parity2, block1_parity3, block1_logical_op, block2_parity1, block2_parity2, block2_parity3, block2_logical_op]
        # Keep runs with all even parities on stabilizer and logical operator measurements
        if (parity_list == [0,0,0,0,0,0,0,0]):
            accepted += len(sv_list)
            for sv in sv_list:
                red_sv = partial_trace(sv, trace_list)
                sumfid += state_fidelity(ideal_sv, red_sv)
                
    if accepted == 0:
        return 0.0, 0.0
    else:
        return sumfid, accepted