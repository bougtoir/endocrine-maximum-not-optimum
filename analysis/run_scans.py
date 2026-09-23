"""Full grid scans: all interventions x all challenges, coarse + refined grids."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
from scan import run_grid, sweep, U_GRID
from interventions import ALL_INTERVENTIONS, INTERVENTIONS

CHALLENGES = ["fasting", "ivgtt", "ogtt", "ivitt", "civii"]
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "scans")


def refine_u(intervention_name, challenge, u_coarse, half_width=0.1, n=21):
    """Local refinement around the coarse-grid optimum."""
    lo, hi = max(0.0, u_coarse - half_width), min(1.0, u_coarse + half_width)
    g = np.linspace(lo, hi, n)
    df, cls = sweep(intervention_name, challenge, u_grid=g)
    return df, cls


def main():
    os.makedirs(OUT, exist_ok=True)
    df, cls = run_grid(ALL_INTERVENTIONS, CHALLENGES)
    df.to_csv(f"{OUT}/full_endpoints.csv", index=False)
    cls.to_csv(f"{OUT}/full_classification.csv", index=False)

    # refine every case with a non-Type0 interior-ish optimum
    rows_e, rows_c = [], []
    for _, r in cls.iterrows():
        if r["response_class"] not in ("Type0", "TypeIII") and 0.02 < r["u_opt"] < 0.99:
            dfr, clsr = refine_u(r["intervention"], r["challenge"], r["u_opt"])
            clsr = dict(clsr)
            clsr["loss_baseline"] = r["loss_baseline"]   # true L(u=0)
            clsr["loss_max"] = r["loss_max"]             # true L(u=1)
            clsr["gain0"] = r["loss_baseline"] - clsr["loss_opt"]
            clsr["gain1"] = r["loss_max"] - clsr["loss_opt"]
            rows_e.append(dfr); rows_c.append(pd.DataFrame([clsr]))
    if rows_c:
        pde = pd.concat(rows_e); pdc = pd.concat(rows_c)
        pde.to_csv(f"{OUT}/refined_endpoints.csv", index=False)
        pdc.to_csv(f"{OUT}/refined_classification.csv", index=False)
        print(pdc[["intervention", "challenge", "response_class", "u_opt",
                   "loss_baseline", "loss_opt", "loss_max", "gain0", "gain1"]]
              .round(3).to_string())
    print("\nFull-grid classification:")
    print(cls[["intervention", "challenge", "response_class", "u_opt",
               "loss_baseline", "loss_opt", "loss_max"]].round(3).to_string())


if __name__ == "__main__":
    main()
