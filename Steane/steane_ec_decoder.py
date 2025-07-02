# s1, s2, s3
unflag_lookup_x = [{"syndrome": [0, 1, 0], "correction": "IIIIZZZ"},
                   {"syndrome": [0, 0, 1], "correction": "IIIIZZZ"},
                   {"syndrome": [0, 1, 1], "correction": "IIIIZZZ"}]
# s4, s5, s6
unflag_lookup_z = [{"syndrome": [0, 1, 0], "correction": "IIIIXXX"},
                   {"syndrome": [0, 0, 1], "correction": "IIIIXXX"},
                   {"syndrome": [0, 1, 1], "correction": "IIIIXXX"}]

# fs1, fs2, fs3, s1, s2, s3
flag_lookup_x = [{"syndrome": [1, 0, 0, 0, 1, 0], "correction": "IIIIZZZ"},
                 {"syndrome": [1, 0, 0, 0, 0, 1], "correction": "IIIIZZZ"},
                 {"syndrome": [0, 1, 1, 0, 0, 1], "correction": "IIIIZZZ"}]

# fs4, fs5, fs6, s4, s5, s6
flag_lookup_z = [{"syndrome": [1, 0, 0, 0, 1, 0], "correction": "IIIIXXX"},
                 {"syndrome": [1, 0, 0, 0, 0, 1], "correction": "IIIIXXX"},
                 {"syndrome": [0, 1, 1, 0, 0, 1], "correction": "IIIIXXX"}]

def lookup(memory):
    split = memory.split()
    
    syndrome_flag1 = [int(b) for b in split[2]][::-1] 
    syndrome_unflag = [int(b) for b in split[1]][::-1]
    syndrome_flag2 = [int(b) for b in split[0]][::-1]
    
    unflag_x = [syndrome_unflag[0], syndrome_unflag[4], syndrome_unflag[5]]
    unflag_z = [syndrome_unflag[3], syndrome_unflag[1], syndrome_unflag[2]]
    flag_x = [syndrome_flag1[0], syndrome_flag2[1], syndrome_flag2[2], syndrome_unflag[0], syndrome_unflag[4], syndrome_unflag[5]]
    flag_z = [syndrome_flag2[0], syndrome_flag1[1], syndrome_flag1[2], syndrome_unflag[3], syndrome_unflag[1], syndrome_unflag[2]]
    
    correction_x = "IIIIIII"
    correction_z = "IIIIIII"
    
    if (syndrome_flag1 == [0, 0, 0] and syndrome_flag2 == [0, 0, 0]):
        return correction_z, correction_x
    elif (syndrome_flag1 != [0, 0, 0]):
        for entry in unflag_lookup_x:
            if (entry["syndrome"] == unflag_x):
                correction_z = entry["correction"]
        for entry in unflag_lookup_z:
            if (entry["syndrome"] == unflag_z):
                correction_x = entry["correction"]
        return correction_z, correction_x
    elif (syndrome_flag1 == [0, 0, 0] and syndrome_flag2 != [0, 0, 0]):
        for entry in flag_lookup_x:
            if (entry["syndrome"] == flag_x):
                correction_z = entry["correction"]
        for entry in flag_lookup_z:
            if (entry["syndrome"] == flag_z):
                correction_x = entry["correction"]
        return correction_z, correction_x
    return correction_z, correction_x
