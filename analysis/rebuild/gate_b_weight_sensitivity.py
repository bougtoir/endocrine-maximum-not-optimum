"""Gate B3: predefined objective-weight / normalisation / risk-formulation sensitivity, recomputed from the
simulated endpoints (corrected_scan_endpoints.csv; configs H and C; 50 cases; 21-point grid). Sets fixed before running."""
import sys, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from homeostatic_loss import DEFAULT_WEIGHTS, NORM, classify_response

W0 = dict(DEFAULT_WEIGHTS)
def mod(**kw):
    w = dict(W0); w.update(kw); return w
NZ = [k for k, v in W0.items() if v > 0]
SETS = {
    "W0_original": (W0, "fixed"),
    "W1_no_exposure": (mod(insulin_auc_muL_min=0.0, glucagon_auc_pM_min=0.0), "fixed"),
    "W2_glycemic_risk_x3": (mod(hypo_burden_mgdl_min=30.0, hyper_burden_mgdl_min=15.0), "fixed"),
    "W3_hypo_x3": (mod(hypo_burden_mgdl_min=30.0), "fixed"),
    "W4_burden_only": (mod(glucose_sd_mgdl=0.0, glucose_rmsd_mgdl=0.0), "fixed"),
    "W5_equal_normalised": ({k: (1.0 if k in NZ else 0.0) for k in W0}, "fixed"),
    "W6_target_deviation_risk": (mod(glucose_sd_mgdl=0.0, glucose_rmsd_mgdl=0.0, abs_dev_from_target_mgdl_min=10.0), "fixed"),
    "W7_baseline_normalised": (W0, "baseline"),
}
ORIGINAL = {("insulin_signal_global_inhibition", "ivgtt"), ("insulin_secretion_inhibition", "ivgtt"),
            ("glucagon_secretion_inhibition", "ogtt"), ("insulin_secretion", "civii")}


def loss(df, w, norm_mode):
    tot = np.zeros(len(df))
    for k, wk in w.items():
        if wk == 0: continue
        if norm_mode == "fixed":
            n = NORM[k]
        else:
            b = df[df.u == 0.0][k].iloc[0]
            n = max(abs(b), NORM[k] / 100.0)
        tot += wk * df[k].values / n
    return tot


def main():
    ep = pd.read_csv(ROOT / "results/rebuild/gate_a/corrected_scan_endpoints.csv")
    rows = []
    for (cfg, iv, ch), d in ep[ep.config.isin(["H", "C"])].groupby(["config", "intervention", "challenge"]):
        d = d.sort_values("u")
        for name, (w, nm) in SETS.items():
            L = loss(d, w, nm)
            lab, u_opt, info = classify_response(d.u.values, L)
            rows.append(dict(config=cfg, intervention=iv, challenge=ch, weight_set=name, response_class=lab,
                             u_opt=u_opt, loss_baseline=L[0], loss_opt=L.min(), loss_max=L[-1],
                             original_type_ii=(iv, ch) in ORIGINAL))
    df = pd.DataFrame(rows)
    out = ROOT / "results/rebuild/gate_b"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "GATE_B_WEIGHT_SENSITIVITY.csv", index=False)
    s = df.assign(t2=df.response_class == "TypeII").groupby(["config", "weight_set"]).agg(
        n_strict_typeII=("t2", "sum"), n_typeII_star=("response_class", lambda x: (x == "TypeII*").sum()))
    c_ref = set(map(tuple, df[(df.config == "C") & (df.weight_set == "W0_original") & (df.response_class == "TypeII")][["intervention", "challenge"]].values))
    for (cfg, ws), g in df.groupby(["config", "weight_set"]):
        t2 = set(map(tuple, g[g.response_class == "TypeII"][["intervention", "challenge"]].values))
        s.loc[(cfg, ws), "original4_retained"] = len(t2 & ORIGINAL)
        s.loc[(cfg, ws), "C_W0_cases_retained"] = len(t2 & c_ref)
        s.loc[(cfg, ws), "typeII_cases"] = "; ".join(f"{a}@{b}" for a, b in sorted(t2))
    s.reset_index().to_csv(out / "GATE_B_WEIGHT_SENSITIVITY_SUMMARY.csv", index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 140)
    print(s.to_string())


if __name__ == "__main__":
    main()
