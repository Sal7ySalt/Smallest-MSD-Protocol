tab1_z = [{"syndrome": [1, 1, 1], "correction": "IIIIIII"},
          {"syndrome": [-1, 1, 1], "correction": "XIIIIII"},
          {"syndrome": [1, 1, -1], "correction": "IXIIIII"},
          {"syndrome": [-1, 1, -1], "correction": "IIXIIII"},
          {"syndrome": [1, -1, 1], "correction": "IIIXIII"},
          {"syndrome": [-1, -1, 1], "correction": "IIIIXII"},
          {"syndrome": [1, -1, -1], "correction": "IIIIIXI"},
          {"syndrome": [-1, -1, -1], "correction": "IIIIIIX"}]

tab1_x = [{"syndrome": [1, 1, 1], "correction": "IIIIIII"},
          {"syndrome": [-1, 1, 1], "correction": "ZIIIIII"},
          {"syndrome": [1, 1, -1], "correction": "IZIIIII"},
          {"syndrome": [-1, 1, -1], "correction": "IIZIIII"},
          {"syndrome": [1, -1, 1], "correction": "IIIZIII"},
          {"syndrome": [-1, -1, 1], "correction": "IIIIZII"},
          {"syndrome": [1, -1, -1], "correction": "IIIIIZI"},
          {"syndrome": [-1, -1, -1], "correction": "IIIIIIZ"}]

tab2_z = [{"syndrome": [1, -1, 1], "correction": "IIXIIIX"},
          {"syndrome": [1, 1, -1], "correction": "IIIXIXI"}]

tab2_x = [{"syndrome": [1, -1, 1], "correction": "IIZIIIZ"},
          {"syndrome": [1, 1, -1], "correction": "IIIZIZI"}]

def find_no_flag_syndrome(no_flag_allqubits_z, no_flag_allqubits_x):
    parity1_z = 1
    for i in [0, 2, 4, 6]:
        parity1_z *= no_flag_allqubits_z[i]

    parity2_z = 1
    for i in [3, 4, 5, 6]:
        parity2_z *= no_flag_allqubits_z[i]
        
    parity3_z = 1
    for i in [1, 2, 5, 6]:
        parity3_z *= no_flag_allqubits_z[i]
        
    parity1_x = 1
    for i in [0, 2, 4, 6]:
        parity1_x *= no_flag_allqubits_x[i]

    parity2_x = 1
    for i in [3, 4, 5, 6]:
        parity2_x *= no_flag_allqubits_x[i]
        
    parity3_x = 1
    for i in [1, 2, 5, 6]:
        parity3_x *= no_flag_allqubits_x[i]
        
    syndrome_no_flag_z = [parity1_z, parity2_z, parity3_z]
    syndrome_no_flag_x = [parity1_x, parity2_x, parity3_x]
    
    return syndrome_no_flag_z, syndrome_no_flag_x

def bool_syndrome_flag(syndrome_flag_z, syndrome_flag_x):
    if (syndrome_flag_z == [1, 1, 1] and syndrome_flag_x == [1, 1, 1]):
        return True
    else:
        return False

def syndrome(syndrome_flag_z, syndrome_flag_x, syndrome_no_flag_z, syndrome_no_flag_x):
    correction_z = None
    correction_x = None
    
    if (syndrome_flag_z == syndrome_no_flag_z and syndrome_flag_x == syndrome_no_flag_x):
        for entry in tab1_z:
            if (entry["syndrome"] == syndrome_flag_z):
                correction_z = entry["correction"]
        for entry in tab1_x:
            if (entry["syndrome"] == syndrome_flag_x):
                correction_x = entry["correction"]
        return correction_z, correction_x
    
    for entry in tab2_z:
        if (entry["syndrome"] == syndrome_no_flag_z):
            correction_z = entry["correction"]
    for entry in tab2_x:
        if (entry["syndrome"] == syndrome_no_flag_x):
            correction_x = entry["correction"]
        
    if (correction_z is None):
        for entry in tab1_z:
            if (entry["syndrome"] == syndrome_no_flag_z):
                correction_z = entry["correction"]
    if (correction_x is None):
        for entry in tab1_x:
            if (entry["syndrome"] == syndrome_no_flag_x):
                correction_x = entry["correction"]
            
    return correction_z, correction_x
    