# Global flag for phase measurement
flag = False

# Syndrome-to-correction dictionaries for XXXXIII
DICT1_TRUE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],   "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, 1, -1, 1],  "correction": "IIXXIII"},
    {"syndrome": [1, 1, 1, -1, 1, 1],  "correction": "IXXXIII"},
    {"syndrome": [-1, -1, 1, -1, 1, 1],   "correction": "IYXXIII"},
    {"syndrome": [-1, -1, 1, 1, -1, 1],  "correction": "IZXXIII"},
    {"syndrome": [1, 1, 1, -1, 1, -1],  "correction": "IIIXIII"},
    {"syndrome": [-1, -1, -1, 1, -1, 1],   "correction": "IIYXIII"},
    {"syndrome": [-1, -1, -1, -1, 1, -1],   "correction": "IIZXIII"},
]
DICT1_FALSE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],    "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, -1, 1, 1],   "correction": "XIIIIII"},
    {"syndrome": [-1, 1, 1, 1, 1, 1], "correction": "ZIIIIII"},
    {"syndrome": [-1, 1, 1, -1, 1, 1],  "correction": "ZXXXIII"},
    {"syndrome": [1, 1, 1, -1, -1, 1],   "correction": "IXIIIII"},
    {"syndrome": [-1, -1, 1, -1, -1, 1], "correction": "IYIIIII"},
    {"syndrome": [-1, -1, 1, 1, 1, 1],  "correction": "IZIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, -1],  "correction": "IIXIIII"},
    {"syndrome": [-1, -1, -1, -1, -1, -1], "correction": "IIYIIII"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],   "correction": "IIZIIII"},
    {"syndrome": [1, 1, 1, -1, 1, -1],  "correction": "IIIXIII"},
    {"syndrome": [-1, 1, -1, -1, 1, -1],"correction": "IIIYIII"},
    {"syndrome": [-1, 1, -1, 1, 1, 1],  "correction": "IIIZIII"},
]

# Syndrome-to-correction dictionaries for IXXIXXI
DICT2_TRUE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],   "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, 1, 1, -1],  "correction": "IIIIXXI"},
    {"syndrome": [1, 1, 1, -1, -1, 1],  "correction": "IIXIXXI"},
    {"syndrome": [-1, -1, -1, -1, -1, 1],   "correction": "IIYIXXI"},
    {"syndrome": [-1, -1, -1, 1, 1, -1],  "correction": "IIZIXXI"},
    {"syndrome": [1, 1, 1, 1, -1, -1],  "correction": "IIIIIXI"},
    {"syndrome": [1, -1, 1, 1, 1, -1],   "correction": "IIIIYXI"},
    {"syndrome": [1, -1, 1, 1, -1, -1],   "correction": "IIIIZXI"},
]
DICT2_FALSE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],    "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, 1],   "correction": "IXIIIII"},
    {"syndrome": [-1, -1, 1, -1, -1, 1], "correction": "IYIIIII"},
    {"syndrome": [-1, -1, 1, 1, 1, 1],  "correction": "IZIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, -1],   "correction": "IIXIIII"},
    {"syndrome": [-1, -1, -1, -1, -1, -1], "correction": "IIYIIII"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],  "correction": "IIZIIII"},
    {"syndrome": [1, 1, 1, 1, -1, 1],  "correction": "IIIIXII"},
    {"syndrome": [1, -1, 1, 1, -1, 1], "correction": "IIIIYII"},
    {"syndrome": [1, -1, 1, 1, 1, 1],   "correction": "IIIIZII"},
    {"syndrome": [1, 1, 1, 1, -1, -1],  "correction": "IIIIIXI"},
    {"syndrome": [1, -1, -1, 1, -1, -1],"correction": "IIIIIYI"},
    {"syndrome": [1, -1, -1, 1, 1, 1],  "correction": "IIIIIZI"},
]

