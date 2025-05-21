# Welcome to the steane encoding module! 

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
from qiskit.quantum_info import state_fidelity

class SteaneBlock(QuantumCircuit):
    def __init__(self, q_num, c_num, is_ideal):
        qreg = QuantumRegister(q_num, name='q')
        creg = ClassicalRegister(c_num, name='c')
        super().__init__(qreg, creg)
        self.is_ideal = is_ideal
    

class SteaneEnc(SteaneBlock):
    def __init__(steane_enc_block, amp_0, amp_1, q_num, is_ideal, is_counts):

        if (q_num != 7)  or  (q_num != 8):
            raise ValueError("SteaneEnc Qubit Number must be 7 or 8")
        
        if is_ideal == True:
            steane_enc_block = QuantumCircuit(q_num, q_num, name="steane_block")
        else:
            steane_enc_block = QuantumCircuit(q_num, name="steane_block_noise")

        if q_num == 8:
            
            steane_enc_block.h(0)
            steane_enc_block.h(4)
            steane_enc_block.h(6)

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
            steane_enc_block.barrier()

        elif q_num == 7:

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
            
        return steane_enc_block
    
    def convert_SteaneEnc_instr(steane_enc_block):
        steane_to_instr = steane_enc_block.to_instruction()
        return steane_to_instr
    
    def prepare_state(steane_enc_block, qc_prep: QuantumCircuit,  log_block: Instruction, num: int, is_ideal: bool):
        
        encode_block = SteaneEnc.convert_SteaneEnc_instr(steane_enc_block)

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

    def preparation_results(steane_enc_block, qc_arr: list, q_num: int,  is_ideal: bool, is_counts:bool,  noise_model: NoiseModel, prep_num = 3):



        # if is_ideal == True:
        qca = QuantumCircuit(q_num, q_num)
        qcb = QuantumCircuit(q_num, q_num)
        qcc = QuantumCircuit(q_num, q_num)
        # else:
        #     qca = QuantumCircuit(num)
        #     qcb = QuantumCircuit(num)
        #     qcc = QuantumCircuit(num)




        qc_arr = [qca, qcb, qcc]



        state_arr = []
        counts_arr = []

        

        
        for i in range(0,prep_num): 

            SteaneEnc.prepare_state(steane_enc_block, qc_arr[i], create_id_block(q_num, is_ideal), q_num, is_ideal)

            if (is_counts == True):
                for j in range(0,7):
                    qc_arr[i].measure(j,j)


            if is_counts == False:
                if is_ideal == True:
                    simulator = Aer.get_backend('statevector_simulator')
                    steane_t = transpile(qc_arr[i], simulator)
                    job = simulator.run(steane_t, shots = 1000)
                    result = job.result()
                    # counts = result.get_counts()
                    state = result.get_statevector()
                    state_arr.append(state)
                    # counts_arr.append(counts)
                else:
                    # for j in range(0,7):
                    #     qc_arr[i].measure(j,j)
                    qc_arr[i].save_statevector(label='state_post', pershot=True, conditional=True)
                    backend = AerSimulator(noise_model=noise_model)
                    transpiled = transpile(qc_arr[i], backend)
                    job = backend.run(transpiled, shots=1000)
                    result = job.result()
                    # state = result.get_statevector()
                    # state_arr.append(state)
                    state = result.data()['state_post']
                    #print(state)
                    for shot in state['0x0']:
                        state_arr.append(shot.data)
            else:
                backend = AerSimulator(noise_model=noise_model)
                transpiled = transpile(qc_arr[i], backend)
                job = backend.run(transpiled, shots = 1000)
                result = job.result()
                counts_n = result.get_counts()
                counts_arr.append(counts_n)

        return [qc_arr, state_arr, counts_arr]





### Helper functions

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
    
# applies identity to 7 qubits
def create_id_block(num: int, is_ideal: bool):

    if (is_ideal == 1):
        id_block = QuantumCircuit(num, num, name = "id_block")
    else:
        id_block = QuantumCircuit(num, name = "id_block")
    

    for i in range(0, num):
        id_block.id(i)

    id_block_instr = id_block.to_instruction()
    return id_block_instr
                    

                 # applies x to 7 qubits
def create_x_block(num: int, is_ideal: bool):
    if (is_ideal == 1):
        x_block = QuantumCircuit(num, num, name = "x_block")
    else:
        x_block = QuantumCircuit(num, name = "x_block")
    

    for i in range(0, num):
        x_block.x(i)

    x_block_instr = x_block.to_instruction()
    return x_block_instr       
