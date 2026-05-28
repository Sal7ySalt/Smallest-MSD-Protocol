import numpy as np
from typing import List, Any
from sklearn.neighbors import NearestNeighbors
from qiskit.circuit.library import TGate, TdgGate
import copy
import pickle
from qiskit.quantum_info import random_unitary

# Exotic magic-state angle
theta = np.arctan(np.sqrt((np.sqrt(5) - 1) / 2))

# Gate-name to integer-id mapping
gate_to_id = {
    'X': 0,
    'Y': 1,
    'Z': 2,
    'H': 3,
    'S': 4,
    'Sdg': 5,
    'Rz(-1*π/4)': 6,
    'Rz(1*π/4)': 7,
    'EMS': 8,
    'I': 9,
    'EMS1': 10
}

# Integer-id to gate-name mapping
id_to_gate = {
    0: 'X',
    1: 'Y',
    2: 'Z',
    3: 'H',
    4: 'S',
    5: 'Sdg',
    6: 'Rz(-1*π/4)',
    7: 'Rz(1*π/4)',
    8: 'EMS',
    9: 'I',
    10: 'EMS1'
}


def cost_function1(n: int) -> int:
    # Magic-gate cost model
    return (4 - 3*2**(3-n))


def rz_gate(theta: float):
    # Single-qubit Z rotation
    return np.array([[np.exp(-1j * theta/2), 0], [0, np.exp(1j * theta/2)]])


# Return allowed odd k values for tau rotations
def odd_k(denom: int) -> List[int]:
    highest = denom//2 - 1
    return list(range(-highest, highest+1, 2))


def tau_set(n: int):
    # Build tau gate set for a given denominator
    tau = []
    denom = 2**(n-1)
    k_list = odd_k(denom)
    cost = cost_function1(n)

    for k in k_list:
        gate = rz_gate(k*np.pi/denom)
        tau.append({
            "gate": gate,
            "t_count": cost,
            "id": gate_to_id[f'Rz({k}*π/{denom})'],
            "magic_gate": True
        })

    return tau


def key_from_U(U, tol: float = 1e-12, digits: int = 12):
    # Convert U into a canonical SU(2) key: U = aI + i(xX + yY + zZ)
    det = np.linalg.det(U)
    U = U / np.sqrt(det + 0j)

    a, b, c, d = U[0, 0], U[0, 1], U[1, 0], U[1, 1]

    key = np.array([
        (0.5 * (a + d)).real,
        (0.5 * (b + c)).imag,
        (0.5 * (b - c)).real,
        (0.5 * (a - d)).imag
    ], dtype=float)

    # Fix global sign ambiguity
    for val in key:
        if abs(val) > tol:
            if val < 0:
                key = -key
            break

    # Remove numerical noise
    key[np.abs(key) < tol] = 0.0
    key = np.round(key, digits)

    return tuple(key)


def rebuild_U(key):
    # Rebuild unitary from key = (a, x, y, z)
    a, x, y, z = key

    identity = np.eye(2, dtype='complex')
    pauli_x = np.array([[0, 1], [1, 0]])
    pauli_y = np.array([[0, -1j], [1j, 0]])
    pauli_z = np.array([[1, 0], [0, -1]])

    return a*identity + 1j*(x*pauli_x + y*pauli_y + z*pauli_z)


##################################################################################################################
# Database structure

class SequenceDB:
    def __init__(self):
        # Store each unique unitary and how it was generated
        self.index_of = {}      # key -> integer index
        self.keys = []          # index -> key tuple
        self.parent = []        # index -> parent index, -1 for root
        self.last_gate = []     # index -> gate id used to reach this node
        self.magic_count = []   # index -> total magic count

    def __len__(self):
        return len(self.parent)

    def contains(self, key):
        return key in self.index_of

    def get_index(self, key):
        return self.index_of.get(key)

    def add_root(self, key):
        # Add identity/root node
        if key in self.index_of:
            raise ValueError(f"Duplicate root key: {key}")

        idx = len(self.parent)
        self.index_of[key] = idx
        self.keys.append(tuple(key))
        self.parent.append(-1)
        self.last_gate.append(-1)
        self.magic_count.append(0)

        return idx

    def add(self, key, parent_idx, gate_id, magic_count):
        # Add new sequence if it is not already in the database
        if key in self.index_of:
            return self.index_of[key], False

        idx = len(self.parent)
        self.index_of[key] = idx
        self.keys.append(tuple(key))
        self.parent.append(int(parent_idx))
        self.last_gate.append(int(gate_id))
        self.magic_count.append(int(magic_count))

        return idx, True

    def reconstruct_seq_ids(self, idx):
        # Trace backward from node to root
        seq = []

        while idx != -1:
            g = self.last_gate[idx]
            if g != -1:
                seq.append(g)
            idx = self.parent[idx]

        seq.reverse()
        return seq

    def reconstruct_seq_names(self, idx, id_to_gate):
        # Convert gate IDs into readable gate names
        return [id_to_gate[g] for g in self.reconstruct_seq_ids(idx)]

    def get_magic_count(self, idx):
        return self.magic_count[idx]

    def save(self, filepath):
        # Save compressed database state
        state = {
            "keys": self.keys,
            "parent": np.asarray(self.parent, dtype=np.int32),
            "last_gate": np.asarray(self.last_gate, dtype=np.int16),
            "magic_count": np.asarray(self.magic_count, dtype=np.int16),
        }

        with open(filepath, "wb", buffering=16 * 1024 * 1024) as f:
            pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

    @classmethod
    def load(cls, filepath):
        # Load database and rebuild key lookup
        with open(filepath, "rb") as f:
            state = pickle.load(f)

        db = cls()
        db.keys = [tuple(k) for k in state["keys"]]
        db.parent = state["parent"].tolist()
        db.last_gate = state["last_gate"].tolist()
        db.magic_count = state["magic_count"].tolist()
        db.index_of = {k: i for i, k in enumerate(db.keys)}

        return db


