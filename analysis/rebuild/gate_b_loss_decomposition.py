"""Gate B2: weighted contribution of every endpoint at u=0, u*, u=1 for the original four Type II cases and all
strict Type II cases of the corrected reference (C), under configs H and C. Uses corrected_scan_endpoints.csv."""
import sys, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from homeostatic_loss import DEFAULT_WEIGHTS, NORM

G = ROOT / "results/rebuild/gate_a"
ORIGINAL = [("insulin_signal_global_inhibition", "ivgtt"), ("insulin_secretion_inhibition", "ivgtt"),
            ("glucagon_secretion_inhibition", "ogtt"), ("insulin_secretion", "civii")]
GLYCEMIC = ["hypo_burden_mgdl_min", "hyper_burden_mgdl_min", "glucose_sd_mgdl", "glucose_rmsd_mgdl",
            "recovery_time_min", "undershoot_mgdl"]
EXPOSURE = ["insulin_auc_muL_min", "glucagon_auc_pM_min"]


def main():
    ep = pd.read_csv(G / "corrected_scan_endpoints.csv")
    cl = pd.read_csv(G / "GATE_A_CORRECTED_50_CASES.csv")
    cases = set(ORIGINAL) | set(map(tuple, cl[(cl.config == "C") & (cl.response_class == "TypeII")][["intervention", "challenge"]].values))
    rows = []
    for cfg in ["H", "C"]:
        for iv, ch in sorted(cases):
            d = ep[(ep.config == cfg) & (ep.intervention == iv) & (ep.challenge == ch)].set_index("u")
            ustar = float(d.composite_loss.idxmin())
            for lab, u in [("baseline_u0", 0.0), ("optimum_ustar", ustar), ("maximum_u1", 1.0)]:
                r = d.loc[u]
                row = dict(config=cfg, intervention=iv, challenge=ch, original_case=(iv, ch) in ORIGINAL,
                           point=lab, u=u, composite_loss=r.composite_loss)
                for k, w in DEFAULT_WEIGHTS.items():
                    row[f"raw__{k}"] = r[k]
                    row[f"contrib__{k}"] = w * r[k] / NORM[k]
                row["glycemic_subtotal"] = sum(row[f"contrib__{k}"] for k in GLYCEMIC)
                row["exposure_subtotal"] = sum(row[f"contrib__{k}"] for k in EXPOSURE)
                rows.append(row)
    df = pd.DataFrame(rows)
    out = ROOT / "results/rebuild/gate_b"; out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "GATE_B_LOSS_DECOMPOSITION.csv", index=False)
    s = ["config", "intervention", "challenge", "point", "u", "composite_loss", "glycemic_subtotal", "exposure_subtotal"] + \
        [f"contrib__{k}" for k in GLYCEMIC + EXPOSURE]
    v = df[s].copy(); v.columns = [c.replace("contrib__", "").replace("_mgdl_min", "").replace("_mgdl", "").replace("_min", "")[:10] for c in s]
    print(v.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
