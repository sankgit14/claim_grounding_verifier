"""
Calibration & Reliability Assessment Module
Computes Brier Score and Expected Calibration Error (ECE).
"""

from typing import List
import numpy as np


def compute_brier_score(y_true: List[int], confidences: List[float]) -> float:
    """
    y_true: 1 if correct prediction, 0 otherwise
    confidences: predicted confidence in [0, 1]
    """
    if not y_true:
        return 0.0
    y_arr = np.array(y_true, dtype=float)
    c_arr = np.array(confidences, dtype=float)
    return float(np.mean((c_arr - y_arr) ** 2))


def compute_expected_calibration_error(y_true: List[int], confidences: List[float], num_bins: int = 10) -> float:
    if not y_true:
        return 0.0

    y_arr = np.array(y_true)
    c_arr = np.array(confidences)
    bin_boundaries = np.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0
    total_n = len(y_arr)

    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        in_bin = (c_arr > bin_lower) & (c_arr <= bin_upper)
        bin_size = np.sum(in_bin)

        if bin_size > 0:
            bin_acc = np.mean(y_arr[in_bin])
            bin_conf = np.mean(c_arr[in_bin])
            ece += (bin_size / total_n) * np.abs(bin_acc - bin_conf)

    return round(float(ece), 4)
