import numpy as np
from qiskit import QuantumCircuit, QuantumRegister 
from qiskit_aer import AerSimulator

# Global variables
x_star = 1/3 * (-2 + np.cbrt(19-3*np.sqrt(33)) + np.cbrt(19+3*np.sqrt(33)))
z_star = np.sqrt(1 - x_star**2)
theta_star = np.arcsin(x_star)

# Quantinuum's H2-2 operation infidelities
one_q = 2.8e-5
two_q = 8.3e-4
idle = 1.2e-4
spam0 = 6.7e-4
spam1 = 1.2e-3

# Infidelity to physical error rates using depolarizing noise 
def inf_to_error(infidelity_list, num_qubits):
    error_rates_list = []
    dimension = 2**num_qubits
    for infidelity in infidelity_list:
        error_rates_list.append( infidelity * (dimension / (dimension - 1)) )
    
    return error_rates_list



# Steane code unitary encoding circuit
def steane_encoding(qc: QuantumCircuit, start: int):
    # Encode one logical qubit into a 7-qubit Steane block.
    for i in [2, 3, 5]:
        qc.h(start + i)
    
    cx_list = [[0, 4], [0, 1], [2, 6], [2, 4], [2, 0], [5, 6], [5, 1], [5, 0], [3, 6], [3, 1], [3, 4]]

    for cx in cx_list:
        cx[0] += start
        cx[1] += start
        qc.cx(cx[0], cx[1])
        



# Input vs. output infidelity

