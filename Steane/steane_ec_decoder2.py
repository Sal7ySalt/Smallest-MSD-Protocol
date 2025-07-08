flag1_lookup = [{"syndrome": [0, 0, 0, 0, 1, 0], "correction": "IIXXIII"},
                {"syndrome": [0, 0, 0, 1, 0, 0], "correction": "IXXXIII"},
                {"syndrome": [1, 1, 0, 1, 0, 0], "correction": "IYXXIII"},
                {"syndrome": [1, 1, 0, 0, 1, 0], "correction": "IZXXIII"},
                {"syndrome": [0, 0, 0, 1, 0, 1], "correction": "IIIXIII"},
                {"syndrome": [1, 1, 1, 0, 1, 0], "correction": "IIYXIII"},
                {"syndrome": [1, 1, 1, 1, 0, 1], "correction": "IIZXIII"}]

weight1err_lookup = [{"syndrome": [0, 0, 0, 1, 0, 0], "correction": "XIIIIII"},
                     {"syndrome": [1, 0, 0, 0, 0, 0], "correction": "ZIIIIII"},
                     {"syndrome": [1, 0, 0, 1, 0, 0], "correction": "ZXXXIII"},
                     {"syndrome": [0, 0, 0, 1, 1, 0], "correction": "IXIIIII"},
                     {"syndrome": [1, 1, 0, 1, 1, 0], "correction": "IYIIIII"},
                     {"syndrome": [1, 1, 0, 0, 0, 0], "correction": "IZIIIII"},
                     {"syndrome": [0, 0, 0, 1, 1, 1], "correction": "IIXIIII"},
                     {"syndrome": [1, 1, 1, 1, 1, 1], "correction": "IIYIIII"},
                     {"syndrome": [1, 1, 1, 0, 0, 0], "correction": "IIZIIII"},
                     {"syndrome": [0, 0, 0, 1, 0, 1], "correction": "IIIXIII"},
                     {"syndrome": [1, 0, 1, 1, 0, 1], "correction": "IIIYIII"},
                     {"syndrome": [1, 0, 1, 0, 0, 0], "correction": "IIIZIII"},
                     {"syndrome": [0, 0, 0, 0, 1, 0], "correction": "IIIIXII"},
                     {"syndrome": [0, 1, 0, 0, 1, 0], "correction": "IIIIYII"},
                     {"syndrome": [0, 1, 0, 0, 0, 0], "correction": "IIIIZII"},
                     {"syndrome": [0, 0, 0, 0, 1, 1], "correction": "IIIIIXI"},
                     {"syndrome": [0, 1, 1, 0, 1, 1], "correction": "IIIIIYI"},
                     {"syndrome": [0, 1, 1, 0, 0, 0], "correction": "IIIIIZI"},
                     {"syndrome": [0, 0, 0, 0, 0, 1], "correction": "IIIIIIX"},
                     {"syndrome": [0, 0, 1, 0, 0, 1], "correction": "IIIIIIY"},
                     {"syndrome": [0, 0, 1, 0, 0, 0], "correction": "IIIIIIZ"},
                     {"syndrome": [0, 0, 0, 1, 0, 0], "correction": "XIIIIII"},
                     {"syndrome": [1, 0, 0, 1, 0, 0], "correction": "YIIIIII"}]
                    

flag2_lookup = [{"syndrome": [0, 0, 0, 0, 0, 1], "correction": "IIIIXXI"},
                {"syndrome": [0, 0, 0, 1, 1, 0], "correction": "IIXIXXI"},
                {"syndrome": [1, 1, 1, 1, 1, 0], "correction": "IIYIXXI"},
                {"syndrome": [1, 1, 1, 0, 0, 1], "correction": "IIZIXXI"},
                {"syndrome": [0, 0, 0, 0, 1, 1], "correction": "IIIIIXI"},
                {"syndrome": [0, 1, 0, 0, 0, 1], "correction": "IIIIYXI"},
                {"syndrome": [0, 1, 0, 0, 1, 1], "correction": "IIIIZXI"}]


flag3_lookup = [{"syndrome": [0, 0, 0, 0, 1, 0], "correction": "IIIIIXX"},
                {"syndrome": [0, 0, 0, 1, 1, 1], "correction": "IIIXIXX"},
                {"syndrome": [1, 0, 1, 1, 1, 1], "correction": "IIIYIXX"},
                {"syndrome": [1, 0, 1, 0, 0, 0], "correction": "IIIZIXX"},
                {"syndrome": [0, 0, 0, 0, 0, 1], "correction": "IIIIIIX"},
                {"syndrome": [0, 1, 1, 0, 1, 0], "correction": "IIIIIYX"},
                {"syndrome": [0, 1, 1, 0, 0, 1], "correction": "IIIIIZX"}]

flag4_lookup = [{"syndrome": [0, 1, 0, 0, 0, 0], "correction": "IIZZIII"},
                {"syndrome": [0, 1, 0, 1, 1, 0], "correction": "IXZZIII"},
                {"syndrome": [1, 0, 0, 1, 1, 0], "correction": "IYZZIII"},
                {"syndrome": [1, 0, 0, 0, 0, 0], "correction": "IZZZIII"},
                {"syndrome": [1, 0, 1, 0, 0, 0], "correction": "IIIZIII"},
                {"syndrome": [1, 0, 1, 1, 1, 1], "correction": "IIXZIII"},
                {"syndrome": [0, 1, 0, 1, 1, 1], "correction": "IIYZIII"}]

flag5_lookup = [{"syndrome": [0, 0, 1, 0, 0, 0], "correction": "IIIIZZI"},
                {"syndrome": [0, 0, 1, 1, 1, 1], "correction": "IIXIZZI"},
                {"syndrome": [1, 1, 0, 1, 1, 1], "correction": "IIYIZZI"},
                {"syndrome": [1, 1, 0, 0, 0, 0], "correction": "IIZIZZI"},
                {"syndrome": [0, 1, 1, 0, 0, 0], "correction": "IIIIIZI"},
                {"syndrome": [0, 1, 1, 0, 1, 0], "correction": "IIIIXZI"},
                {"syndrome": [0, 0, 1, 0, 1, 0], "correction": "IIIIYZI"}]

flag6_lookup = [{"syndrome": [0, 1, 0, 0, 0, 0], "correction": "IIIIIZZ"},
                {"syndrome": [0, 1, 0, 1, 0, 1], "correction": "IIIXIZZ"},
                {"syndrome": [1, 1, 1, 1, 0, 1], "correction": "IIIYIZZ"},
                {"syndrome": [1, 1, 1, 0, 0, 0], "correction": "IIIZIZZ"},
                {"syndrome": [0, 0, 1, 0, 0, 0], "correction": "IIIIIIZ"},
                {"syndrome": [0, 0, 1, 0, 1, 1], "correction": "IIIIIXZ"},
                {"syndrome": [0, 1, 0, 0, 1, 1], "correction": "IIIIIYZ"}]

def allstab_lookup(memory):
    syndrome = [int (b) for b in memory][::-1]
    correction = "IIIIIII"
    
    for entry in weight1err_lookup:
        if (entry == syndrome):
            correction = entry["correction"]
    return correction