# Syndrome-to-correction dictionaries for IIXXIXX
DICT3_TRUE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],   "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, 1, -1, 1],  "correction": "IIIIIXX"},
    {"syndrome": [1, 1, 1, -1, -1, -1],  "correction": "IIIXIXX"},
    {"syndrome": [-1, 1, -1, -1, -1, -1],   "correction": "IIIYIXX"},
    {"syndrome": [-1, 1, -1, 1, 1, 1],  "correction": "IIIZIXX"},
    {"syndrome": [1, 1, 1, 1, 1, -1],  "correction": "IIIIIIX"},
    {"syndrome": [1, -1, -1, 1, -1, 1],   "correction": "IIIIIYX"},
    {"syndrome": [1, -1, -1, 1, 1, -1],   "correction": "IIIIIZX"},
]
DICT3_FALSE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],    "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, -1],   "correction": "IIXIIII"},
    {"syndrome": [-1, -1, -1, -1, -1, -1], "correction": "IIYIIII"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],  "correction": "IIZIIII"},
    {"syndrome": [1, 1, 1, -1, 1, -1],   "correction": "IIIXIII"},
    {"syndrome": [-1, 1, -1, -1, 1, -1], "correction": "IIIYIII"},
    {"syndrome": [-1, 1, -1, 1, 1, 1],  "correction": "IIIZIII"},
    {"syndrome": [1, 1, 1, 1, -1, -1],  "correction": "IIIIIXI"},
    {"syndrome": [1, -1, -1, 1, -1, -1], "correction": "IIIIIYI"},
    {"syndrome": [1, -1, -1, 1, 1, 1],   "correction": "IIIIIZI"},
    {"syndrome": [1, 1, 1, 1, 1, -1],  "correction": "IIIIIIX"},
    {"syndrome": [1, 1, -1, 1, 1, -1],"correction": "IIIIIIY"},
    {"syndrome": [1, 1, -1, 1, 1, 1],  "correction": "IIIIIIZ"},
]

# Syndrome-to-correction dictionaries for ZZZZIII
DICT4_TRUE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],   "correction": "IIIIIII"},
    {"syndrome": [1, -1, 1, 1, 1, 1],  "correction": "IIZZIII"},
    {"syndrome": [1, -1, 1, -1, -1, 1],  "correction": "IXZZIII"},
    {"syndrome": [-1, 1, 1, -1, -1, 1],   "correction": "IYZZIII"},
    {"syndrome": [-1, 1, 1, 1, 1, 1],  "correction": "IZZZIII"},
    {"syndrome": [-1, 1, -1, 1, 1, 1],  "correction": "IIIZIII"},
    {"syndrome": [-1, 1, -1, -1, -1, -1],   "correction": "IIXZIII"},
    {"syndrome": [1, -1, 1, -1, -1, -1],   "correction": "IIYZIII"},
]
DICT4_FALSE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],    "correction": "IIIIIII"},
    {"syndrome": [-1, 1, 1, 1, 1, 1],   "correction": "ZIIIIII"},
    {"syndrome": [1, 1, 1, -1, 1, 1], "correction": "XIIIIII"},
    {"syndrome": [-1, 1, 1, -1, 1, 1],  "correction": "YIIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, 1],   "correction": "IXIIIII"},
    {"syndrome": [-1, -1, 1, -1, -1, 1], "correction": "IYIIIII"},
    {"syndrome": [-1, -1, 1, 1, 1, 1],  "correction": "IZIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, -1],  "correction": "IIXIIII"},
    {"syndrome": [-1, -1, -1, -1, -1, -1], "correction": "IIYIIII"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],   "correction": "IIZIIII"},
    {"syndrome": [1, 1, 1, -1, 1, -1],  "correction": "IIIXIII"},
    {"syndrome": [-1, 1, -1, -1, 1, -1],"correction": "IIIYIII"},
    {"syndrome": [-1, 1, -1, 1, 1, 1],  "correction": "IIIZIII"},
]

