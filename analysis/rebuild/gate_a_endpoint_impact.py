"""Gate A6: effect of the confirmed discrepancies on baseline (u=0, no intervention) endpoints and loss,
including time below 70 / above 140 mg/dL, per challenge and configuration H/S/O/C/CB."""
import sys, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "analysis/rebuild"))
import sorensen_model as sm
from challenges import run_challenge
from endpoints import endpoint_values, MMOL_TO_MGDL, GLUCOSE_HYPO_MGDL, GLUCOSE_HYPER_MGDL
from homeostatic_loss import composite_loss
from interventions import INTERVENTIONS
from gate_a_corrected_scan import CONFIGS, CHALLENGES5, GI
from gate_a_reference_sims import SORENSEN_IV_SECRETION

iv = INTERVENTIONS["insulin_secretion"]  # u=0 -> no modification for every axis
rows = []
for cfg, (sec_fix, obs) in CONFIGS.items():
    for ch in CHALLENGES5:
        extra = dict(SORENSEN_IV_SECRETION) if (sec_fix and ch != "ogtt") else None
        t, Y = run_challenge(ch, 0.0, iv, extra_params=extra)
        Y = np.array(Y, copy=True); Y[GI] *= obs
        ep = endpoint_values(t, Y); ep["composite_loss"] = composite_loss(ep)
        tu = np.arange(0.0, t[-1] + 1e-9, 0.5); g = np.interp(tu, t, Y[GI]) * MMOL_TO_MGDL
        ep["time_below_70_min"] = 0.5 * float((g < GLUCOSE_HYPO_MGDL).sum())
        ep["time_above_140_min"] = 0.5 * float((g > GLUCOSE_HYPER_MGDL).sum())
        rows.append(dict(config=cfg, challenge=ch, **ep))
df = pd.DataFrame(rows)
df.to_csv(ROOT / "results/rebuild/gate_a/GATE_A_BASELINE_ENDPOINT_IMPACT.csv", index=False)
cols = ["config", "challenge", "glucose_nadir_mgdl", "glucose_peak_mgdl", "time_below_70_min", "time_above_140_min",
        "hypo_burden_mgdl_min", "hyper_burden_mgdl_min", "recovery_time_min", "insulin_auc_muL_min", "composite_loss"]
print(df[cols].round(1).to_string(index=False))
