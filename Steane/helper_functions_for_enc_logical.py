## helper functions for encoding_logical_error_rate

# general imports
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info import Statevector, state_fidelity, Pauli, DensityMatrix
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
from qiskit import transpile 
import numpy as np
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError, pauli_error 
from qiskit.circuit.library import HGate, UnitaryGate, CXGate
import matplotlib.pyplot as plt

# our imports
from steane_ec_decoder import bool_syndrome_flag, syndrome

# 
def get_noise_list(noise_sweep_type: str, error_list, error_list_size , factor = 10):
    noise_list = []
    if noise_sweep_type == "depolarizing":
        for error in error_list:
            # readout_err = ReadoutError([[0.98, 0.02],  # P(measured 0 | actual 0), P(1 | 0)
            #                             [0.02, 0.98]]) # P(0 | 1), P(1 | 1)

            noise_model = NoiseModel()

            error2 = error*factor

            noise_model.add_all_qubit_quantum_error(depolarizing_error(error,1), ['id'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(error,1), ['h'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(error2,2),['cz'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(error2,2),['cx'])

            readout_err = ReadoutError([[1-error2, error2],  # P(measured 0 | actual 0), P(1 | 0)
                                    [error2, 1-error2]]) # P(0 | 1), P(1 | 1)
            
            
            noise_model.add_readout_error(readout_err, [7])
            noise_model.add_readout_error(readout_err, [8])
            
            noise_list.append(noise_model)
    elif noise_sweep_type == "pauli":
        for p in error_list:
            # New noise model for each
            noise_model = NoiseModel()
            
            # Assign 1q and 2q Pauli errors
            noise_1q = [
                (Pauli('I'),    1-p), 
                (Pauli('X'),    2*p/5),
                (Pauli('Y'),    p/5),
                (Pauli('Z'),    2*p/5),
            ]
            
            two_qubit_paulis = []
            for P1 in ['I','X','Y','Z']:
                for P2 in ['I','X','Y','Z']:
                    two_qubit_paulis.append((Pauli(P1+P2), None))

            p2 = factor*p
            noise_2q = []
            for pauli, _ in two_qubit_paulis:
                if pauli.to_label() == 'II':
                    prob = 1 - p2
                else:
                    prob = p2/15
                noise_2q.append((pauli, prob))
            

            # Apply depolarizing error with probability p
            noise_model.add_all_qubit_quantum_error(pauli_error(noise_1q), ['id'])
            noise_model.add_all_qubit_quantum_error(pauli_error(noise_1q), ['h'])
            noise_model.add_all_qubit_quantum_error(pauli_error(noise_2q), ['cz']) 
            noise_model.add_all_qubit_quantum_error(pauli_error(noise_2q), ['cx']) 

            # Readout error 
            readout_err = ReadoutError([[1-p2, p2],  
                                    [p2, 1-p2]]) 
            noise_model.add_readout_error(readout_err, [7])
            noise_model.add_readout_error(readout_err, [8])
                
            
            noise_list.append(noise_model)
    elif noise_sweep_type == "readout":
        for error in error_list:
            # readout_err = ReadoutError([[0.98, 0.02],  # P(measured 0 | actual 0), P(1 | 0)
            #                             [0.02, 0.98]]) # P(0 | 1), P(1 | 1)

            noise_model = NoiseModel()

            error2 = error*factor

            noise_model.add_all_qubit_quantum_error(depolarizing_error(0.005,1), ['id'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(0.005,1), ['h'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(0.05,2),['cz'])
            noise_model.add_all_qubit_quantum_error(depolarizing_error(0.05,2),['cx'])

            readout_err = ReadoutError([[1-error2, error2],  # P(measured 0 | actual 0), P(1 | 0)
                                    [error2, 1-error2]]) # P(0 | 1), P(1 | 1)
            
            
            noise_model.add_readout_error(readout_err, [7])
            noise_model.add_readout_error(readout_err, [8])
            
            noise_list.append(noise_model)
    else:
        raise ValueError("noise_sweep_type must be one of 'depolarizing', 'pauli', or 'readout'")



def get_logical_error_circ():


    theta = np.arctan(np.sqrt((np.sqrt(5) - 1) / 2))
    amp_0 = np.cos(theta/2)
    amp_1 = np.sin(theta/2)

    logical_error_circ = QuantumCircuit(29, 22)
    # First 7 qubits are data qubits
    # Next 6 qubits are for syndrome extraction with flag
    # Next 16 qubits are for syndrome extractino without flag

    logical_error_circ.initialize([amp_0, amp_1], 0)

    for i in range(7):
        logical_error_circ.id(i)

    for i in range(4, 7):
        logical_error_circ.h(i)

    logical_error_circ.cx(0, 1)
    logical_error_circ.cx(0, 2)
    logical_error_circ.cx(6, 0)
    logical_error_circ.cx(6, 1)
    logical_error_circ.cx(6, 3)
    logical_error_circ.cx(5, 0)
    logical_error_circ.cx(5, 2)
    logical_error_circ.cx(5, 3)
    logical_error_circ.cx(4, 1)
    logical_error_circ.cx(4, 2)
    logical_error_circ.cx(4, 3)

    return logical_error_circ

def get_meas_circuit_noise():

    logical_error_circ = get_logical_error_circ()

    meas_circuit_noise = logical_error_circ.copy()
    meas_circuit_noise.barrier()
    # Syndrome measurement using flag
    for i in range(4, 7):
        meas_circuit_noise.h(i)
    meas_circuit_noise.cx(0, 1)
    meas_circuit_noise.cx(0, 2)
    meas_circuit_noise.cx(6, 0)
    meas_circuit_noise.cx(6, 1)
    meas_circuit_noise.cx(6, 3)
    meas_circuit_noise.cx(5, 0)
    meas_circuit_noise.cx(5, 2)
    meas_circuit_noise.cx(5, 3)
    meas_circuit_noise.cx(4, 1)
    meas_circuit_noise.cx(4, 2)
    meas_circuit_noise.cx(4, 3)
    meas_circuit_noise.barrier()

    # Encoding next 6 qubits and applying CNOTs and measurements, 7-12
    meas_circuit_noise.h(7)
    meas_circuit_noise.h(11)
    meas_circuit_noise.h(12)
    meas_circuit_noise.cx(7, 4)
    meas_circuit_noise.cx(6, 8)
    meas_circuit_noise.cx(5, 9)
    meas_circuit_noise.cx(7, 9)
    meas_circuit_noise.cx(7, 0)
    meas_circuit_noise.cx(4, 8)
    meas_circuit_noise.cx(1, 9)
    meas_circuit_noise.cx(7, 2)
    meas_circuit_noise.cx(3, 8)
    meas_circuit_noise.cx(6, 9)
    meas_circuit_noise.cx(7, 8)
    meas_circuit_noise.cx(7, 6)
    meas_circuit_noise.cx(5, 8)
    meas_circuit_noise.cx(2, 9)
    meas_circuit_noise.cx(4, 10)
    meas_circuit_noise.cx(11, 6)
    meas_circuit_noise.cx(12, 5)
    meas_circuit_noise.cx(12, 10)
    meas_circuit_noise.cx(0, 10)
    meas_circuit_noise.cx(11, 4)
    meas_circuit_noise.cx(12, 1)
    meas_circuit_noise.cx(2, 10)
    meas_circuit_noise.cx(11, 3)
    meas_circuit_noise.cx(12, 6)
    meas_circuit_noise.cx(11, 10)
    meas_circuit_noise.cx(6, 10)
    meas_circuit_noise.cx(11, 5)
    meas_circuit_noise.cx(12, 2)

    meas_circuit_noise.h(7)
    meas_circuit_noise.h(11)
    meas_circuit_noise.h(12)
    for i in range(6):
        meas_circuit_noise.measure([i+7], [i])
        
    #############################################

    # Encoding next 8 qubits, 13-20
    meas_circuit_noise.h(13)
    meas_circuit_noise.h(14)
    meas_circuit_noise.h(16)
    meas_circuit_noise.cx(13, 17)
    meas_circuit_noise.cx(14, 15)
    meas_circuit_noise.cx(16, 18)
    meas_circuit_noise.cx(13, 19)
    meas_circuit_noise.cx(16, 17)
    meas_circuit_noise.cx(14, 18)
    meas_circuit_noise.cx(13, 15)
    meas_circuit_noise.cx(18, 19)
    meas_circuit_noise.cx(17, 20)
    meas_circuit_noise.cx(15, 20)
    meas_circuit_noise.cx(18, 20)
    meas_circuit_noise.measure([20], [6]) # Post-select for 0
    for i in range(13, 20):
        meas_circuit_noise.h(i)
    meas_circuit_noise.barrier()

    # Encoding last 8 qubits, 21-28
    meas_circuit_noise.h(21)
    meas_circuit_noise.h(22)
    meas_circuit_noise.h(24)
    meas_circuit_noise.cx(21, 25)
    meas_circuit_noise.cx(22, 23)
    meas_circuit_noise.cx(24, 26)
    meas_circuit_noise.cx(21, 27)
    meas_circuit_noise.cx(24, 25)
    meas_circuit_noise.cx(22, 26)
    meas_circuit_noise.cx(21, 23)
    meas_circuit_noise.cx(26, 27)
    meas_circuit_noise.cx(25, 28)
    meas_circuit_noise.cx(23, 28)
    meas_circuit_noise.cx(26, 28)
    meas_circuit_noise.measure([28], [7]) # Post-select for 0
    meas_circuit_noise.barrier()
        
    # Transversal CNOTs from data qubits to next 7 qubits and measure syndrome
    for i in range(7):
        meas_circuit_noise.cx(i, i+13)
    for i in range(7):
        meas_circuit_noise.measure([i+13], [i+8])
    meas_circuit_noise.barrier()

    # Transversal CNOTs from last 7 qubits to data qubits and measure syndrome
    for i in range(7):
        meas_circuit_noise.cx(i+21, i)
    for i in range(21, 28):
        meas_circuit_noise.h(i)
    for i in range(7):
        meas_circuit_noise.measure([i+21], [i+15])

    return meas_circuit_noise
