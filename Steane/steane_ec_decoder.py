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
