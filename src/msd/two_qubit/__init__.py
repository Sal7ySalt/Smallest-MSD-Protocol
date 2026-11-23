"""Steane-encoded (logical-level) simulations of the 2-qubit [[2,1,1]] MSD protocol.

The physical protocol takes two copies of the magic state, applies CX (control
= output qubit) and H on the output qubit, measures the other qubit in Z, and
keeps the output when the outcome is 0. Here every qubit is replaced by a
7-qubit Steane block and the gates act transversally (14 data qubits).

Modules
-------
logical_depolarizing   Circuit and noise models with depolarizing gate noise.
logical_convergence    The same circuit with "convergence-axis" Kraus noise.
fidelity_stats         Pools (sum F, sum F^2, accepted) tallies into mean/SEM.
no_errors, one_q_errors, two_q_errors, meas_errors, all_errors
                       Command-line sweep scripts (one per noise case). They
                       call ``logical_depolarizing`` and append results to
                       ``data/two_qubit/logical_level/depolarizing/*_sweep.npz``.
"""
