"""Sweep the Steane-encoded 2-qubit MSD circuit over physical error rates: Meas case.

Calls ``logical_msd_meas_errors`` from ``logical_depolarizing.py``: depolarizing noise p on state preparation and readout flips P(1|0) = P(0|1) = p on qubits 7-13.
A single parameter p sets every active noise channel. p is the parameter of
Qiskit's ``depolarizing_error`` (and the readout-flip probability), swept over
``error_rates`` = 9 log-spaced values from 1e-5 to 1e-3.

Run from anywhere (the path is resolved relative to this file):

    python src/msd/two_qubit/meas_errors.py

Output: ``data/two_qubit/logical_level/depolarizing/logical_msd_meas_errors_sweep.npz`` with
arrays indexed by error rate:
    error_rates       physical error rate p
    sum_fid_list      sum of output fidelities over accepted shots
    sum_fid2_list     sum of squared fidelities (for the SEM)
    accepted_list     number of post-selected (accepted) shots
    total_shots_list  number of shots simulated

The script accumulates: each run adds ``num_shots`` shots per rate to the
totals already in the file and saves after every rate, so it can be stopped
and restarted. Delete the file to start from scratch. No random seed is set;
Aer draws a fresh seed for every batch, so repeated runs are statistically,
not bitwise, reproducible. These files feed the last two cells of
``notebooks/two_qubit/logical_level/creating_plots.ipynb``
(``figures/2Q_logical_plots.png``).
"""
import os
import sys
from pathlib import Path
import numpy as np

# Make the shared `msd` package importable when this file is run as a script.
src_dir = Path(__file__).resolve().parents[2]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from msd.two_qubit.fidelity_stats import combine_fidelity_stats
from msd.two_qubit.logical_depolarizing import logical_msd_meas_errors


# Physical error rates to sweep; the same rate is used for p1, spam0, spam1.
error_rates = np.logspace(-5, -3, 9)

# Shots added per error rate on each run, split into batches to limit memory.
num_shots = 500_000
batch_shots = 1000

save_path = (
    Path(__file__).resolve().parents[3]
    / "data/two_qubit/logical_level/depolarizing/logical_msd_meas_errors_sweep.npz"
)


def load_results(path):
    # Load previously accumulated results, or start empty.
    if not path.exists():
        return np.array([]), np.array([]), np.array([]), np.array([]), np.array([], dtype=int)

    data = np.load(path)
    # Older files have no squared-fidelity sums, so their SEM can't be recovered.
    if "sum_fid2_list" in data:
        sum_fid2_list = data["sum_fid2_list"]
    else:
        sum_fid2_list = np.full(len(data["error_rates"]), np.nan)
    return (
        data["error_rates"],
        data["sum_fid_list"],
        sum_fid2_list,
        data["accepted_list"],
        data["total_shots_list"],
    )


def save_results(path, rates, sum_fid_list, sum_fid2_list, accepted_list, total_shots_list):
    # Write to a temporary file first so an interrupted run can't corrupt the data.
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.stem + "_tmp.npz")
    np.savez(
        tmp_path,
        error_rates=rates,
        sum_fid_list=sum_fid_list,
        sum_fid2_list=sum_fid2_list,
        accepted_list=accepted_list,
        total_shots_list=total_shots_list,
    )
    os.replace(tmp_path, path)


def main():
    rates, sum_fid_list, sum_fid2_list, accepted_list, total_shots_list = load_results(save_path)

    # Add entries for any error rates not yet in the saved file.
    for p in error_rates:
        if not np.any(np.isclose(rates, p, rtol=1e-9, atol=0)):
            rates = np.append(rates, p)
            sum_fid_list = np.append(sum_fid_list, 0.0)
            sum_fid2_list = np.append(sum_fid2_list, 0.0)
            accepted_list = np.append(accepted_list, 0.0)
            total_shots_list = np.append(total_shots_list, 0)

    order = np.argsort(rates)
    rates = rates[order]
    sum_fid_list = sum_fid_list[order]
    sum_fid2_list = sum_fid2_list[order]
    accepted_list = accepted_list[order]
    total_shots_list = total_shots_list[order].astype(int)

    # i indexes the saved arrays; matching by value lets runs with different
    # error_rates lists share one file.
    for p in error_rates:
        i = np.flatnonzero(np.isclose(rates, p, rtol=1e-9, atol=0))[0]

        for _ in range(num_shots // batch_shots):
            # Returns sums over the accepted shots of this batch only.
            sumfid, sumfid2, accepted = logical_msd_meas_errors(batch_shots, p, p, p)
            sum_fid_list[i] += sumfid
            sum_fid2_list[i] += sumfid2
            accepted_list[i] += accepted

        total_shots_list[i] += num_shots

        # Save after each error rate so progress is kept if the run stops early.
        save_results(save_path, rates, sum_fid_list, sum_fid2_list, accepted_list, total_shots_list)

        stats = combine_fidelity_stats((sum_fid_list[i], sum_fid2_list[i], accepted_list[i]))
        print(
            f"p = {p:.2e}: total shots = {total_shots_list[i]}, "
            f"accepted = {stats['accepted']}, avg fidelity = {stats['mean_fidelity']:.8f}, "
            f"infidelity = {stats['mean_infidelity']:.3e} +/- {stats['sem']:.3e} (SEM)"
        )


if __name__ == "__main__":
    main()
