flag1_lookup = [{"syndrome": '000010', "correction": "IIXXIII"},
                {"syndrome": '000100', "correction": "IXXXIII"},
                {"syndrome": '110100', "correction": "IYXXIII"},
                {"syndrome": '110010', "correction": "IZXXIII"},
                {"syndrome": '000101', "correction": "IIIXIII"},
                {"syndrome": '111010', "correction": "IIYXIII"},
                {"syndrome": '111101', "correction": "IIZXIII"}]

weight1err_lookup = [{"syndrome": '000100', "correction": "XIIIIII"},
                     {"syndrome": '100000', "correction": "ZIIIIII"},
                     {"syndrome": '100100', "correction": "ZXXXIII"},
                     {"syndrome": '000110', "correction": "IXIIIII"},
                     {"syndrome": '110110', "correction": "IYIIIII"},
                     {"syndrome": '110000', "correction": "IZIIIII"},
                     {"syndrome": '000111', "correction": "IIXIIII"},
                     {"syndrome": '111111', "correction": "IIYIIII"},
                     {"syndrome": '111000', "correction": "IIZIIII"},
                     {"syndrome": '000101', "correction": "IIIXIII"},
                     {"syndrome": '101101', "correction": "IIIYIII"},
                     {"syndrome": '101000', "correction": "IIIZIII"},
                     {"syndrome": '000010', "correction": "IIIIXII"},
                     {"syndrome": '010010', "correction": "IIIIYII"},
                     {"syndrome": '010000', "correction": "IIIIZII"},
                     {"syndrome": '000011', "correction": "IIIIIXI"},
                     {"syndrome": '011011', "correction": "IIIIIYI"},
                     {"syndrome": '011000', "correction": "IIIIIZI"},
                     {"syndrome": '000001', "correction": "IIIIIIX"},
                     {"syndrome": '001001', "correction": "IIIIIIY"},
                     {"syndrome": '001000', "correction": "IIIIIIZ"},
                     {"syndrome": '000100', "correction": "XIIIIII"},
                     {"syndrome": '100100', "correction": "YIIIIII"}]
                    

flag2_lookup = [{"syndrome": '000001', "correction": "IIIIXXI"},
                {"syndrome": '000110', "correction": "IIXIXXI"},
                {"syndrome": '111110', "correction": "IIYIXXI"},
                {"syndrome": '111001', "correction": "IIZIXXI"},
                {"syndrome": '000011', "correction": "IIIIIXI"},
                {"syndrome": '010001', "correction": "IIIIYXI"},
                {"syndrome": '010011', "correction": "IIIIZXI"}]


flag3_lookup = [{"syndrome": '000010', "correction": "IIIIIXX"},
                {"syndrome": '000111', "correction": "IIIXIXX"},
                {"syndrome": '101111', "correction": "IIIYIXX"},
                {"syndrome": '101000', "correction": "IIIZIXX"},
                {"syndrome": '000001', "correction": "IIIIIIX"},
                {"syndrome": '011010', "correction": "IIIIIYX"},
                {"syndrome": '011001', "correction": "IIIIIZX"}]

flag4_lookup = [{"syndrome": '010000', "correction": "IIZZIII"},
                {"syndrome": '010110', "correction": "IXZZIII"},
                {"syndrome": '100110', "correction": "IYZZIII"},
                {"syndrome": '100000', "correction": "IZZZIII"},
                {"syndrome": '101000', "correction": "IIIZIII"},
                {"syndrome": '101111', "correction": "IIXZIII"},
                {"syndrome": '010111', "correction": "IIYZIII"}]

flag5_lookup = [{"syndrome": '001000', "correction": "IIIIZZI"},
                {"syndrome": '001111', "correction": "IIXIZZI"},
                {"syndrome": '110111', "correction": "IIYIZZI"},
                {"syndrome": '110000', "correction": "IIZIZZI"},
                {"syndrome": '011000', "correction": "IIIIIZI"},
                {"syndrome": '011010', "correction": "IIIIXZI"},
                {"syndrome": '001010', "correction": "IIIIYZI"}]

flag6_lookup = [{"syndrome": '010000', "correction": "IIIIIZZ"},
                {"syndrome": '010101', "correction": "IIIXIZZ"},
                {"syndrome": '111101', "correction": "IIIYIZZ"},
                {"syndrome": '111000', "correction": "IIIZIZZ"},
                {"syndrome": '001000', "correction": "IIIIIIZ"},
                {"syndrome": '001011', "correction": "IIIIIXZ"},
                {"syndrome": '010011', "correction": "IIIIIYZ"}]

def allstab_lookup(memory):
    split = memory[0].split()
    flags = [split[11], split[9], split[7], split[5], split[3], split[1]]
    reversed_flags = [f[::-1] for f in flags]
    syndromes = [split[10], split[8], split[6], split[4], split[2], split[0]]
    reversed_syndromes = [s[::-1] for s in syndromes]
    corrections = []
    for i, flag in enumerate(reversed_flags):
        correction = "IIIIIII"
        if (flag == '00'):
            corrections.append(correction)
            continue
        elif (flag == '10'):
            for entry in weight1err_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
        elif (i == 0):
            for entry in flag1_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
        elif (i == 1):
            for entry in flag2_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
        elif (i == 2):
            for entry in flag3_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
        elif (i == 3):
            for entry in flag4_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
        elif (i == 4):
            for entry in flag5_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
        elif (i == 5):
            for entry in flag6_lookup:
                if (entry["syndrome"] == reversed_syndromes[i]):
                    correction = entry["correction"]
            corrections.append(correction)
            continue
            
    return corrections