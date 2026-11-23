"""Steane-encoded 2-qubit [[2,1,1]] MSD circuit with convergence-axis noise.

Identical to ``logical_depolarizing.py`` except that every noise channel is
the single-qubit Kraus map rho -> (1 - p) rho + p |k><k| (tensored for CX),
which replaces the qubit by the fixed state |k> = alpha|0> + beta|1> with
Bloch vector (-z_star, 0, -x_star). Notebooks and file names call this
"convergence-axis" or "stable-axis" noise. Used by
``notebooks/two_qubit/logical_level/convergence_axis.ipynb``.

Qubit layout (Qiskit little-endian; qubit 0 is the rightmost bit):
    0-6    block A, the output block (control of the transversal CX)
    7-13   block B, measured and used for post-selection
    7-9    reused (after reset) as ancillas for the final syndrome extraction
Classical bits: 0-6 hold B's measurement; then a 3-bit X-syndrome and a 3-bit
Z-syndrome register are added for the final error correction of A.

Each ``logical_msd_*`` function builds the full circuit, attaches noise to a
subset of gate names, runs ``num_shots`` shots of the statevector simulator,
and returns ``(sum F, sum F^2, accepted)`` over accepted shots, where F is the
fidelity of block A with the ideal encoded magic state. Noise is matched by
gate name: 'ry' (input preparation), 'h' (encoding and transversal H) and
'cx' (encoding and transversal CX). The final syndrome extraction uses
custom-labelled copies of H, CX, X and Z, so gate noise never reaches it.
Readout errors are attached to qubits 7-13 and therefore also affect the
syndrome ancillas 7-9.

Arguments: p1 = one-qubit noise parameter, p2 = two-qubit noise parameter,
spam0 = P(read 1 | 0), spam1 = P(read 0 | 1). Some functions accept
parameters they do not use, so call signatures stay aligned with the notebooks.

Post-selection: Aer's conditional-save keys encode all 13 classical bits
(B's 7 bits in clbits 0-6, then the X- and Z-syndrome registers of A in
clbits 7-12). Only the low 7 bits (B's measurement) decide acceptance.
"""
import os
from qiskit import QuantumCircuit, ClassicalRegister
from qiskit.quantum_info import Statevector, state_fidelity, partial_trace
from qiskit_aer import AerSimulator
from qiskit_aer.library import SaveStatevector
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError, kraus_error
from qiskit.circuit.library import HGate, UnitaryGate, CXGate, RYGate, XGate, ZGate


# Target magic state |T*> = RY(theta)|0>, Bloch vector (x_star, 0, z_star) with
# x_star = sin(theta) ~ 0.8393: the nontrivial fixed point of the [[2,1,1]]
# protocol's Bloch map (x, z) -> (2z, x^2)/(1 + z^2).
x_star = 1/3 * (-2 + np.cbrt(19-3*np.sqrt(33)) + np.cbrt(19+3*np.sqrt(33)))
theta = np.arcsin(x_star)

# Define custom gate labels so noise can be attached by gate name.
# The noise models below target the standard names 'h', 'cx' and 'ry'. These
# relabelled copies are used only in the final syndrome extraction and
# recovery, so those steps stay noiseless. (ry_custom is defined but unused.)
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


# To build a custom noise model
# Convergence-axis channel: with probability error_prob the qubit is replaced by
# |ket_bar>, Bloch vector (-z_star, 0, -x_star). The Kraus operators are
# K0 = sqrt(1-p) I, K1 = sqrt(p)|k><0|, K2 = sqrt(p)|k><1|, and the two-qubit
# version applies the one-qubit channel to both qubits.
alpha_star = np.sqrt((1-x_star)/2)
beta_star = -np.sqrt((1+x_star)/2)
ket_bar = alpha_star * np.array([[1],[0]]) + beta_star * np.array([[0],[1]])

def kraus0(error_prob):
    return np.sqrt(1-error_prob) * np.eye(2)
def kraus1(error_prob):
    return np.sqrt(error_prob) * np.matmul(ket_bar, np.array([[1,0]]))
