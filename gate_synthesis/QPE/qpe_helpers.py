from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import RZGate, UnitaryGate
import numpy as np
import time
import sys
from pathlib import Path

helpers_dir = Path("../").resolve()
sys.path.append(str(helpers_dir))

import importlib
import helpers
importlib.reload(helpers)
from helpers import key_from_U


# Defining global variables
theta = np.arctan(np.sqrt((np.sqrt(5) - 1) / 2))
x_star = 1/3 * (-2 + np.cbrt(19-3*np.sqrt(33)) + np.cbrt(19+3*np.sqrt(33)))
theta_star = np.arcsin(x_star)
h1 = 0.79605
h2 = -0.18092
h3 = -0.32096
t = np.pi/(8*h1)
alpha0 = 0
alpha1 = 0
kmax = 12 
tilde_phi_list = np.linspace(0, 2 * np.pi, 20_000, endpoint=False)


# Mappings
id_to_gate = {
    0: 'X',
    1: 'Y',
    2: 'Z',
    3: 'H',
    4: 'S',
    5: 'Sdg',
    6: 'Rz(-1*π/4)',
    7: 'Rz(1*π/4)',
    8: 'EMS',
    9: 'I',
    10: 'EMS1'
}

name_to_gate = {
    'I': np.array([[1,0],[0,1]]),
    'X': np.array([[0,1],[1,0]]),
    'Y': np.array([[0,-1j],[1j,0]]), 
    'Z': np.array([[1,0],[0,-1]]),
    'H': 1/np.sqrt(2) * np.array([[1,1],[1,-1]]),
    'S': np.array([[1,0],[0,1j]]),
    'Sdg': np.array([[1,0],[0,1j]]).conj().T,
    'Rz(1*π/4)': np.array([[1,0],[0,np.exp(1j*np.pi/4)]]),
    'Rz(-1*π/4)': np.array([[1,0],[0,np.exp(1j*np.pi/4)]]).conj().T,
    'EMS': np.array([[np.cos(theta/2),-np.sin(theta/2)],[np.sin(theta/2),np.cos(theta/2)]]),
    'EMS1': np.array([[np.cos(theta_star/2),-np.sin(theta_star/2)],[np.sin(theta_star/2),np.cos(theta_star/2)]])
}


def find_approximation(nn, unitary):
    euclidean_dist, idxs = nn.kneighbors(np.array(key_from_U(unitary), dtype=float).reshape(1, -1), 1, return_distance=True)
    return euclidean_dist, idxs

def create_approx_gate(unitary, nn, base_gate_set):
    temp = np.eye(2)
    euclidean_dist, idxs = find_approximation(nn, unitary)
    idx = int(idxs[0, 0])
    approx_unitary_list = base_gate_set.reconstruct_seq_names(idx, id_to_gate)
    for name in approx_unitary_list:
        temp = name_to_gate[name] @ temp
        
    return temp

def approx_cu(base_gate_set, nn):
    approx_gate_list = []
    # Approximating Rz(h1*t)
    unitary1 = np.asarray(RZGate(h1*t).to_matrix(), dtype=complex)
    temp1 = create_approx_gate(unitary1, nn, base_gate_set)
    gate1 = UnitaryGate(temp1, label="gate1")
    approx_gate_list.append(gate1)

    # Approximating Rz(-h1*t)
    temp2 = temp1.conj().T
    gate2 = UnitaryGate(temp2, label="gate2")
    approx_gate_list.append(gate2)

    # Approximating Rz(h2*t)
    unitary3 = np.asarray(RZGate(h2*t).to_matrix(), dtype=complex)
    temp3 = create_approx_gate(unitary3, nn, base_gate_set)
    gate3 = UnitaryGate(temp3, label="gate3")
    approx_gate_list.append(gate3)

    # Approximating Rz(-h2*t)
    temp4 = temp3.conj().T
    gate4 = UnitaryGate(temp4, label="gate4")
    approx_gate_list.append(gate4)

    return approx_gate_list

# Approximating Rz(beta)
def approx_rz_beta_dict(beta_values, base_gate_set, nn):
    beta_gate_dict = {}

    for i, beta in enumerate(beta_values):
        U_exact = np.asarray(RZGate(beta).to_matrix(), dtype=complex)
        U_approx = create_approx_gate(U_exact, nn, base_gate_set)

        key = round(float(beta), 12)
    
        gate = UnitaryGate(U_approx, label=f"Rz({beta:.3f})")

        beta_gate_dict[key] = gate

    return beta_gate_dict