##################################################################################################################
# Algorithm

def reconstruct_unitary_from_index(db, idx, gate_matrix):
    # Reconstruct unitary corresponding to database index
    U = np.eye(2, dtype=complex)
    gate_ids = []

    while db.parent[idx] != -1:
        gate_ids.append(db.last_gate[idx])
        idx = db.parent[idx]

    for gid in reversed(gate_ids):
        U = gate_matrix[gid] @ U

    return U


def generate_sequences(base_gate_set, max_magic_count, previous=None):
    # Generate all reachable sequences up to a magic-count cutoff
    clifford_gates = [g for g in base_gate_set if not g["magic_gate"]]
    magic_gates = [g for g in base_gate_set if g["magic_gate"]]

    gate_matrix = {g["id"]: np.asarray(g["gate"], dtype=complex) for g in base_gate_set}
    magic_ids = {g["id"] for g in magic_gates}

    if previous is None:
        db = SequenceDB()

        # Start from identity
        root_idx = db.add_root((1.0, 0.0, 0.0, 0.0))

        # Add all single-gate sequences
        for g in clifford_gates + magic_gates:
            U = gate_matrix[g["id"]]
            key = key_from_U(U)
            magic_count = 1 if g["magic_gate"] else 0

            db.add(
                key=key,
                parent_idx=root_idx,
                gate_id=g["id"],
                magic_count=magic_count
            )

        start_idx = 1  # skip root

    else:
        # Continue from existing database
        db = copy.deepcopy(previous)

        if max(db.magic_count, default=0) >= max_magic_count:
            print("Max Magic Count Reached")
            return db

        start_idx = 0

    i = start_idx

    while i < len(db):
        current_U = reconstruct_unitary_from_index(db, i, gate_matrix)
        current_magic_count = db.magic_count[i]
        last_gate_id = db.last_gate[i]

        # Alternate Clifford and magic layers
        last_was_clifford = (last_gate_id == -1) or (last_gate_id not in magic_ids)
        candidates = magic_gates if last_was_clifford else clifford_gates

        for gate_info in candidates:
            added_magic = 1 if gate_info["magic_gate"] else 0
            new_magic_count = current_magic_count + added_magic

            if new_magic_count > max_magic_count:
                continue

            new_U = gate_matrix[gate_info["id"]] @ current_U
            new_key = key_from_U(new_U)

            db.add(
                key=new_key,
                parent_idx=i,
                gate_id=gate_info["id"],
                magic_count=new_magic_count
            )

        i += 1

    return db


##################################################################################################################
# Approximating unitaries

def distance(U, V):
    # Distance between two SU(2) key vectors
    if np.allclose(U, V):
        return 0
    else:
        return np.sqrt((1 - abs(np.dot(U, V))) + 0j).real


def db_to_nn(db):
    # Build nearest-neighbor index from database keys
    keys = np.asarray(db.keys, dtype=float)

    nn = NearestNeighbors(algorithm="auto", metric="euclidean")
    nn.fit(keys)

    return nn


def unitary_from_key(db, key, gate_matrix):
    # Recover unitary and gate sequence from key
    idx = db.get_index(key)

    if idx is None:
        raise KeyError(f"Key not found in database: {key}")

    # Collect gate ids from target back to root
    gate_ids = []

    while idx != -1:
        gid = db.last_gate[idx]
        if gid != -1:
            gate_ids.append(gid)
        idx = db.parent[idx]

    # Apply gates in forward order
    gate_ids.reverse()

    U = np.eye(2, dtype=complex)

    for gid in gate_ids:
        U = gate_matrix[gid] @ U

    return U, gate_ids


def closest_neighbors(unitary, db, nn, epsilon, base_gate_set):
    # Search for database unitaries within epsilon of target unitary
    r = np.sqrt(2) * epsilon
    target_key = np.array(key_from_U(unitary), dtype=float).reshape(1, -1)

    idxs = nn.radius_neighbors(
        target_key,
        radius=r,
        return_distance=False
    )

    if len(idxs[0]) == 0:
        print(f"No closest neighbors given epsilon {epsilon}.")
        return None, None, None, None

    gate_matrix = {
        g["id"]: np.asarray(g["gate"], dtype=complex)
        for g in base_gate_set
    }

    best_magic = None
    best_distance = 1
    best_unitary = None
    best_seqs = None

    # Choose lowest magic count, then smallest distance
    for i in idxs[0]:
        temp_distance = distance(
            np.array(db.keys[i], dtype=float),
            np.array(key_from_U(unitary), dtype=float)
        )

        if temp_distance <= epsilon:
            temp_magic = db.magic_count[i]

            if (
                best_magic is None
                or temp_magic < best_magic
                or (temp_magic == best_magic and temp_distance < best_distance)
            ):
                best_magic = temp_magic
                best_distance = temp_distance
                best_unitary, best_seqs = unitary_from_key(
                    db,
                    db.keys[i],
                    gate_matrix
                )

    return best_magic, best_distance, best_unitary, best_seqs