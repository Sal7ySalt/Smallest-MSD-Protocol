"""Shared hardware constants and helpers for the 2-qubit protocol.

Not imported by any notebook or script: the notebooks define the same numbers
inline. Kept as a single reference for the values used throughout.
"""
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister 
from qiskit_aer import AerSimulator

# Target magic state of the 2-qubit protocol: |psi_star> = RY(theta_star)|0>, with
# Bloch vector (x_star, 0, z_star) ~ (0.8393, 0, 0.5437). z_star is the real
# root of z^3 + z^2 + z = 1, and the state is the nontrivial fixed point of the
# [[2,1,1]] Bloch map (x, z) -> (2z, x^2) / (1 + z^2).
x_star = 1/3 * (-2 + np.cbrt(19-3*np.sqrt(33)) + np.cbrt(19+3*np.sqrt(33)))
z_star = np.sqrt(1 - x_star**2)
theta_star = np.arcsin(x_star)

# Quantinuum H2-2 operation infidelities (inf_to_error treats them as average infidelities).
# The notebooks sweep 1x..5x these values. spam0 = P(read 1 | prepared 0),
# spam1 = P(read 0 | prepared 1).
one_q = 2.8e-5
two_q = 8.3e-4
idle = 1.2e-4
spam0 = 6.7e-4
spam1 = 1.2e-3

# Infidelity to physical error rates using depolarizing noise 
# Converts an average infidelity r on d = 2^n levels into the parameter lambda
# of Qiskit's depolarizing_error, E(rho) = (1 - lambda) rho + lambda I/d, using
# r = lambda (d - 1)/d. The notebooks use the same conversion with n = 1 to
# report output "error rates": for one qubit, error rate = 2 * infidelity.
def inf_to_error(infidelity_list, num_qubits):
    error_rates_list = []
    dimension = 2**num_qubits
    for infidelity in infidelity_list:
        error_rates_list.append( infidelity * (dimension / (dimension - 1)) )
    
    return error_rates_list



# Steane code unitary encoding circuit
# Same encoder as encoding() in logical_depolarizing.py: block-local qubit 0
# carries the input state; qubits start..start+6 hold the [[7,1,3]] block.
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

