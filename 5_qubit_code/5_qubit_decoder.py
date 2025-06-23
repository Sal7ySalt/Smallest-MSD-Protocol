import sys

# Global flag for phase measurement
flag = False

# Syndrome-to-correction dictionaries for syndrome1
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

# Syndrome-to-correction dictionaries for syndrome2
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

# Syndrome-to-correction dictionaries for syndrome3
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

# Syndrome-to-correction dictionaries for syndrome4
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

# Function to read and validate syndrome bits
def read_syndrome():
    syndrome = []
    for i in range(4):
        # read and validate
        try:
            val = int(input(f"Syndrome bit {i+1}: "))
        except ValueError:
            print("Incorrect Stabilizer Measurement Outcome.")
            sys.exit(1)
        if abs(val) != 1:
            print("Incorrect Stabilizer Measurement Outcome.")
            sys.exit(1)
        syndrome.append(val)
    return syndrome

# Lookup utility
def lookup_correction(syndrome, true_dict, false_dict):
    table = true_dict if flag else false_dict
    for entry in table:
        if entry["syndrome"] == syndrome:
            return entry["correction"]
    return None

# Syndrome measurement functions
def syndrome1():
    print("Measuring XZZXI:")
    s = read_syndrome()
    return lookup_correction(s, DICT1_TRUE, DICT1_FALSE)

def syndrome2():
    print("Measuring IXZZX:")
    s = read_syndrome()
    return lookup_correction(s, DICT2_TRUE, DICT2_FALSE)

def syndrome3():
    print("Measuring XIXZZ:")
    s = read_syndrome()
    return lookup_correction(s, DICT3_TRUE, DICT3_FALSE)

def syndrome4():
    print("Measuring ZXIXZ:")
    s = read_syndrome()
    return lookup_correction(s, DICT4_TRUE, DICT4_FALSE)

# Main program
def main():
    global flag
    # Read flag measurement
    try:
        n = int(input("Enter flag measurement (1 or -1): "))
    except ValueError:
        print("Incorrect Flag Measurement.")
        sys.exit(1)
    if n == 1:
        flag = False
    elif n == -1:
        flag = True
    else:
        print("Incorrect Flag Measurement.")
        sys.exit(1)

    # Syndrome corrections with error checks
    corr1 = syndrome1()
    if corr1 is None:
        print("No valid correction for syndrome measurement 1.")
        sys.exit(1)
    corr2 = syndrome2()
    if corr2 is None:
        print("No valid correction for syndrome measurement 2.")
        sys.exit(1)
    corr3 = syndrome3()
    if corr3 is None:
        print("No valid correction for syndrome measurement 3.")
        sys.exit(1)
    corr4 = syndrome4()
    if corr4 is None:
        print("No valid correction for syndrome measurement 4.")
        sys.exit(1)

    # Print corrections
    print(f"Correction1: {corr1}")
    print(f"Correction2: {corr2}")
    print(f"Correction3: {corr3}")
    print(f"Correction4: {corr4}")



if __name__ == '__main__':
    main()