# Syndrome-to-correction dictionaries for IZZIZZI
DICT5_TRUE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],   "correction": "IIIIIII"},
    {"syndrome": [1, 1, -1, 1, 1, 1],  "correction": "IIIIZZI"},
    {"syndrome": [1, 1, -1, -1, -1, -1],  "correction": "IIXIZZI"},
    {"syndrome": [-1, -1, 1, -1, -1, -1],   "correction": "IIYIZZI"},
    {"syndrome": [-1, -1, 1, 1, 1, 1],  "correction": "IIZIZZI"},
    {"syndrome": [1, -1, -1, 1, 1, 1],  "correction": "IIIIIZI"},
    {"syndrome": [1, -1, -1, 1, -1, 1],   "correction": "IIIIXZI"},
    {"syndrome": [1, 1, -1, 1, -1, 1],   "correction": "IIIIYZI"},
]
DICT5_FALSE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],    "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, 1],   "correction": "IXIIIII"},
    {"syndrome": [-1, -1, 1, -1, -1, 1], "correction": "IYIIIII"},
    {"syndrome": [-1, -1, 1, 1, 1, 1],  "correction": "IZIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, -1],   "correction": "IIXIIII"},
    {"syndrome": [-1, -1, -1, -1, -1, -1], "correction": "IIYIIII"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],  "correction": "IIZIIII"},
    {"syndrome": [1, 1, 1, 1, -1, 1],  "correction": "IIIIXII"},
    {"syndrome": [1, -1, 1, 1, -1, 1], "correction": "IIIIYII"},
    {"syndrome": [1, -1, 1, 1, 1, 1],   "correction": "IIIIZII"},
    {"syndrome": [1, 1, 1, 1, -1, -1],  "correction": "IIIIIXI"},
    {"syndrome": [1, -1, -1, 1, -1, -1],"correction": "IIIIIYI"},
    {"syndrome": [1, -1, -1, 1, 1, 1],  "correction": "IIIIIZI"},
]

# Syndrome-to-correction dictionaries for IIZZIZZ
DICT6_TRUE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],   "correction": "IIIIIII"},
    {"syndrome": [1, -1, 1, 1, 1, 1],  "correction": "IIIIIZZ"},
    {"syndrome": [1, -1, 1, -1, 1, -1],  "correction": "IIIXIZZ"},
    {"syndrome": [-1, -1, -1, -1, 1, -1],   "correction": "IIIYIZZ"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],  "correction": "IIIZIZZ"},
    {"syndrome": [1, 1, -1, 1, 1, 1],  "correction": "IIIIIIZ"},
    {"syndrome": [1, 1, -1, 1, -1, -1],   "correction": "IIIIIXZ"},
    {"syndrome": [1, -1, 1, 1, -1, -1],   "correction": "IIIIIYZ"},
]
DICT6_FALSE = [
    {"syndrome": [1, 1, 1, 1, 1, 1],    "correction": "IIIIIII"},
    {"syndrome": [1, 1, 1, -1, -1, -1],   "correction": "IIXIIII"},
    {"syndrome": [-1, -1, -1, -1, -1, -1], "correction": "IIYIIII"},
    {"syndrome": [-1, -1, -1, 1, 1, 1],  "correction": "IIZIIII"},
    {"syndrome": [1, 1, 1, -1, 1, -1],   "correction": "IIIXIII"},
    {"syndrome": [-1, 1, -1, -1, 1, -1], "correction": "IIIYIII"},
    {"syndrome": [-1, 1, -1, 1, 1, 1],  "correction": "IIIZIII"},
    {"syndrome": [1, 1, 1, 1, -1, -1],  "correction": "IIIIIXI"},
    {"syndrome": [1, -1, -1, 1, -1, -1], "correction": "IIIIIYI"},
    {"syndrome": [1, -1, -1, 1, 1, 1],   "correction": "IIIIIZI"},
    {"syndrome": [1, 1, 1, 1, 1, -1],  "correction": "IIIIIIX"},
    {"syndrome": [1, 1, -1, 1, 1, -1],"correction": "IIIIIIY"},
    {"syndrome": [1, 1, -1, 1, 1, 1],  "correction": "IIIIIIZ"},
]


# Lookup utility
def lookup_correction(syndrome, true_dict, false_dict):
    table = true_dict if flag else false_dict
    for entry in table:
        if entry["syndrome"] == syndrome:
            return entry["correction"]
    return None

# Syndrome measurement functions
# XXXXIII
def syndrome1(syndrome):
    return lookup_correction(syndrome, DICT1_TRUE, DICT1_FALSE)

# IXXIXXI
def syndrome2(syndrome):
    return lookup_correction(syndrome, DICT2_TRUE, DICT2_FALSE)

# IIXXIXX
def syndrome3(syndrome):
    return lookup_correction(syndrome, DICT3_TRUE, DICT3_FALSE)

# ZZZZIII
def syndrome4(syndrome):
    return lookup_correction(syndrome, DICT4_TRUE, DICT4_FALSE)

# IZZIZZI
def syndrome5(syndrome):
    return lookup_correction(syndrome, DICT5_TRUE, DICT5_FALSE)

# IIZZIZZ
def syndrome6(syndrome):
    return lookup_correction(syndrome, DICT6_TRUE, DICT6_FALSE)
