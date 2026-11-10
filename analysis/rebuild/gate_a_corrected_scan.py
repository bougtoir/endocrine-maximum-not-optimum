"""Gate A5: rerun the 10 x 5 scan under the pre-specified configurations H/S/O/C
(docs/rebuild/GATE_A_CORRECTION_PRESPEC.md)."""
import sys, pathlib
from multiprocessing import Pool
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "analysis/rebuild"))
import sorensen_model as sm
from challenges import run_challenge
from endpoints import endpoint_values
from homeostatic_loss import composite_loss, classify_response
from interventions import INTERVENTIONS
from scan import U_GRID
from gate_a_reference_sims import SORENSEN_IV_SECRETION

CHALLENGES5 = ["fasting", "ivgtt", "ogtt", "ivitt", "civii"]
PLASMA = 0.925
CONFIGS = {"H": (False, 1.0), "S": (True, 1.0), "O": (False, PLASMA), "C": (True, PLASMA)}
# exploratory sensitivity (not pre-specified as primary): whole-blood scale 0.84 against the same thresholds
SENSITIVITY = {"CB": (True, 0.84)}
CONFIGS.update(SENSITIVITY)
GI = sm.STATE_INDEX["GlucPV"]


def case(args):
    cfg, ivn, ch = args
    sec_fix, obs = CONFIGS[cfg]
    extra = dict(SORENSEN_IV_SECRETION) if (sec_fix and ch != "ogtt") else None
    iv = INTERVENTIONS[ivn]
    rows = []
    for u in U_GRID:
        t, Y = run_challenge(ch, float(u), iv, extra_params=extra)
        Y = np.array(Y, copy=True); Y[GI] *= obs
        ep = endpoint_values(t, Y); ep["composite_loss"] = composite_loss(ep)
        rows.append(dict(config=cfg, intervention=ivn, challenge=ch, u=float(u), **ep))
    df = pd.DataFrame(rows)
    lab, u_opt, info = classify_response(df.u.values, df.composite_loss.values)
    cls = dict(config=cfg, intervention=ivn, challenge=ch, response_class=lab, u_opt=u_opt,
               loss_baseline=df.composite_loss.iloc[0], loss_opt=df.composite_loss.min(),
               loss_max=df.composite_loss.iloc[-1], **info)
    return df, cls


def main():
    out = ROOT / "results/rebuild/gate_a"
    sel = sys.argv[1:] or ["H", "S", "O", "C"]
    jobs = [(c, i, ch) for c in sel for ch in CHALLENGES5 for i in INTERVENTIONS]
    tag = "" if sel == ["H", "S", "O", "C"] else "_" + "_".join(sel)
    with Pool(2) as p:
        res = p.map(case, jobs, chunksize=1)
    pd.concat([r[0] for r in res]).to_csv(out / f"corrected_scan_endpoints{tag}.csv", index=False)
    cl = pd.DataFrame([r[1] for r in res])
    cl.to_csv(out / f"GATE_A_CORRECTED_50_CASES{tag}.csv", index=False)
    print(pd.crosstab(cl.config, cl.response_class))
    print(cl[cl.response_class == "TypeII"][["config", "intervention", "challenge", "u_opt"]].to_string(index=False))


if __name__ == "__main__":
    main()
