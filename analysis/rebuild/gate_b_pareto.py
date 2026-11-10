"""Gate B5: three-outcome glycaemic Pareto analysis (hypo burden, hyper burden, glucose SD; all lower-better), configs H and C,
all 50 cases, 21-point grid. Separates frontier membership of the composite optimum from composite-loss improvement and
tests for weight-independent interior optima (an interior u that Pareto-dominates both u=0 and u=1)."""
import pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
AX = ["hypo_burden_mgdl_min", "hyper_burden_mgdl_min", "glucose_sd_mgdl"]
TOL = 1e-6


def dominates(a, b):
    return bool(np.all(a <= b + TOL) and np.any(a < b - TOL))


def main():
    ep = pd.read_csv(ROOT / "results/rebuild/gate_a/corrected_scan_endpoints.csv")
    cl = pd.read_csv(ROOT / "results/rebuild/gate_a/GATE_A_CORRECTED_50_CASES.csv")
    rows = []
    for (cfg, iv, ch), d in ep[ep.config.isin(["H", "C"])].groupby(["config", "intervention", "challenge"]):
        d = d.sort_values("u").reset_index(drop=True)
        P = d[AX].to_numpy(); us = d.u.values
        front = [i for i in range(len(P)) if not any(dominates(P[j], P[i]) for j in range(len(P)) if j != i)]
        c = cl[(cl.config == cfg) & (cl.intervention == iv) & (cl.challenge == ch)].iloc[0]
        s = int(np.argmin(np.abs(us - c.u_opt)))
        dom_both = [us[i] for i in range(1, len(P) - 1) if dominates(P[i], P[0]) and dominates(P[i], P[-1])]
        rows.append(dict(config=cfg, intervention=iv, challenge=ch, response_class=c.response_class, u_opt=c.u_opt,
                         frontier_size=len(front), frontier_u=";".join(f"{us[i]:.2f}" for i in front),
                         u0_on_frontier=0 in front, u1_on_frontier=len(P) - 1 in front, uopt_on_frontier=s in front,
                         uopt_dominates_u0=dominates(P[s], P[0]), uopt_dominates_u1=dominates(P[s], P[-1]),
                         n_interior_dominating_both_ends=len(dom_both),
                         interior_dominating_both_ends_u=";".join(f"{u:.2f}" for u in dom_both)))
    df = pd.DataFrame(rows)
    out = ROOT / "results/rebuild/gate_b"; df.to_csv(out / "GATE_B_PARETO.csv", index=False)
    pd.set_option("display.width", 250)
    t2 = df[df.response_class.isin(["TypeII", "TypeII*"])]
    print(t2.drop(columns=["frontier_u"]).to_string(index=False))
    print("\ncases with an interior point dominating both ends (weight-independent):")
    print(df[df.n_interior_dominating_both_ends > 0][["config", "intervention", "challenge", "response_class", "interior_dominating_both_ends_u"]].to_string(index=False))


if __name__ == "__main__":
    main()
