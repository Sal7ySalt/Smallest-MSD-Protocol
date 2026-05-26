# steane functions
from qiskit import QuantumCircuit
import numpy as np
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
from qiskit.visualization import plot_histogram 
import typing
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

from qiskit_aer import Aer
from qiskit import transpile
from qiskit_aer.primitives import Sampler
from qiskit.primitives.backend_sampler import BackendSampler
from qiskit.quantum_info import Statevector
from qiskit.circuit import Instruction
from matplotlib import pyplot as plt
from qiskit.quantum_info import state_fidelity, DensityMatrix

from qiskit.quantum_info import Pauli
from qiskit_aer.noise import pauli_error 

import matplotlib.pyplot as plt
import pandas as pd
from lmfit import Model
from pandas import DataFrame

no_noise = NoiseModel()
theta = np.arctan(np.sqrt((np.sqrt(5) - 1) / 2))
amp_0_theta = np.cos(theta/2)
amp_1_theta = np.sin(theta/2)


def steane_enc_8(amp_0: float, amp_1: float, is_ideal: bool):


    if is_ideal == True:
        steane_enc_block = QuantumCircuit(8, 8, name="steane_block")
    else:
        steane_enc_block = QuantumCircuit(8, name="steane_block_noise")


    steane_enc_block.h(0)
    steane_enc_block.h(4)
    steane_enc_block.h(6)

    #steane_enc_block.initialize([amp_0, amp_1], 6)
    steane_enc_block.initialize([amp_0, amp_1], 6)

    steane_enc_block.barrier()

    steane_enc_block.cx(0, 1)
    steane_enc_block.cx(4, 5)
    steane_enc_block.cx(6, 3)

    steane_enc_block.cx(4,2)
    steane_enc_block.cx(6,5)

    steane_enc_block.cx(0,3)
    steane_enc_block.cx(4,1)

    steane_enc_block.cx(3,2)

    steane_enc_block.cx(1,7)
    steane_enc_block.cx(3,7)
    steane_enc_block.cx(5,7)

    steane_enc_block.barrier()

    for i in range(0, 8):
        steane_enc_block.h(i)
        #steane_enc_block.measure(i,0)
    steane_enc_block.barrier()
    # steane_enc_block.measure(7,0)


    #print(steane_enc_block)

    return steane_enc_block

def steane_enc_7(amp_0: float, amp_1: float, is_ideal: bool):


    if is_ideal == True:
        steane_enc_block = QuantumCircuit(7, 7, name="steane_block")
    else:
        steane_enc_block = QuantumCircuit(7, name="steane_block_noise")

    for i in range(1,4):
        steane_enc_block.h(i)
    
    steane_enc_block.h(6)
    steane_enc_block.initialize([amp_0, amp_1], 6)

    steane_enc_block.barrier()

    steane_enc_block.cx(1,0)
    steane_enc_block.cx(2,4)
    steane_enc_block.cx(6,5)

    steane_enc_block.cx(2,0)
    steane_enc_block.cx(3,5)
    steane_enc_block.cx(6,4)
    steane_enc_block.cx(2,6)
    steane_enc_block.cx(3,4)
    steane_enc_block.cx(1,5)
    steane_enc_block.cx(1,6)
    steane_enc_block.cx(3,0)
    
    steane_enc_block.barrier()

    # switch to measuring in other basis
    for i in range(0, 7):
        steane_enc_block.h(i)

    #print(steane_enc_block)
    return steane_enc_block


def create_h_block(num: int, is_ideal: bool):
    if (is_ideal == 1):
        h_block = QuantumCircuit(num, num, name="h_block")
    else:
        h_block = QuantumCircuit(num, name="h_block_noise")

    for i in range(0, num):
        h_block.h(i)

    # convert to instruction
    h_block_instr = h_block.to_instruction()
    return h_block_instr

# applies cz to n qubits
def create_cz_block(num: int, is_ideal: bool):
    if (is_ideal == 1):
        cz_block = QuantumCircuit(num*2, num*2, name="cz_block")
    else:
        cz_block = QuantumCircuit(num*2, name="cz_block_noise")
    
    for i in range(0, num):
        cz_block.cz(i, i + num)
        print(num)

    # convert to instruction
    cz_block_instr = cz_block.to_instruction()
    return cz_block_instr


# applies identity 
def create_id_block(num: int, is_ideal: bool):

    if (is_ideal == 1):
        id_block = QuantumCircuit(num, num, name = "id_block")
    else:
        id_block = QuantumCircuit(num, name = "id_block")
    

    for i in range(0, num):
        id_block.id(i)

    id_block_instr = id_block.to_instruction()
    return id_block_instr


# applies x 
def create_x_block(num: int, is_ideal: bool):
    if (is_ideal == 1):
        x_block = QuantumCircuit(num, num, name = "x_block")
    else:
        x_block = QuantumCircuit(num, name = "x_block")
    

    for i in range(0, num):
        x_block.x(i)

    x_block_instr = x_block.to_instruction()
    return x_block_instr

def prepare_state(qc_prep: QuantumCircuit, encode_block: Instruction, log_block: Instruction, num: int, is_ideal: bool):

    if (is_ideal == 1):
        qc_prep.append(create_id_block(num, is_ideal), range(0,num), range(0,num))
        qc_prep.append(encode_block, range(0,num), range(0,num))
        qc_prep.append(create_id_block(num, is_ideal), range(0,num), range(0,num))
        qc_prep.append(log_block,range(0,num), range(0,num))
        qc_prep.draw('mpl')
    else:
        qc_prep.append(create_id_block(num, is_ideal), range(0,num))
        qc_prep.append(encode_block, range(0,num))
        qc_prep.append(create_id_block(num, is_ideal), range(0,num))
        qc_prep.append(log_block,range(0,num))
        qc_prep.draw('mpl')


