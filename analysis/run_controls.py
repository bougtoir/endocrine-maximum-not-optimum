"""Mandatory negative/synthetic controls.

1. Monotonic synthetic responder: model replaced by a monotone-in-u glucose
   shift must classify Type0/I and NOT TypeII (no spurious interior optima).
2. Flat responder: identical curves -> Type0/III.
3. Inverted synthetic (planted U-shape) MUST be caught as TypeII
   (verifies the classifier can detect the target pattern).
4. Permutation sanity: interpolated loss between grid points stays smooth
   (monotone-interp consistency check).
Outputs to results/controls/.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
from homeostatic_loss import classify_response

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "controls")


def main():
    os.makedirs(OUT, exist_ok=True)
    u = np.linspace(0, 1, 21)
    rows = []

    cases = {
        "monotonic_worsening": 5 + 10 * u,
        "monotonic_improving": 5 - 4 * u + 0.2 * u ** 2,
        "flat": np.full_like(u, 5.0),
        "planted_U": 5 + 12 * (u - 0.45) ** 2,
        "planted_U_edge0": 5 + 12 * (u - 0.05) ** 2,
        "inverted_U_loss": 12 - 10 * (u - 0.4) ** 2,   # best at ends
        "noisy_flat": 5 + 0.01 * np.sin(37 * u),
    }
    for name, L in cases.items():
        lab, u_opt, info = classify_response(u, np.asarray(L, float))
        rows.append(dict(case=name, response_class=lab, u_opt=u_opt,
                         span=info.get("span")))
    df = pd.DataFrame(rows)
    df.to_csv(f"{OUT}/synthetic_controls.csv", index=False)
    print(df.to_string())

    # interpolation smoothness: the classifier result on a coarse grid must
    # match a 4x refined evaluation of a cubic interpolation (no sign flips).
    from scipy.interpolate import CubicSpline
    L = 5 + 12 * (u - 0.45) ** 2
    cs = CubicSpline(u, L)
    u2 = np.linspace(0, 1, 81)
    lab_c, *_ = classify_response(u, L)
    lab_f, *_ = classify_response(u2, cs(u2))
    print("interp consistency:", lab_c, "->", lab_f)
    pd.DataFrame([dict(coarse=lab_c, fine=lab_f)]).to_csv(
        f"{OUT}/interpolation_consistency.csv", index=False)


if __name__ == "__main__":
    main()
