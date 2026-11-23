"""Shared code for the smallest magic-state-distillation (MSD) protocols.

Subpackages
-----------
two_qubit       Logical-level (Steane-encoded) simulations of the 2-qubit
                [[2,1,1]] protocol, plus the command-line sweep scripts that
                write ``data/two_qubit/logical_level/depolarizing/*_sweep.npz``.
three_qubit     Logical-level (Steane-encoded) simulations of the 3-qubit
                [[3,1,1]] protocol.
gate_synthesis  Breadth-first search for short Clifford + magic-gate
                sequences, and the phase-estimation benchmark built on it.

Top-level modules
-----------------
flow_diagrams   Builds the polynomial Bloch-vector map of a small stabilizer
                code; currently imported (but not called) by
                ``notebooks/two_qubit/physical_level/creating_plots.ipynb``.
hardware        Shared constants (magic-state angle, Quantinuum H2-2 error
                rates) and a Steane encoder; not imported elsewhere.

Notebooks put ``src/`` on ``sys.path`` themselves, so the package is used
without installation. See the README for the full workflow.
"""
