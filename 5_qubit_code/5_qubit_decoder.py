import sys

# Global flag for phase measurement
flag = False

# Syndrome-to-correction dictionaries for XZZXI
DICT1_TRUE = [
    {"syndrome": [1, 1, 1, 1],   "correction": "IIIII"},
    {"syndrome": [-1, -1, 1, 1],  "correction": "IXZXI"},
    {"syndrome": [-1, 1, 1, -1],  "correction": "IYZXI"},
    {"syndrome": [1, 1, 1, -1],   "correction": "IZZXI"},
    {"syndrome": [1, -1, -1, 1],  "correction": "IIIXI"},
    {"syndrome": [-1, 1, -1, 1],  "correction": "IIXXI"},
    {"syndrome": [-1, 1, 1, 1],   "correction": "IIYXI"},
    {"syndrome": [1, -1, 1, 1],   "correction": "IIZXI"},
]
DICT1_FALSE = [
    {"syndrome": [1, 1, 1, 1],    "correction": "IIIII"},
    {"syndrome": [1, 1, 1, -1],   "correction": "XIIII"},
    {"syndrome": [-1, 1, -1, -1], "correction": "YIIII"},
    {"syndrome": [-1, 1, -1, 1],  "correction": "ZIIII"},
    {"syndrome": [-1, 1, 1, 1],   "correction": "IXIII"},
    {"syndrome": [-1, -1, 1, -1], "correction": "IYIII"},
    {"syndrome": [1, -1, 1, -1],  "correction": "IZIII"},
    {"syndrome": [-1, -1, 1, 1],  "correction": "IIXII"},
    {"syndrome": [-1, -1, -1, 1], "correction": "IIYII"},
    {"syndrome": [1, 1, -1, 1],   "correction": "IIZII"},
    {"syndrome": [1, -1, -1, 1],  "correction": "IIIXI"},
    {"syndrome": [-1, -1, -1, -1],"correction": "IIIYI"},
    {"syndrome": [-1, 1, 1, -1],  "correction": "IIIZI"},
]

# Syndrome-to-correction dictionaries for IXZZX
DICT2_TRUE = [
    {"syndrome": [1, 1, 1, 1],   "correction": "IIIII"},
    {"syndrome": [-1, 1, -1, 1], "correction": "IIIZX"},
    {"syndrome": [1, -1, -1, 1], "correction": "IIXZX"},
    {"syndrome": [1, -1, 1, 1],  "correction": "IIYZX"},
    {"syndrome": [-1, 1, 1, 1],  "correction": "IIZZX"},
    {"syndrome": [1, 1, -1, -1], "correction": "IIIIX"},
    {"syndrome": [1, -1, 1, -1], "correction": "IIIXX"},
    {"syndrome": [-1, -1, 1, 1], "correction": "IIIYX"},
]
DICT2_FALSE = [
    {"syndrome": [1, 1, 1, 1],    "correction": "IIIII"},
    {"syndrome": [-1, 1, 1, 1],   "correction": "IXIII"},
    {"syndrome": [-1, -1, 1, -1], "correction": "IYIII"},
    {"syndrome": [1, -1, 1, -1],  "correction": "IZIII"},
    {"syndrome": [-1, -1, 1, 1],  "correction": "IIXII"},
    {"syndrome": [-1, -1, -1, 1], "correction": "IIYII"},
    {"syndrome": [1, 1, -1, 1],   "correction": "IIZII"},
    {"syndrome": [1, -1, -1, 1],  "correction": "IIIXI"},
    {"syndrome": [-1, -1, -1, -1],"correction": "IIIYI"},
    {"syndrome": [-1, 1, 1, -1],  "correction": "IIIZI"},
    {"syndrome": [1, 1, -1, -1],  "correction": "IIIIX"},
    {"syndrome": [1, -1, -1, -1], "correction": "IIIIY"},
    {"syndrome": [1, -1, 1, 1],   "correction": "IIIIZ"},
]

