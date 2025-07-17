tab1_z = [{"syndrome": [0, 0, 0], "correction": "IIIIIII"},
          {"syndrome": [1, 0, 0], "correction": "XIIIIII"},
          {"syndrome": [0, 0, 1], "correction": "IXIIIII"},
          {"syndrome": [1, 0, 1], "correction": "IIXIIII"},
          {"syndrome": [0, 1, 0], "correction": "IIIXIII"},
          {"syndrome": [1, 1, 0], "correction": "IIIIXII"},
          {"syndrome": [0, 1, 1], "correction": "IIIIIXI"},
          {"syndrome": [1, 1, 1], "correction": "IIIIIIX"}]

tab1_x = [{"syndrome": [0, 0, 0], "correction": "IIIIIII"},
          {"syndrome": [1, 0, 0], "correction": "ZIIIIII"},
          {"syndrome": [0, 0, 1], "correction": "IZIIIII"},
          {"syndrome": [1, 0, 1], "correction": "IIZIIII"},
          {"syndrome": [0, 1, 0], "correction": "IIIZIII"},
          {"syndrome": [1, 1, 0], "correction": "IIIIZII"},
          {"syndrome": [0, 1, 1], "correction": "IIIIIZI"},
          {"syndrome": [1, 1, 1], "correction": "IIIIIIZ"}]

virtual_dec_tab = [{"syndrome": [0, 0, 0], "correction": None},
                {"syndrome": [1, 0, 0], "correction": 0},
                {"syndrome": [0, 1, 0], "correction": 3},
                {"syndrome": [0, 0, 1], "correction": 1},
                {"syndrome": [1, 1, 0], "correction": 4},
                {"syndrome": [1, 0, 1], "correction": 2},
                {"syndrome": [0, 1, 1], "correction": 5},
                {"syndrome": [1, 1, 1], "correction": 6}]

def lookup(memory):
    split = memory.split()
    flag1 = [int(b) for b in split[1][::-1]]
    flag2 = [int(b) for b in split[0][::-1]]
    
    syndrome_x = [flag1[0], flag2[1], flag2[2]]
    syndrome_z = [flag2[0], flag1[1], flag1[2]]
    
    correction_x = None
    correction_z = None
    
    for entry in tab1_z:
        if (entry["syndrome"] == syndrome_z):
            correction_x = entry["correction"]
    for entry in tab1_x:
        if (entry["syndrome"] == syndrome_x):
            correction_z = entry["correction"]
    return correction_x, correction_z

def hadamard_lookup(memory):
    split = memory.split()
    split = list(split[0])
    bit_str = [int(b) for b in split[::-1]]
    stab1 = (bit_str[0] + bit_str[2] + bit_str[4] + bit_str[6]) % 2
    stab2 = (bit_str[3] + bit_str[4] + bit_str[5] + bit_str[6]) % 2
    stab3 = (bit_str[1] + bit_str[2] + bit_str[5] + bit_str[6]) % 2
    syndrome = [stab1, stab2, stab3]
    
    correction_qubit = None
    for entry in virtual_dec_tab:
        if (entry["syndrome"] == syndrome):
            correction_qubit = entry["correction"]
    
    if (correction_qubit != None):
        bit_str[correction_qubit] = (bit_str[correction_qubit] + 1) % 2
    
    logical_op = (bit_str[1] + bit_str[3] + bit_str[5]) % 2
    return logical_op

def cz_lookup(memory):
    split = memory.split()
    block1 = list(split[1])[::-1]
    block1 = [int(b) for b in block1]
    block2 = list(split[0])[::-1]
    block2 = [int(b) for b in block2]
    
    b1_stab1 = (block1[0] + block1[2] + block1[4] + block1[6]) % 2
    b1_stab2 = (block1[3] + block1[4] + block1[5] + block1[6]) % 2
    b1_stab3 = (block1[1] + block1[2] + block1[5] + block1[6]) % 2
    b1_syndrome = [b1_stab1, b1_stab2, b1_stab3]
    
    b2_stab1 = (block2[0] + block2[2] + block2[4] + block2[6]) % 2
    b2_stab2 = (block2[3] + block2[4] + block2[5] + block2[6]) % 2
    b2_stab3 = (block2[1] + block2[2] + block2[5] + block2[6]) % 2
    b2_syndrome = [b2_stab1, b2_stab2, b2_stab3]
    
    b1_correction_qubit = None
    b2_correction_qubit = None
    for entry in virtual_dec_tab:
        if (entry["syndrome"] == b1_syndrome):
            b1_correction_qubit = entry["correction"]
        if (entry["syndrome"] == b2_syndrome):
            b2_correction_qubit = entry["correction"]
    
    if (b1_correction_qubit != None):
        block1[b1_correction_qubit] = (block1[b1_correction_qubit] + 1) % 2
    if (b2_correction_qubit != None):
        block2[b2_correction_qubit] = (block2[b2_correction_qubit] + 1) % 2
    
    b1_logical_op = (block1[1] + block1[3] + block1[5]) % 2
    b2_logical_op = (block2[1] + block2[3] + block2[5]) % 2
    
    return (b1_logical_op == b2_logical_op)