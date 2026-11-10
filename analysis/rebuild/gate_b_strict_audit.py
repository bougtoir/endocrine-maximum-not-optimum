"""Gate B4: strict Type II audit. For the original four Type II cases and every strict Type II case of the corrected
reference C (configs H and C): grid refinement (0.01 step), solver tolerance (rtol 1e-10, atol 1e-12), optimum location,
absolute / relative improvement over the better endpoint, and near-optimal width (u-range within the classification
tolerance eps = 0.02*max|L(0)|,|L(1)| of the minimum)."""
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
from gate_a_corrected_scan import CONFIGS, GI
from gate_a_reference_sims import SORENSEN_IV_SECRETION

ORIGINAL = [("insulin_signal_global_inhibition", "ivgtt"), ("insulin_secretion_inhibition", "ivgtt"),
            ("glucagon_secretion_inhibition", "ogtt"), ("insulin_secretion", "civii")]
FINE = np.round(np.arange(0, 1.0001, 0.01), 2)
_SIM = sm.simulate


def curve(cfg, ivn, ch, grid, tight):
    sm.simulate = (lambda *a, **k: _SIM(*a, **{**k, "rtol": 1e-10, "atol": 1e-12})) if tight else _SIM
    sec_fix, obs = CONFIGS[cfg]
    extra = dict(SORENSEN_IV_SECRETION) if (sec_fix and ch != "ogtt") else None
    rows = []
    for u in grid:
        t, Y = run_challenge(ch, float(u), INTERVENTIONS[ivn], extra_params=extra)
        Y = np.array(Y, copy=True); Y[GI] *= obs
        ep = endpoint_values(t, Y); ep["composite_loss"] = composite_loss(ep); ep["u"] = float(u)
        rows.append(ep)
    sm.simulate = _SIM
    return pd.DataFrame(rows)


def summarise(d):
    us, L = d.u.values, d.composite_loss.values
    lab, u_opt, _ = classify_response(us, L)
    L0, L1, Lo = L[0], L[-1], L.min()
    eps = 0.02 * max(abs(L0), abs(L1))
    near = us[L <= Lo + eps]
    best_end = min(L0, L1)
    return dict(response_class=lab, u_opt=u_opt, loss_baseline=L0, loss_opt=Lo, loss_max=L1,
                abs_gain_vs_best_end=best_end - Lo, rel_gain_vs_best_end=(best_end - Lo) / best_end if best_end > 0 else np.nan,
                near_opt_u_min=near.min(), near_opt_u_max=near.max(), near_opt_width=near.max() - near.min(),
                near_opt_band_touches_endpoint=bool(near.min() == 0.0 or near.max() == 1.0))


def job(args):
    cfg, ivn, ch = args
    out = []
    fine = curve(cfg, ivn, ch, FINE, False)
    tight = curve(cfg, ivn, ch, U_GRID, True)
    for lab, d in [("grid21_default", fine[fine.u.isin(np.round(U_GRID, 2))]), ("grid101_default", fine), ("grid21_tight", tight)]:
        out.append(dict(config=cfg, intervention=ivn, challenge=ch, original_case=(ivn, ch) in ORIGINAL, variant=lab, **summarise(d)))
    fine.assign(config=cfg, intervention=ivn, challenge=ch).to_csv(
        ROOT / f"results/rebuild/gate_b/fine_curves/{cfg}__{ivn}__{ch}.csv", index=False)
    return out


def main():
    (ROOT / "results/rebuild/gate_b/fine_curves").mkdir(parents=True, exist_ok=True)
    cl = pd.read_csv(ROOT / "results/rebuild/gate_a/GATE_A_CORRECTED_50_CASES.csv")
    cases = sorted(set(ORIGINAL) | set(map(tuple, cl[(cl.config == "C") & (cl.response_class == "TypeII")][["intervention", "challenge"]].values)))
    jobs = [(c, i, ch) for c in ["H", "C"] for i, ch in cases]
    with Pool(2) as p:
        res = sum(p.map(job, jobs, chunksize=1), [])
    df = pd.DataFrame(res)
    df.to_csv(ROOT / "results/rebuild/gate_b/GATE_B_STRICT_TYPEII_AUDIT.csv", index=False)
    pd.set_option("display.width", 250)
    print(df[["config", "intervention", "challenge", "variant", "response_class", "u_opt", "loss_opt",
              "rel_gain_vs_best_end", "near_opt_u_min", "near_opt_u_max", "near_opt_band_touches_endpoint"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
