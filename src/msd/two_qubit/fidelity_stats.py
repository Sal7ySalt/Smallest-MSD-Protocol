"""Combine per-batch fidelity tallies into a mean, SEM and 95% interval.

Used by the sweep scripts (no_errors.py, ..., all_errors.py) to print progress.
Each logical_msd_* function in logical_depolarizing.py returns
(sum of F, sum of F^2, accepted shots) over the shots it kept.
"""
import numpy as np


def combine_fidelity_stats(*runs):
    """Pool (sumfid, sumfid2, accepted) tuples from any number of runs.

    Each run can be the direct output of a logical_msd_* function or
    previously saved totals. Since sums are additive, pooling is exact and
    weights every accepted shot equally, however many each run accepted.
    """
    sumfid = sum(float(r[0]) for r in runs)
    sumfid2 = sum(float(r[1]) for r in runs)
    accepted = int(sum(r[2] for r in runs))

    stats = {
        "accepted": accepted,
        "mean_fidelity": np.nan,
        "mean_infidelity": np.nan,
        "std": np.nan,
        "sem": np.nan,
        "ci95_fidelity": (np.nan, np.nan),
        "ci95_infidelity": (np.nan, np.nan),
    }
    if accepted == 0:
        return stats

    mean = sumfid / accepted
    stats["mean_fidelity"] = mean
    stats["mean_infidelity"] = 1.0 - mean

    # Sample variance needs at least two shots.
    if accepted < 2:
        return stats

    # Clip tiny negative values caused by floating-point cancellation.
    var = max((sumfid2 - sumfid**2 / accepted) / (accepted - 1), 0.0)
    std = np.sqrt(var)
    sem = std / np.sqrt(accepted)

    # Normal approximation; only reliable when many shots are accepted.
    half_width = 1.96 * sem
    stats["std"] = std
    stats["sem"] = sem
    stats["ci95_fidelity"] = (mean - half_width, mean + half_width)
    stats["ci95_infidelity"] = (1.0 - mean - half_width, 1.0 - mean + half_width)
    return stats