def kraus2(error_prob):
    return np.sqrt(error_prob) * np.matmul(ket_bar, np.array([[0,1]]))
def one_qubit_kraus_noise(error_prob):
    K0 = kraus0(error_prob)
    K1 = kraus1(error_prob)
    K2 = kraus2(error_prob)
    return kraus_error([K0, K1, K2])
def two_qubit_kraus_noise(error_prob):
    oneq_error = one_qubit_kraus_noise(error_prob)
    twoq_error = oneq_error.tensor(oneq_error)
    return twoq_error


def encoding(qc: QuantumCircuit, start: int):
    # Encode one logical qubit into a 7-qubit Steane block.
    # Unitary [[7,1,3]] encoder: the state on qubit `start` (block-local qubit
    # 0) becomes the logical state of qubits start..start+6; the other six
    # qubits must start in |0>. Block-local qubit j is qubit start + j.
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
    # One round of Steane syndrome extraction on the block at `start`, using
    # three ancillas at ancillas_start..+2 (measured and reset twice). Stabilizer
    # supports (block-local): {0,1,2,3}, {1,2,4,5}, {2,3,5,6}; bit j of each
    # syndrome register reports stabilizer j. Only custom-labelled gates are
    # used, so the gate noise model does not act here.
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
    # Lookup-table decoder for single-qubit errors: each nonzero 3-bit syndrome
    # matches exactly one qubit whose stabilizer-membership pattern equals it
    # (e.g. 0b011 = stabilizers 0 and 1 only = qubit 1).
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
# ideal_conj (length 128) is the conjugated reference vector for block A.
ideal = QuantumCircuit(7)
ideal.ry(theta, 0)
encoding(ideal, 0)
ideal_sv = Statevector.from_instruction(ideal)
ideal_conj = ideal_sv.data.conj()