def preparation_results_2(num: int, is_ideal: bool, is_counts:bool, encoding: Instruction, noise_model: NoiseModel, shots = 1000):


    qc = QuantumCircuit(num,num)

    state = []
    counts = []

  
    prepare_state(qc, encoding, create_id_block(num, is_ideal), num, is_ideal)

    if (is_counts == True):
        for j in range(0,7):
            qc.measure(j,j)


    if is_counts == False:
        if is_ideal == True:
            simulator = Aer.get_backend('statevector_simulator')
            steane_t = transpile(qc, simulator)
            job = simulator.run(steane_t, shots=shots)
            result = job.result()
            # counts = result.get_counts()
            state = result.get_statevector()
            
            # counts_arr.append(counts)
        else:
            # for j in range(0,7):
            #     qc_arr[i].measure(j,j)
            qc.save_statevector(label='state_post', pershot=True, conditional=True)
            backend = AerSimulator(noise_model=noise_model)
            transpiled = transpile(qc, backend)
            job = backend.run(transpiled, shots=shots)
            result = job.result()
            # state = result.get_statevector()
            # state_arr.append(state)
            state = result.data()['state_post']
            #print(state)
            for shot in state['0x0']:
                state = shot.data
    else:
        backend = AerSimulator(noise_model=noise_model)
        transpiled = transpile(qc, backend)
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        

    return [qc, state, counts]


def preparation_results_2(num: int, is_ideal: bool, is_counts:bool, encoding: Instruction, noise_model: NoiseModel, shots = 1000):


    qc = QuantumCircuit(num,num)

    state = []
    counts = []

  
    prepare_state(qc, encoding, create_id_block(num, is_ideal), num, is_ideal)

    if (is_counts == True):
        for j in range(0,7):
            qc.measure(j,j)


    if is_counts == False:
        if is_ideal == True:
            simulator = Aer.get_backend('statevector_simulator')
            steane_t = transpile(qc, simulator)
            job = simulator.run(steane_t, shots=shots)
            result = job.result()
            # counts = result.get_counts()
            state = result.get_statevector()
            
            # counts_arr.append(counts)
        else:
            # for j in range(0,7):
            #     qc_arr[i].measure(j,j)
            qc.save_statevector(label='state_post', pershot=True, conditional=True)
            backend = AerSimulator(noise_model=noise_model)
            transpiled = transpile(qc, backend)
            job = backend.run(transpiled, shots=shots)
            result = job.result()
            # state = result.get_statevector()
            # state_arr.append(state)
            state = result.data()['state_post']
            # print(state)
            for shot in state['0x0']:
                state = shot.data
    else:
        backend = AerSimulator(noise_model=noise_model)
        transpiled = transpile(qc, backend)
        job = backend.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()

    
    return [qc, state, counts]




            

def direct_fid_results(noise_model: NoiseModel, shots = 1000, amp_0 = amp_0_theta, amp_1 = amp_1_theta):

    state = []
    counts = []

    ideal = True
    noisy = False

    num = 7

    ### ideal circuit #####
    qc = QuantumCircuit(num,num)

    
    steane_intr_theta_ideal_7 = steane_enc_7(amp_0_theta, amp_1_theta, True).to_instruction()
    steane_intr_theta_n_7 = steane_enc_7(amp_0_theta, amp_1_theta, False).to_instruction()


    prepare_state(qc, steane_intr_theta_ideal_7, create_id_block(num,ideal), num, ideal)


    simulator = Aer.get_backend('statevector_simulator')
    steane_t = transpile(qc, simulator)
    job = simulator.run(steane_t, shots=shots)
    result = job.result()
    # counts = result.get_counts()
    state_ideal = result.get_statevector()
    sv_ideal = Statevector(state_ideal)

    #print("state_ideal", state_ideal)

    ################# noisy circuit #####

    qc = QuantumCircuit(num,num)

    prepare_state(qc, steane_intr_theta_n_7, create_id_block(num, noisy), num, noisy)

    qc.save_statevector(label='state_post', pershot=True, conditional=True)
    backend = AerSimulator(noise_model=noise_model)
    transpiled = transpile(qc, backend)
    job = backend.run(transpiled, shots=shots)
    result = job.result()
    
    state_noisy = result.data()['state_post']

    #print("state_noisy", state_noisy)
    
    fid_list = []
    for shot in state_noisy['0x0']:
        comp_state = shot.data
        comp_sv = Statevector(comp_state)
        fid = state_fidelity(sv_ideal, comp_sv)
        fid_list.append(fid)
        
    
        

    return fid_list

def fidelity_sweep(noise_list: list, error_list, err_size: int, shots=1000):
    error_to_fidelity_dict = {}
    for error_index in range(err_size):
        fid_list = direct_fid_results(noise_list[error_index], shots = shots)
        mean_fidelity = np.mean(fid_list)
        error_to_fidelity_dict.update({error_list[error_index]: mean_fidelity})
    
    return error_to_fidelity_dict
    
def get_sample_error_rate(fidelity, shots = 1000):
    sample_err_rate = []
    for fid in fidelity:
        # print(fid)
        sample_err_rate.append((fid)*(1 - fid) / shots)
    
    return sample_err_rate
    

    

    


        






