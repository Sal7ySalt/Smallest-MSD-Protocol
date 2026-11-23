"""Polynomial Bloch-vector map of a small stabilizer-code distillation protocol.

Each input copy is rho = (I + xX + yY + zZ)/2, so for an n-qubit Pauli string
P, Tr(P rho^{(x)n}) = (+/-) x^{#X} y^{#Y} z^{#Z}. Projecting n copies onto the
code space and reading off the logical Bloch vector gives

    p_success  ~  sum_{S in stabilizer group} Tr(S rho^n)
    <L>        =  sum_S Tr(S L rho^n) / sum_S Tr(S rho^n),   L in {X_L, Y_L, Z_L}.

The functions below count the X/Y/Z content of each term and turn the counts
into sympy rational functions of (x, y, z). Plotting those maps on the y = 0
plane gives flow diagrams such as ``figures/flow_diagrams.png``. No notebook
in the repository currently calls these functions; see the README.

Code labels follow Qiskit's Pauli-label convention: the rightmost character
acts on qubit 0.
"""
import sympy as sp
import itertools
import qiskit.quantum_info as qi
import typing

def CounterXYZ(pauli_string_list):
    # Map each signed Pauli label to (#'-' signs, #X, #Y, #Z) and count how often
    # each tuple occurs. The tuple is one monomial (-1)^s x^a y^b z^c; its count
    # is the integer coefficient of that monomial.
    XY_tuple = [(stabilizer.count('-'),stabilizer.count('X'),stabilizer.count('Y'),stabilizer.count('Z')) for stabilizer in pauli_string_list]
    count_dict = {}
# Counting elements
    for element in XY_tuple:
        if element in count_dict:
            count_dict[element] += 1
        else:
            count_dict[element] = 1
    #print(count_dict)
    return count_dict

def generator2stabilizer(generator_set, to_label=True):
    # Enumerate the full stabilizer group (2^k elements, identity included) as
    # products over every subset of the k generators. Labels keep their sign.

    G_qi = [qi.Pauli(G) for G in generator_set]
    n_qubit = G_qi[0].num_qubits
    S_qi = []
    for n_ele in range(len(G_qi)+1):
        for subset in itertools.combinations(G_qi, n_ele):
            stabilizer = qi.Pauli('I'*n_qubit)
            for element in subset:
                stabilizer = stabilizer @ element
            S_qi.append(stabilizer)



    return [S.to_label() for S in S_qi] if to_label else S_qi

def get_poly_from_code(generator_set, logical_operator):
    # Return the monomial counts for the success probability ('p') and the
    # unnormalised logical Bloch components ('X', 'Y', 'Z'). Y_L is built as
    # -i Z_L X_L so that it is Hermitian with the usual sign.

    X_L, Z_L = qi.Pauli(logical_operator['X']), qi.Pauli(logical_operator['Z'])
    Y_L = -1j * Z_L @ X_L

    S_qi = generator2stabilizer(generator_set=generator_set, to_label=False)
    stabilizer_set = [S.to_label() for S in S_qi] 
    dict_p_suc = CounterXYZ(stabilizer_set)

    logical_X_qi = [S @ X_L for S in S_qi]
    logical_X_set = [ele.to_label() for ele in logical_X_qi]
    dict_X = CounterXYZ(logical_X_set)

    logical_Z_qi = [S @ Z_L for S in S_qi]
    logical_Z_set = [ele.to_label() for ele in logical_Z_qi]
    dict_Z = CounterXYZ(logical_Z_set)

    logical_Y_qi = [S @ Y_L for S in S_qi]
    logical_Y_set = [ele.to_label() for ele in logical_Y_qi]
    dict_Y = CounterXYZ(logical_Y_set)

    poly_dicts = {'p': dict_p_suc, 'X': dict_X, 'Y': dict_Y, 'Z': dict_Z}

    return poly_dicts

def poly_dicts_to_sympy(poly_dicts, y_value=None):
    # Return (p_success, x', y', z') as sympy expressions in the input Bloch
    # components x, y, z. Pass y_value (e.g. 0) to restrict to a plane of the
    # Bloch ball. p_success is unnormalised: it counts stabilizer terms without
    # the 1/2^n factors.
    x = sp.Symbol('x', real=True)
    y = sp.Symbol('y', real=True)
    z = sp.Symbol('z', real=True)

    def dict_to_sympy(poly_dict):
        poly_sp = 0
        for ele in poly_dict:
            coef = poly_dict[ele]
            poly_sp += (-1)**ele[0] * x**ele[1] * y**ele[2] * z**ele[3] * coef
        return poly_sp
    
    p_poly = dict_to_sympy(poly_dicts['p'])
    X_poly = dict_to_sympy(poly_dicts['X'])
    Y_poly = dict_to_sympy(poly_dicts['Y'])
    Z_poly = dict_to_sympy(poly_dicts['Z'])

    if y_value is None:
        return p_poly, X_poly/p_poly, Y_poly/p_poly, Z_poly/p_poly
    else:
        return p_poly.subs(y, y_value), (X_poly/p_poly).subs(y, y_value), (Y_poly/p_poly).subs(y, y_value), (Z_poly/p_poly). subs(y, y_value)
    



def get_stabilizer_code(code_name: str) -> typing.Tuple[list[str], typing.Union[dict, list[dict]]]:
    # Look up the stabilizer generators and logical operators of a named code:
    #   '2_1_1' : the [[2,1,1]] code of the 2-qubit protocol (stabilizer ZZ).
    #   '3_1_1' : the [[3,1,1]] code of the 3-qubit protocol.
    #   '3a_y'  : '3_1_1' with Pauli labels cycled X->Y, Y->Z, Z->X.

    if code_name == '2_1_1':
        generator_set = ['ZZ']
        logical_operator = {'Z': 'XX', 'X': 'ZI'}
    
    elif code_name == '3_1_1':
        generator_set = ['XZI', 'ZXX']
        logical_operator = {'Z':'IIX','X':'IZZ'}
    elif code_name == '3a_y': ## the 3a code with Pauli label shifted: X->Y; Y->Z; Z->X
        generator_set = ['YXI', 'XYY']
        logical_operator = {'X': 'IIY', 'Z': '-IXZ'}

    else:
        raise ValueError("the input code name has not been implemented.")
    return (generator_set, logical_operator)