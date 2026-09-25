"""Full grid scans: all interventions x all challenges, coarse + refined grids."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
from scan import run_grid, sweep, U_GRID
from interventions import ALL_INTERVENTIONS, INTERVENTIONS

CHALLENGES = ["fasting", "ivgtt", "ogtt", "ivitt", "civii"]
OUT = os.path.join(os.path.dirname(__file__), "..", "results", "scans")


def refine_u(intervention_name, challenge, u_coarse, full_df,
             half_width=0.1, n=21):
    """Local refinement around the coarse-grid optimum.

    Classification is recomputed on the refined grid combined with the true
    u=0 and u=1 endpoints from the full-range scan — never on the local
    window alone, whose edges are not the true endpoints.
    """
    from homeostatic_loss import classify_response
    lo, hi = max(0.0, u_coarse - half_width), min(1.0, u_coarse + half_width)
    g = np.linspace(lo, hi, n)
    df, _ = sweep(intervention_name, challenge, u_grid=g)
    ends = full_df[full_df["modulation_fraction"].isin([0.0, 1.0])]
    combo = pd.concat([df, ends]).sort_values("modulation_fraction")
    label, u_opt, info = classify_response(
        combo["modulation_fraction"].to_numpy(),
        combo["composite_loss"].to_numpy())
    L0 = float(ends[ends.modulation_fraction == 0.0]["composite_loss"].iloc[0])
    L1 = float(ends[ends.modulation_fraction == 1.0]["composite_loss"].iloc[0])
    rec = dict(intervention=intervention_name, challenge=challenge,
               response_class=label, u_opt=float(u_opt),
               loss_baseline=L0, loss_opt=float(combo.composite_loss.min()),
               loss_max=L1,
               gain0=info.get("gain0", 0.0), gain1=info.get("gain1", 0.0),
               span=info.get("span", np.nan))
    return df, rec


def main():
    os.makedirs(OUT, exist_ok=True)
    df, cls = run_grid(ALL_INTERVENTIONS, CHALLENGES)
    df.to_csv(f"{OUT}/full_endpoints.csv", index=False)
    cls.to_csv(f"{OUT}/full_classification.csv", index=False)

    # refine every case with a non-Type0 interior-ish optimum
    rows_e, rows_c = [], []
    for _, r in cls.iterrows():
        if r["response_class"] not in ("Type0", "TypeIII") and 0.02 < r["u_opt"] < 0.99:
            mask = (df.intervention == r["intervention"]) & \
                   (df.challenge == r["challenge"])
            dfr, clsr = refine_u(r["intervention"], r["challenge"],
                                 r["u_opt"], df[mask])
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
