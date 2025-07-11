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

tab2_z = [{"syndrome": [0, 1, 0], "correction": "IIXIIIX"},
          {"syndrome": [0, 0, 1], "correction": "IIIXIXI"}]

tab2_x = [{"syndrome": [0, 1, 0], "correction": "IIZIIIZ"},
          {"syndrome": [0, 0, 1], "correction": "IIIZIZI"}]

def lookup(memory):
    split = memory.split()
    flag_syndrome = [int(b) for b in split[2]][::-1]
    unflag_z = [int(b) for b in split[1]][::-1]
    unflag_x = [int(b) for b in split[0]][::-1]

    flag_syndrome_z = [flag_syndrome[3], flag_syndrome[1], flag_syndrome[2]]
    flag_syndrome_x = [flag_syndrome[0], flag_syndrome[4], flag_syndrome[5]]

    unflag_syndrome_z = [(unflag_z[0] + unflag_z[2] + unflag_z[4] + unflag_z[6]) % 2,  (unflag_z[3] + unflag_z[4] + unflag_z[5] + unflag_z[6]) % 2, (unflag_z[1] + unflag_z[2] + unflag_z[5] + unflag_z[6]) % 2]
    unflag_syndrome_x = [(unflag_x[0] + unflag_x[2] + unflag_x[4] + unflag_x[6]) % 2,  (unflag_x[3] + unflag_x[4] + unflag_x[5] + unflag_x[6]) % 2, (unflag_x[1] + unflag_x[2] + unflag_x[5] + unflag_x[6]) % 2]
    
    correction_x = "IIIIIII"
    correction_z = "IIIIIII"
    # finding correction_x
    if (flag_syndrome_z == unflag_syndrome_z):
        for entry in tab1_z:
            if (entry["syndrome"] == flag_syndrome_z):
                correction_x = entry["correction"]
    else:
        for entry in tab2_z:
            if (entry["syndrome"] == unflag_syndrome_z):
                correction_x = entry["correction"]
        if (correction_x == "IIIIIII"):
            for entry in tab1_z:
                if (entry["syndrome"] == unflag_syndrome_z):
                    correction_x = entry["correction"]

    # finding correction_z
    if (flag_syndrome_x == unflag_syndrome_x):
        for entry in tab1_x:
            if (entry["syndrome"] == flag_syndrome_x):
                correction_z = entry["correction"]
    else:
        for entry in tab2_x:
            if (entry["syndrome"] == unflag_syndrome_x):
                correction_z = entry["correction"]
        if (correction_z == "IIIIIII"):
            for entry in tab1_x:
                if (entry["syndrome"] == unflag_syndrome_x):
                    correction_z = entry["correction"]
                    
    return correction_x, correction_z