def logical_msd_all_errors(num_shots, p1, p2, spam0, spam1):
    # Logical MSD with noise on 1Q gates, 2Q gates, and measurements.
    # "All" case: p1 on 'ry' and 'h', p2 on 'cx', readout errors on qubits 7-13.
    circuit = QuantumCircuit(14, 7)

    # Prepare and encode the two logical input magic states (blocks A and B).
    for i in [0, 7]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)

    # Apply the logical two-qubit MSD circuit transversally: CX_L (A controls
    # B), then H_L on A.
    for i in range(7):
        circuit.cx(i, i + 7)
        circuit.h(i)
    
    # Build the noise model for this case (see the comment above the function).
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['h'])
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['ry'])
    noise_model.add_all_qubit_quantum_error(two_qubit_kraus_noise(p2), ['cx']) 
    
    readout_err = ReadoutError([
        [1 - spam0, spam0],
        [spam1, 1 - spam1]
    ])
    
    for q in range(7,14):
        noise_model.add_readout_error(readout_err, [q])
    
    # Measure block B (qubits 7-13) into clbits 0-6, then reset qubits 7-9 so
    # they can serve as syndrome ancillas for block A.
    circuit.measure([i for i in range(7,14)], [i for i in range(7)]) 
    circuit.reset([q for q in range(7,10)])
    
    # Final syndrome extraction and recovery on output block A, free of gate
    # noise (readout noise on ancillas 7-9 still applies when spam > 0).
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)

    ideal_syndrome_meas(circuit, 0, 7, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 0, x_syndrome, z_syndrome)
    
    # Save post-measurement statevectors conditioned on classical outcomes.
    # Result: {hex key of all classical bits: [one statevector per shot]}.
    circuit.append(
        SaveStatevector(num_qubits=14, label="state_post", conditional=True, pershot=True),
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
    
    # Average the fidelity of block A over accepted shots. trace_list is unused:
    # the fidelity is computed directly from each statevector below.
    trace_list = [i for i in range(7,14)]
    sumfid = 0
    sumfid2 = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        # The key encodes all 13 classical bits; B's measurement is clbits 0-6,
        # the low 7 bits. Mask them out so the syndrome registers of block A
        # (clbits 7-12) never enter the post-selection decision.
        binary_string = format(int(key, 16) & 0x7F, '07b')
        
        block_syndrome = str(binary_string)[0:7]
        
        # Parities of B's measured bits (character -1-j = block-local qubit j):
        # the three Z-type stabilizers and the logical Z_L on qubits {0,1,4}.
        block_parity1 = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-3]) + int(block_syndrome[-4])
        ) % 2
        block_parity2 = (
            int(block_syndrome[-2]) + int(block_syndrome[-3])
            + int(block_syndrome[-5]) + int(block_syndrome[-6])
        ) % 2
        block_parity3 = (
            int(block_syndrome[-3]) + int(block_syndrome[-4])
            + int(block_syndrome[-6]) + int(block_syndrome[-7])
        ) % 2
        block_logical_op = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-5])
        ) % 2 
        
        parity_list = [
            block_parity1, block_parity2, block_parity3, block_logical_op
        ]

        # Accept only runs with trivial stabilizer and logical parity checks.
        # This is the encoded version of keeping outcome 0 in the physical protocol.
        if parity_list == [0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                # F = <ideal|rho|ideal>; rows are qubits 7-13, columns are qubits 0-6.
                # Little-endian reshape to (128, 128): summing |row . ideal*|^2
                # over rows gives <ideal|rho_A|ideal> without forming rho_A.
                fid = np.sum(np.abs(np.asarray(sv).reshape(128, 128) @ ideal_conj)**2)
                sumfid += fid
                sumfid2 += fid**2
                
    if accepted == 0:
        return 0.0, 0.0, 0

    return sumfid, sumfid2, accepted


# Logical MSD with ideal error correction in the end. No depolarizing noise added
# "Ideal" case: only the input preparation 'ry' is noisy (parameter p1). It is
# the baseline that the other cases are compared against.
def logical_msd_no_errors(num_shots, p1):
    circuit = QuantumCircuit(14, 7)

    # Prepare and encode the two logical input magic states (blocks A and B).
    for i in [0, 7]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)

    # Apply the logical two-qubit MSD circuit transversally: CX_L (A controls
    # B), then H_L on A.
    for i in range(7):
        circuit.cx(i, i + 7)
        circuit.h(i)
    
    # Build the noise model for this case (see the comment above the function).
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['ry'])
    
    # Measure block B (qubits 7-13) into clbits 0-6, then reset qubits 7-9 so
    # they can serve as syndrome ancillas for block A.
    circuit.measure([i for i in range(7,14)], [i for i in range(7)]) 
    circuit.reset([q for q in range(7,10)])
    
    # Final syndrome extraction and recovery on output block A, free of gate
    # noise (readout noise on ancillas 7-9 still applies when spam > 0).
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)

    ideal_syndrome_meas(circuit, 0, 7, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 0, x_syndrome, z_syndrome)
    
    # Save post-measurement statevectors conditioned on classical outcomes.
    # Result: {hex key of all classical bits: [one statevector per shot]}.
    circuit.append(
        SaveStatevector(num_qubits=14, label="state_post", conditional=True, pershot=True),
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
    
    # Average the fidelity of block A over accepted shots. trace_list is unused:
    # the fidelity is computed directly from each statevector below.
    trace_list = [i for i in range(7,14)]
    sumfid = 0
    sumfid2 = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        # The key encodes all 13 classical bits; B's measurement is clbits 0-6,
        # the low 7 bits. Mask them out so the syndrome registers of block A
        # (clbits 7-12) never enter the post-selection decision.
        binary_string = format(int(key, 16) & 0x7F, '07b')
        
        block_syndrome = str(binary_string)[0:7]
        
        # Parities of B's measured bits (character -1-j = block-local qubit j):
        # the three Z-type stabilizers and the logical Z_L on qubits {0,1,4}.
        block_parity1 = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-3]) + int(block_syndrome[-4])
        ) % 2
        block_parity2 = (
            int(block_syndrome[-2]) + int(block_syndrome[-3])
            + int(block_syndrome[-5]) + int(block_syndrome[-6])
        ) % 2
        block_parity3 = (
            int(block_syndrome[-3]) + int(block_syndrome[-4])
            + int(block_syndrome[-6]) + int(block_syndrome[-7])
        ) % 2
        block_logical_op = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-5])
        ) % 2 
        
        parity_list = [
            block_parity1, block_parity2, block_parity3, block_logical_op
        ]

        # Accept only runs with trivial stabilizer and logical parity checks.
        # This is the encoded version of keeping outcome 0 in the physical protocol.
        if parity_list == [0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                # F = <ideal|rho|ideal>; rows are qubits 7-13, columns are qubits 0-6.
                # Little-endian reshape to (128, 128): summing |row . ideal*|^2
                # over rows gives <ideal|rho_A|ideal> without forming rho_A.
                fid = np.sum(np.abs(np.asarray(sv).reshape(128, 128) @ ideal_conj)**2)
                sumfid += fid
                sumfid2 += fid**2
                
    if accepted == 0:
        return 0.0, 0.0, 0

    return sumfid, sumfid2, accepted


# Logical MSD with ideal error correction in the end. Depolarizing noise added to only measurements
# "Meas" case: noisy 'ry' (p1) plus readout errors (spam0, spam1) on qubits 7-13.
def logical_msd_meas_errors(num_shots, p1, spam0, spam1):
    circuit = QuantumCircuit(14, 7)

    # Prepare and encode the two logical input magic states (blocks A and B).
    for i in [0, 7]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)

    # Apply the logical two-qubit MSD circuit transversally: CX_L (A controls
    # B), then H_L on A.
    for i in range(7):
        circuit.cx(i, i + 7)
        circuit.h(i)
    
    # Build the noise model for this case (see the comment above the function).
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['ry'])
    
    readout_err = ReadoutError([
        [1 - spam0, spam0],
        [spam1, 1 - spam1]
    ])
    
    for q in range(7,14):
        noise_model.add_readout_error(readout_err, [q])
    
    # Measure block B (qubits 7-13) into clbits 0-6, then reset qubits 7-9 so
    # they can serve as syndrome ancillas for block A.
    circuit.measure([i for i in range(7,14)], [i for i in range(7)]) 
    circuit.reset([q for q in range(7,10)])
    
    # Final syndrome extraction and recovery on output block A, free of gate
    # noise (readout noise on ancillas 7-9 still applies when spam > 0).
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)

    ideal_syndrome_meas(circuit, 0, 7, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 0, x_syndrome, z_syndrome)
    
    # Save post-measurement statevectors conditioned on classical outcomes.
    # Result: {hex key of all classical bits: [one statevector per shot]}.
    circuit.append(
        SaveStatevector(num_qubits=14, label="state_post", conditional=True, pershot=True),
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
    
    # Average the fidelity of block A over accepted shots. trace_list is unused:
    # the fidelity is computed directly from each statevector below.
    trace_list = [i for i in range(7,14)]
    sumfid = 0
    sumfid2 = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        # The key encodes all 13 classical bits; B's measurement is clbits 0-6,
        # the low 7 bits. Mask them out so the syndrome registers of block A
        # (clbits 7-12) never enter the post-selection decision.
        binary_string = format(int(key, 16) & 0x7F, '07b')
        
        block_syndrome = str(binary_string)[0:7]
        
        # Parities of B's measured bits (character -1-j = block-local qubit j):
        # the three Z-type stabilizers and the logical Z_L on qubits {0,1,4}.
        block_parity1 = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-3]) + int(block_syndrome[-4])
        ) % 2
        block_parity2 = (
            int(block_syndrome[-2]) + int(block_syndrome[-3])
            + int(block_syndrome[-5]) + int(block_syndrome[-6])
        ) % 2
        block_parity3 = (
            int(block_syndrome[-3]) + int(block_syndrome[-4])
            + int(block_syndrome[-6]) + int(block_syndrome[-7])
        ) % 2
        block_logical_op = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-5])
        ) % 2 
        
        parity_list = [
            block_parity1, block_parity2, block_parity3, block_logical_op
        ]

        # Accept only runs with trivial stabilizer and logical parity checks.
        # This is the encoded version of keeping outcome 0 in the physical protocol.
        if parity_list == [0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                # F = <ideal|rho|ideal>; rows are qubits 7-13, columns are qubits 0-6.
                # Little-endian reshape to (128, 128): summing |row . ideal*|^2
                # over rows gives <ideal|rho_A|ideal> without forming rho_A.
                fid = np.sum(np.abs(np.asarray(sv).reshape(128, 128) @ ideal_conj)**2)
                sumfid += fid
                sumfid2 += fid**2
                
    if accepted == 0:
        return 0.0, 0.0, 0

    return sumfid, sumfid2, accepted


# Logical MSD with ideal error correction in the end. Depolarizing noise added to only 2-qubit gates
# "2Q" case: noisy 'ry' (p1) plus two-qubit noise (p2) on every 'cx'.
def logical_msd_2q_errors(num_shots, p1, p2):
    circuit = QuantumCircuit(14, 7)

    # Prepare and encode the two logical input magic states (blocks A and B).
    for i in [0, 7]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)

    # Apply the logical two-qubit MSD circuit transversally: CX_L (A controls
    # B), then H_L on A.
    for i in range(7):
        circuit.cx(i, i + 7)
        circuit.h(i)
    
    # Build the noise model for this case (see the comment above the function).
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['ry'])
    noise_model.add_all_qubit_quantum_error(two_qubit_kraus_noise(p2), ['cx']) 
    
    # Measure block B (qubits 7-13) into clbits 0-6, then reset qubits 7-9 so
    # they can serve as syndrome ancillas for block A.
    circuit.measure([i for i in range(7,14)], [i for i in range(7)]) 
    circuit.reset([q for q in range(7,10)])
    
    # Final syndrome extraction and recovery on output block A, free of gate
    # noise (readout noise on ancillas 7-9 still applies when spam > 0).
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)

    ideal_syndrome_meas(circuit, 0, 7, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 0, x_syndrome, z_syndrome)
    
    # Save post-measurement statevectors conditioned on classical outcomes.
    # Result: {hex key of all classical bits: [one statevector per shot]}.
    circuit.append(
        SaveStatevector(num_qubits=14, label="state_post", conditional=True, pershot=True),
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
    
    # Average the fidelity of block A over accepted shots. trace_list is unused:
    # the fidelity is computed directly from each statevector below.
    trace_list = [i for i in range(7,14)]
    sumfid = 0
    sumfid2 = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        # The key encodes all 13 classical bits; B's measurement is clbits 0-6,
        # the low 7 bits. Mask them out so the syndrome registers of block A
        # (clbits 7-12) never enter the post-selection decision.
        binary_string = format(int(key, 16) & 0x7F, '07b')
        
        block_syndrome = str(binary_string)[0:7]
        
        # Parities of B's measured bits (character -1-j = block-local qubit j):
        # the three Z-type stabilizers and the logical Z_L on qubits {0,1,4}.
        block_parity1 = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-3]) + int(block_syndrome[-4])
        ) % 2
        block_parity2 = (
            int(block_syndrome[-2]) + int(block_syndrome[-3])
            + int(block_syndrome[-5]) + int(block_syndrome[-6])
        ) % 2
        block_parity3 = (
            int(block_syndrome[-3]) + int(block_syndrome[-4])
            + int(block_syndrome[-6]) + int(block_syndrome[-7])
        ) % 2
        block_logical_op = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-5])
        ) % 2 
        
        parity_list = [
            block_parity1, block_parity2, block_parity3, block_logical_op
        ]

        # Accept only runs with trivial stabilizer and logical parity checks.
        # This is the encoded version of keeping outcome 0 in the physical protocol.
        if parity_list == [0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                # F = <ideal|rho|ideal>; rows are qubits 7-13, columns are qubits 0-6.
                # Little-endian reshape to (128, 128): summing |row . ideal*|^2
                # over rows gives <ideal|rho_A|ideal> without forming rho_A.
                fid = np.sum(np.abs(np.asarray(sv).reshape(128, 128) @ ideal_conj)**2)
                sumfid += fid
                sumfid2 += fid**2
                
    if accepted == 0:
        return 0.0, 0.0, 0

    return sumfid, sumfid2, accepted


# Logical MSD with ideal error correction in the end. Depolarizing noise added to only 1-qubit gates 
# "1Q" case: noise p1 on 'ry' and on every 'h' gate.
def logical_msd_1q_errors(num_shots, p1):
    circuit = QuantumCircuit(14, 7)

    # Prepare and encode the two logical input magic states (blocks A and B).
    for i in [0, 7]:
        circuit.ry(theta, i)

    encoding(circuit, 0)
    encoding(circuit, 7)

    # Apply the logical two-qubit MSD circuit transversally: CX_L (A controls
    # B), then H_L on A.
    for i in range(7):
        circuit.cx(i, i + 7)
        circuit.h(i)
    
    # Build the noise model for this case (see the comment above the function).
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['h'])
    noise_model.add_all_qubit_quantum_error(one_qubit_kraus_noise(p1), ['ry'])
    
    # Measure block B (qubits 7-13) into clbits 0-6, then reset qubits 7-9 so
    # they can serve as syndrome ancillas for block A.
    circuit.measure([i for i in range(7,14)], [i for i in range(7)]) 
    circuit.reset([q for q in range(7,10)])
    
    # Final syndrome extraction and recovery on output block A, free of gate
    # noise (readout noise on ancillas 7-9 still applies when spam > 0).
    x_syndrome = ClassicalRegister(3)
    z_syndrome = ClassicalRegister(3)
    circuit.add_register(x_syndrome, z_syndrome)

    ideal_syndrome_meas(circuit, 0, 7, x_syndrome, z_syndrome)
    ideal_recovery(circuit, 0, x_syndrome, z_syndrome)
    
    # Save post-measurement statevectors conditioned on classical outcomes.
    # Result: {hex key of all classical bits: [one statevector per shot]}.
    circuit.append(
        SaveStatevector(num_qubits=14, label="state_post", conditional=True, pershot=True),
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
    
    # Average the fidelity of block A over accepted shots. trace_list is unused:
    # the fidelity is computed directly from each statevector below.
    trace_list = [i for i in range(7,14)]
    sumfid = 0
    sumfid2 = 0
    accepted = 0

    for key, sv_list in res_statevectors.items():
        # The key encodes all 13 classical bits; B's measurement is clbits 0-6,
        # the low 7 bits. Mask them out so the syndrome registers of block A
        # (clbits 7-12) never enter the post-selection decision.
        binary_string = format(int(key, 16) & 0x7F, '07b')
        
        block_syndrome = str(binary_string)[0:7]
        
        # Parities of B's measured bits (character -1-j = block-local qubit j):
        # the three Z-type stabilizers and the logical Z_L on qubits {0,1,4}.
        block_parity1 = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-3]) + int(block_syndrome[-4])
        ) % 2
        block_parity2 = (
            int(block_syndrome[-2]) + int(block_syndrome[-3])
            + int(block_syndrome[-5]) + int(block_syndrome[-6])
        ) % 2
        block_parity3 = (
            int(block_syndrome[-3]) + int(block_syndrome[-4])
            + int(block_syndrome[-6]) + int(block_syndrome[-7])
        ) % 2
        block_logical_op = (
            int(block_syndrome[-1]) + int(block_syndrome[-2])
            + int(block_syndrome[-5])
        ) % 2 
        
        parity_list = [
            block_parity1, block_parity2, block_parity3, block_logical_op
        ]

        # Accept only runs with trivial stabilizer and logical parity checks.
        # This is the encoded version of keeping outcome 0 in the physical protocol.
        if parity_list == [0, 0, 0, 0]:
            accepted += len(sv_list)

            for sv in sv_list:
                # F = <ideal|rho|ideal>; rows are qubits 7-13, columns are qubits 0-6.
                # Little-endian reshape to (128, 128): summing |row . ideal*|^2
                # over rows gives <ideal|rho_A|ideal> without forming rho_A.
                fid = np.sum(np.abs(np.asarray(sv).reshape(128, 128) @ ideal_conj)**2)
                sumfid += fid
                sumfid2 += fid**2
                
    if accepted == 0:
        return 0.0, 0.0, 0

    return sumfid, sumfid2, accepted