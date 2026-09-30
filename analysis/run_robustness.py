"""Robustness & sensitivity analyses.

1. Weight sensitivity: scale each loss-term family x{0.5, 2} and reclassify.
2. Endpoint-set sensitivity: drop each term entirely.
3. Grid-density check: step 0.10 vs 0.05 vs 0.025 on key cases.
4. Solver tolerance: rtol 1e-5 vs 1e-7 on representative cases.
5. Classification threshold: rel_thresh 1% / 2% / 5%.
Outputs to results/robustness/.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
from scan import sweep, U_GRID
from interventions import INTERVENTIONS
from homeostatic_loss import DEFAULT_WEIGHTS, classify_response
import sorensen_model as sm
from challenges import run_challenge

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "robustness")

CASES = [  # (intervention, challenge) pairs that showed interior optima
    ("insulin_secretion_inhibition", "ivgtt"),
    ("insulin_signal_global_inhibition", "ivgtt"),
    ("glucagon_secretion", "ogtt"),
    ("glucagon_signal_inhibition", "ogtt"),
    ("glucagon_secretion_inhibition", "ogtt"),
    ("glucagon_signal_hepatic", "ogtt"),
]

TERM_GROUPS = {  # loss-term families for weight perturbation
    "glucose_band": ["hypo_burden_mgdl_min", "hyper_burden_mgdl_min"],
    "variability": ["glucose_sd_mgdl", "glucose_rmsd_mgdl"],
    "dynamics": ["recovery_time_min", "undershoot_mgdl"],
    "endocrine": ["insulin_auc_muL_min", "glucagon_auc_pM_min"],
}


def reclassify(df, weights):
    losses = df.apply(lambda r: sum(
        weights.get(k, 0.0) * r[k] / __import__("homeostatic_loss").NORM[k]
        for k in weights if np.isfinite(r.get(k, np.nan))), axis=1).values
    lab, u_opt, info = classify_response(df["modulation_fraction"].values, losses)
    return lab, u_opt, losses


def main():
    os.makedirs(OUT, exist_ok=True)
    grids = {ivn: {} for ivn, _ in CASES}
    for ivn, ch in CASES:
        df, _ = sweep(ivn, ch)
        grids[ivn][ch] = df

    # 1+2: weight scale / drop
    rows = []
    for ivn, ch in CASES:
        df = grids[ivn][ch]
        lab, u_opt, _ = reclassify(df, DEFAULT_WEIGHTS)
        rows.append(dict(intervention=ivn, challenge=ch, perturbation="default",
                         response_class=lab, u_opt=u_opt))
        for gname, keys in TERM_GROUPS.items():
            for fac in (0.5, 2.0):
                w = dict(DEFAULT_WEIGHTS)
                for k in keys: w[k] = w.get(k, 0) * fac
                lab, u_opt, _ = reclassify(df, w)
                rows.append(dict(intervention=ivn, challenge=ch,
                                 perturbation=f"{gname}x{fac}",
                                 response_class=lab, u_opt=u_opt))
            w = dict(DEFAULT_WEIGHTS)
            for k in keys: w[k] = 0.0
            lab, u_opt, _ = reclassify(df, w)
            rows.append(dict(intervention=ivn, challenge=ch,
                             perturbation=f"{gname}=0",
                             response_class=lab, u_opt=u_opt))
    ws = pd.DataFrame(rows)
    ws.to_csv(f"{OUT}/weight_sensitivity.csv", index=False)
    print("=== weight/endpoint sensitivity ===")
    print(ws.to_string())

    # 3: grid density
    rows = []
    for ivn, ch in CASES[:3]:
        for step in (0.10, 0.05, 0.025):
            g = np.arange(0, 1 + step / 2, step)
            df, cls = sweep(ivn, ch, u_grid=g)
            rows.append(dict(intervention=ivn, challenge=ch, step=step,
                             response_class=cls["response_class"],
                             u_opt=cls["u_opt"]))
    gd = pd.DataFrame(rows); gd.to_csv(f"{OUT}/grid_density.csv", index=False)
    print(gd.to_string())

    # 4: solver tolerance (direct simulate calls at two tolerances)
    rows = []
    for ivn, ch in CASES[:3]:
        chd = __import__("challenges").CHALLENGES[ch]
        for rtol in (1e-5, 1e-7):
            losses = []
            for u in (0.0, 0.3, 0.5, 0.7, 1.0):
                t, Y = sm.simulate(params=chd["params"],
                                   mods=INTERVENTIONS[ivn].mods(u),
                                   t_span=chd["t_span"],
                                   oral_dose_mmol=chd.get("oral_dose_mmol"),
                                   dose_time=chd.get("dose_time", 0.0),
                                   rtol=rtol)
                from endpoints import endpoint_values
                from homeostatic_loss import composite_loss
                losses.append(composite_loss(endpoint_values(t, Y), DEFAULT_WEIGHTS))
            rows.append(dict(intervention=ivn, challenge=ch, rtol=rtol,
                             losses=";".join(f"{x:.4f}" for x in losses)))
    tol = pd.DataFrame(rows); tol.to_csv(f"{OUT}/solver_tolerance.csv", index=False)
    print(tol.to_string())

    # 5: classification threshold
    rows = []
    for ivn, ch in CASES:
        df = grids[ivn][ch]
        for rt in (0.01, 0.02, 0.05):
            lab, u_opt, _ = classify_response(
                df["modulation_fraction"].values, df["composite_loss"].values,
                rel_thresh=rt)
            rows.append(dict(intervention=ivn, challenge=ch, rel_thresh=rt,
                             response_class=lab, u_opt=u_opt))
    ct = pd.DataFrame(rows); ct.to_csv(f"{OUT}/classification_threshold.csv", index=False)
    print(ct.to_string())


if __name__ == "__main__":
    main()
