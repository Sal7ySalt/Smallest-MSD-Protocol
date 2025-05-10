# 1 input list, length 7 (each qubit)
# We only measure in the X-basis, so can only correct Z-errors

def main():
    syndrome = list(map(int, input("Input Syndrome: ").split()))
    if len(syndrome) != 7:
        print("Invalid Syndrome")
        return 1
    
    for i in range(len(syndrome)):
        if abs(syndrome[i]) != 1:
            print("Invalid Syndrome")
            return 1
        
    # Calculating the parity of each plaquette
    # 1st plaquette target qubits: 0, 1, 2, 3 
    # 2nd plaquette target qubits: 1, 2, 4, 5 
    # 3rd plaquette target qubits: 2, 3, 5, 6 
    
    parity1 = 1 
    for i in range(4):
        parity1 *= syndrome[i]

    parity2 = 1
    for i in [1, 2, 4, 5]:
        parity2 *= syndrome[i]
        
    parity3 = 1 
    for i in [2, 3, 5, 6]:
        parity3 *= syndrome[i]
    
    lookup = {
        (1, 1, 1): None,
        (-1 ,1, 1): 0, 
        (1, -1, 1): 4, 
        (1, 1, -1): 6, 
        (-1, -1, 1): 1, 
        (1, -1, -1): 5, 
        (-1, 1, -1): 3,
        (-1, -1, -1): 2
    }
    
    parity_list = (parity1, parity2, parity3)
    if parity_list in lookup:
        print(f"Apply Z to qubit: {lookup[parity_list]}")
        return 0
    else:
        print("Cannot correct error")
        return 1
    
    

if __name__ == "__main__":
    main()