def distance(U, V):
    # U and V are 2x2 complex matrices
    if np.allclose(U, V):
        return 0.0
    else:
        overlap = 0.5 * np.trace(U.conj().T @ V)
        return np.sqrt((1 - abs(overlap)) + 0j).real
    
def state_prep(qc):
    qc.h(0)
    qc.x(1)
    qc.ry(alpha0, 1)
    qc.rz(alpha1, 1)
    
def control_uk(qc, cu_gate_list):
    qc.append(cu_gate_list[0], [1])
    qc.cx(0,1)
    qc.append(cu_gate_list[1], [1])
    qc.cx(0,1)
    qc.h(1)
    qc.append(cu_gate_list[2], [1])
    qc.cx(0,1)
    qc.append(cu_gate_list[3], [1])
    qc.cx(0,1)
    qc.h(1)
    
def qpe(qc, k, beta, cu_gate_list, beta_gate_dict):
    state_prep(qc)

    for _ in range(k):
        control_uk(qc, cu_gate_list)

    beta_key = round(float(beta), 12)
    qc.append(beta_gate_dict[beta_key], [0])

    qc.h(0)
    qc.measure([0], [0])
    
def calculate_Q(k_list, beta_list, m_list, tilde_phi, eps=1e-15):
    k_array = np.asarray(k_list, dtype=float)
    beta_array = np.asarray(beta_list, dtype=float)
    m_array = np.asarray(m_list, dtype=float)

    probs = (1 + np.cos(k_array * tilde_phi + beta_array - m_array * np.pi)) / 2
    probs = np.clip(probs, eps, 1.0)

    return np.sum(np.log(probs))

def estimate_phase(k_list, beta_list, m_list):
    Q_list = np.array([
        calculate_Q(k_list, beta_list, m_list, tilde_phi)
        for tilde_phi in tilde_phi_list
    ])

    max_idx = np.argmax(Q_list)
    return tilde_phi_list[max_idx]

# Returns [-pi, pi)
def circular_mean0(phi_list):
    phi_array = np.asarray(phi_list, dtype=float)

    mean_complex = np.mean(np.exp(1j * phi_array))
    phi_avg = np.angle(mean_complex)

    R_bar = np.abs(mean_complex)

    if np.isclose(R_bar, 0.0):
        holevo_variance = np.inf
        holevo_std = np.inf
    else:
        holevo_variance = 1 / (R_bar**2) - 1
        holevo_std = np.sqrt(holevo_variance)

    return phi_avg, holevo_variance, holevo_std

# Returns [0, 2*pi)
def circular_mean1(phi_list):
    phi_avg, holevo_variance, holevo_std = circular_mean0(phi_list)

    phi_avg = phi_avg % (2 * np.pi)

    return phi_avg, holevo_variance, holevo_std


# The algorithm
def algorithm(base_gate_set, nn, N_s, R):
    rng = np.random.default_rng(seed=time.time_ns())

    original_k_list = rng.integers(1, kmax + 1, size=N_s)
    original_beta_list = rng.choice([0.0, np.pi / 2], size=N_s)

    cu_gate_list = approx_cu(base_gate_set, nn)
    beta_gate_dict = approx_rz_beta_dict(
        [0.0, np.pi / 2],
        base_gate_set,
        nn
    )

    backend = AerSimulator()

    original_m_list = []

    for i in range(N_s):
        qc = QuantumCircuit(2, 1)
        qpe(qc, original_k_list[i], original_beta_list[i], cu_gate_list, beta_gate_dict)

        job = backend.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()

        measured_bit = int(next(iter(counts.keys())))
        original_m_list.append(measured_bit)

    original_m_list = np.asarray(original_m_list)

    phi_list = []
    for _ in range(R):
        indices = rng.choice(N_s, size=N_s, replace=True)

        k_list = original_k_list[indices]
        beta_list = original_beta_list[indices]
        m_list = original_m_list[indices]

        phi_est = estimate_phase(k_list, beta_list, m_list)
        phi_list.append(phi_est)

    estimated_phase, holevo_variance, holevo_std = circular_mean0(phi_list)
    
    return estimated_phase, holevo_variance, holevo_std, original_k_list, original_beta_list, original_m_list, tilde_phi_list, cu_gate_list, beta_gate_dict