# Syndrome-to-correction dictionaries for XIXZZ
DICT3_TRUE = [
    {"syndrome": [1, 1, 1, 1],    "correction": "IIIII"},
    {"syndrome": [-1, -1, 1, -1], "correction": "IIIZZ"},
    {"syndrome": [1, 1, 1, -1],   "correction": "IIXZZ"},
    {"syndrome": [1, 1, -1, -1],  "correction": "IIYZZ"},
    {"syndrome": [-1, -1, -1, -1],"correction": "IIZZZ"},
    {"syndrome": [1, -1, 1, 1],   "correction": "IIIIZ"},
    {"syndrome": [1, 1, -1, 1],   "correction": "IIIXZ"},
    {"syndrome": [-1, 1, -1, -1], "correction": "IIIYZ"},
]
DICT3_FALSE = [
    {"syndrome": [1, 1, 1, 1],    "correction": "IIIII"},
    {"syndrome": [1, 1, 1, -1],   "correction": "XIIII"},
    {"syndrome": [-1, 1, -1, -1], "correction": "YIIII"},
    {"syndrome": [-1, 1, -1, 1],  "correction": "ZIIII"},
    {"syndrome": [-1, -1, 1, 1],  "correction": "IIXII"},
    {"syndrome": [-1, -1, -1, 1], "correction": "IIYII"},
    {"syndrome": [1, 1, -1, 1],   "correction": "IIZII"},
    {"syndrome": [1, -1, -1, 1],  "correction": "IIIXI"},
    {"syndrome": [-1, -1, -1, -1],"correction": "IIIYI"},
    {"syndrome": [-1, 1, 1, -1],  "correction": "IIIZI"},
    {"syndrome": [1, 1, -1, -1],  "correction": "IIIIX"},
    {"syndrome": [1, -1, -1, -1], "correction": "IIIIY"},
    {"syndrome": [1, -1, 1, 1],   "correction": "IIIIZ"},
]

# Syndrome-to-correction dictionaries for ZXIXZ
DICT4_TRUE = [
    {"syndrome": [1, 1, 1, 1],    "correction": "IIIII"},
    {"syndrome": [1, 1, -1, 1],   "correction": "IIIXZ"},
    {"syndrome": [-1, 1, -1, 1],  "correction": "IXIXZ"},
    {"syndrome": [-1, -1, -1, -1],"correction": "IYIXZ"},
    {"syndrome": [1, -1, -1, -1], "correction": "IZIXZ"},
    {"syndrome": [1, -1, 1, 1],   "correction": "IIIIZ"},
    {"syndrome": [-1, 1, -1, -1], "correction": "IIIYZ"},
    {"syndrome": [-1, -1, 1, -1], "correction": "IIIZZ"},
]
DICT4_FALSE = [
    {"syndrome": [1, 1, 1, 1],    "correction": "IIIII"},
    {"syndrome": [1, 1, 1, -1],   "correction": "XIIII"},
    {"syndrome": [-1, 1, -1, -1], "correction": "YIIII"},
    {"syndrome": [-1, 1, -1, 1],  "correction": "ZIIII"},
    {"syndrome": [-1, 1, 1, 1],   "correction": "IXIII"},
    {"syndrome": [-1, -1, 1, -1], "correction": "IYIII"},
    {"syndrome": [1, -1, 1, -1],  "correction": "IZIII"},
    {"syndrome": [1, -1, -1, 1],  "correction": "IIIXI"},
    {"syndrome": [-1, -1, -1, -1],"correction": "IIIYI"},
    {"syndrome": [-1, 1, 1, -1],  "correction": "IIIZI"},
    {"syndrome": [1, 1, -1, -1],  "correction": "IIIIX"},
    {"syndrome": [1, -1, -1, -1], "correction": "IIIIY"},
    {"syndrome": [1, -1, 1, 1],   "correction": "IIIIZ"},
]

# Lookup utility
def lookup_correction(syndrome, true_dict, false_dict):
    table = true_dict if flag else false_dict
    for entry in table:
        if entry["syndrome"] == syndrome:
            return entry["correction"]
    return None

# Syndrome measurement functions
# XZZXI
def syndrome1(syndrome):
    return lookup_correction(syndrome, DICT1_TRUE, DICT1_FALSE)

# IXZZX
def syndrome2(syndrome):
    return lookup_correction(syndrome, DICT2_TRUE, DICT2_FALSE)

# XIXZZ
def syndrome3(syndrome):
    return lookup_correction(syndrome, DICT3_TRUE, DICT3_FALSE)

# ZXIXZ
def syndrome4(syndrome):
    return lookup_correction(syndrome, DICT4_TRUE, DICT4_FALSE)
