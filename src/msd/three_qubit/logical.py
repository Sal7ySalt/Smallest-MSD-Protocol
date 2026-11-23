"""Steane-encoded 3-qubit [[3,1,1]] MSD circuit (21 qubits) with depolarizing noise.

Used by ``notebooks/three_qubit/logical_level/21_qubits.ipynb``. Each qubit of
the physical 3-qubit protocol becomes a 7-qubit Steane block; gates act
transversally.

Qubit layout (Qiskit little-endian; qubit 0 is the rightmost bit):
    0-6    block A, measured (reset qubits 0-2 later serve as syndrome ancillas)
    7-13   block B, measured
    14-20  block C, the output block
Physical circuit being encoded: CZ(A,B) and H(C); CZ(B,C); H on A and B;
measure A and B in Z and keep C only if both outcomes are 0.

Each ``logical_msd_*`` function returns ``(sum F, accepted)`` over accepted
shots; F is the fidelity of block C with the ideal encoded magic state
(computed with partial_trace). Unlike the 2-qubit module, no sum of F^2 is
returned. Gate noise is matched by name: 'ry' (input preparation), 'h'
(encoding and logical H), 'cz' (logical CZ) and 'cx' (encoder). The final
syndrome extraction uses custom-labelled gates and is free of gate noise;
readout errors are attached to qubits 0-13, so they also reach the
syndrome ancillas 0-2.

Arguments: p1 = one-qubit noise parameter, p2 = two-qubit noise parameter,
spam0 = P(read 1 | 0), spam1 = P(read 0 | 1). The meas/2q/1q variants take all
four so their signatures match; each uses only the noise it names.

Post-selection caveat: the conditional-save keys encode all 20 classical bits
(14 measurement bits plus the two 3-bit syndrome registers). The parsing
takes the leading 14 characters of the zero-padded binary string, which are
the measurement bits only when both syndrome registers read 0. See the
README, "Known caveats".
"""
import os
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
from qiskit_aer import AerSimulator
from qiskit_aer.library import SaveStatevector
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit.circuit.library import HGate, UnitaryGate, CXGate, RYGate, XGate, ZGate


# Target magic state of the 3-qubit protocol: RY(theta)|0> with
# tan(theta)^2 = (sqrt(5) - 1)/2, i.e. Bloch vector
# (sin theta, 0, cos theta) ~ (0.618, 0, 0.786).
theta = np.arctan(np.sqrt((np.sqrt(5) - 1) / 2))

# Define custom gate labels so noise can be attached by gate name.
# The noise models target 'h', 'cz', 'cx' and 'ry'. These relabelled copies are
# used only in the final syndrome extraction and recovery, which therefore
# stay noiseless. (ry_custom is defined but unused.)
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
    # Unitary [[7,1,3]] encoder: the state on qubit `start` becomes the logical
    # state of qubits start..start+6 (the other six must start in |0>).
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
    # One round of Steane syndrome extraction on the block at `start` with three
    # ancillas. Stabilizer supports (block-local): {0,1,2,3}, {1,2,4,5},
    # {2,3,5,6}; bit j of each syndrome register reports stabilizer j.
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
    # Lookup-table decoder: each nonzero 3-bit syndrome matches exactly one
    # qubit whose stabilizer-membership pattern equals it.
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
    # "All" case: p1 on 'h' and 'ry', p2 on 'cz' and 'cx', readout on qubits 0-13.
    circuit = QuantumCircuit(21, 14)

    # Prepare and encode three logical input magic states (blocks A, B, C).
    for i in [0, 7, 14]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)
    encoding(circuit, 14)

    # Apply the logical three-qubit MSD circuit transversally:
    # CZ_L(A,B) and H_L(C); CZ_L(B,C); H_L on A and B.
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
    
    # Measure blocks A and B (qubits 0-13) for post-selection; reset qubits
    # 0-2 for reuse as syndrome ancillas of block C.
    circuit.measure([i for i in range(14)], [i for i in range(14)]) 
    circuit.reset([q for q in range(3)])
    
    # Final syndrome extraction and recovery on output block C, free of gate
    # noise (readout noise on ancillas 0-2 still applies when spam > 0).
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
    # (Note: partial_trace also traces out the reused ancillas 0-2.)
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        # [0:7] holds clbits 13..7 (block B) and [7:14] clbits 6..0 (block A)
        # when the syndrome registers are 0. Both halves get identical checks,
        # so the "block1"/"block2" labels are interchangeable.
        binary_string = format(int(key, 16), 'b').zfill(14)
        
        block1_syndrome = str(binary_string)[0:7]
        block2_syndrome = str(binary_string)[7:14]
        
        # Check stabilizer and logical parities for the first block.
        # Character -1-j is block-local qubit j: three Z-type stabilizers, then
        # the logical Z_L on qubits {0,1,4}.
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
        # This is the encoded version of keeping outcome 00 in the physical protocol.
        if parity_list == [0, 0, 0, 0, 0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                red_sv = partial_trace(sv, trace_list)
                sumfid += state_fidelity(ideal_sv, red_sv)
                
    if accepted == 0:
        return 0.0, 0.0

    return sumfid, accepted
    
    
# Logical MSD with ideal error correction in the end. No depolarizing noise added
# "Ideal" case: only the input preparation 'ry' is noisy (p1).
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
    # (blocks A and B = qubits 0-13; qubits 0-2 become ancillas for block C)
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
    # (one key per distinct classical record; see the module docstring)
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        # [0:7] holds clbits 13..7 (block B) and [7:14] clbits 6..0 (block A)
        # when the syndrome registers are 0. Both halves get identical checks,
        # so the "block1"/"block2" labels are interchangeable.
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
# "Meas" case: noisy 'ry' (p1) plus readout errors on qubits 0-13; p2 is unused.
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
    # (blocks A and B = qubits 0-13; qubits 0-2 become ancillas for block C)
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
    # (one key per distinct classical record; see the module docstring)
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        # [0:7] holds clbits 13..7 (block B) and [7:14] clbits 6..0 (block A)
        # when the syndrome registers are 0. Both halves get identical checks,
        # so the "block1"/"block2" labels are interchangeable.
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
# "2Q" case: noisy 'ry' (p1) plus p2 on 'cz' and 'cx'; spam0/spam1 are unused.
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
    # (blocks A and B = qubits 0-13; qubits 0-2 become ancillas for block C)
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
    # (one key per distinct classical record; see the module docstring)
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        # [0:7] holds clbits 13..7 (block B) and [7:14] clbits 6..0 (block A)
        # when the syndrome registers are 0. Both halves get identical checks,
        # so the "block1"/"block2" labels are interchangeable.
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
# "1Q" case: p1 on 'h' and 'ry'; p2, spam0 and spam1 are unused.
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
    # (blocks A and B = qubits 0-13; qubits 0-2 become ancillas for block C)
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
    # (one key per distinct classical record; see the module docstring)
    trace_list = [i for i in range(14)]
    sumfid = 0
    accepted = 0
    for key, sv_list in res_statevectors.items():
        # [0:7] holds clbits 13..7 (block B) and [7:14] clbits 6..0 (block A)
        # when the syndrome registers are 0. Both halves get identical checks,
        # so the "block1"/"block2" labels are interchangeable.
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