"""Pareto analysis: trade-off fronts among key endpoint pairs per case."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
from scan import sweep

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "robustness")
CASES = [
    ("insulin_secretion_inhibition", "ivgtt"),
    ("insulin_signal_global_inhibition", "ivgtt"),
    ("glucagon_secretion", "ogtt"),
    ("glucagon_signal_inhibition", "ogtt"),
    ("insulin_secretion_inhibition", "ogtt"),
    ("insulin_signal_global", "ogtt"),
]
AXES = [("hypo_burden_mgdl_min", "hyper_burden_mgdl_min"),
        ("hyper_burden_mgdl_min", "insulin_auc_muL_min"),
        ("glucose_sd_mgdl", "insulin_auc_muL_min")]


def pareto_front(df, a, b):
    """Non-dominated set minimizing both a and b."""
    pts = df[["modulation_fraction", a, b]].dropna().values
    keep = []
    for i, (u, x, y) in enumerate(pts):
        if not np.any((pts[:, 1] <= x) & (pts[:, 2] <= y) & ((pts[:, 1] < x) | (pts[:, 2] < y))):
            keep.append((u, x, y))
    return pd.DataFrame(keep, columns=["u", a, b])


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for ivn, ch in CASES:
        df, _ = sweep(ivn, ch)
        for a, b in AXES:
            pf = pareto_front(df, a, b)
            pf["intervention"] = ivn; pf["challenge"] = ch
            pf["axes"] = f"{a}|{b}"
            rows.append(pf)
    out = pd.concat(rows)
    out.to_csv(f"{OUT}/pareto_fronts.csv", index=False)
    print(out.groupby(["intervention", "challenge", "axes"]).size())


if __name__ == "__main__":
    main()
