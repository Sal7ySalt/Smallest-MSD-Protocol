"""Gate synthesis with exotic magic gates, and the phase-estimation benchmark.

``sequences``  Breadth-first enumeration of single-qubit Clifford + magic-gate
               sequences, stored in a ``SequenceDB``, plus nearest-neighbour
               lookup of approximations to a target unitary.
``qpe``        Single-ancilla phase estimation whose rotations are replaced by
               approximations taken from a ``SequenceDB``.
"""
