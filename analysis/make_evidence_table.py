"""Type II evidence table: per-case weight-independent (Pareto) support and
stability status for all strict Type II intervention-challenge combinations."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd

R = os.path.join(os.path.dirname(__file__), "..", "results")
T = os.path.join(R, "tables")
os.makedirs(T, exist_ok=True)

fc = pd.read_csv(f"{R}/scans/full_classification.csv")
ep = pd.concat([pd.read_csv(f"{R}/scans/full_endpoints.csv"),
                pd.read_csv(f"{R}/scans/refined_endpoints.csv")],
               ignore_index=True)
rc = pd.read_csv(f"{R}/scans/refined_classification.csv")
ws = pd.read_csv(f"{R}/robustness/weight_sensitivity.csv")
gd = pd.read_csv(f"{R}/robustness/grid_density.csv")
st = pd.read_csv(f"{R}/robustness/solver_tolerance.csv")
dis = pd.read_csv(f"{R}/disease/disease_classification.csv")

II = fc[fc.response_class == "TypeII"]

def epv(ivn, ch, u, col):
    row = ep[(ep.intervention == ivn) & (ep.challenge == ch)
             & (np.isclose(ep.modulation_fraction, u))]
    if not len(row):
        row = ep[(ep.intervention == ivn) & (ep.challenge == ch)]
        row = row.iloc[(row.modulation_fraction - u).abs().idxmin()]
        return row[col]
    return row.iloc[0][col]

def ustar(ivn, ch):
    r = rc[(rc.intervention == ivn) & (rc.challenge == ch)]
    return float(r.u_opt.iloc[0]) if len(r) else \
        float(fc[(fc.intervention == ivn) & (fc.challenge == ch)].u_opt.iloc[0])

rows = []
for _, r in II.iterrows():
    ivn, ch = r.intervention, r.challenge
    u = ustar(ivn, ch)
    h0, hs, h1 = (epv(ivn, ch, x, "hypo_burden_mgdl_min") for x in (0, u, 1))
    p0, ps, p1 = (epv(ivn, ch, x, "hyper_burden_mgdl_min") for x in (0, u, 1))
    sd0, sds, sd1 = (epv(ivn, ch, x, "glucose_sd_mgdl") for x in (0, u, 1))
    L0, Ls, L1 = (epv(ivn, ch, x, "composite_loss") for x in (0, u, 1))
    dom0 = hs <= h0 and ps <= p0 and (hs < h0 or ps < p0)
    dom1 = hs <= h1 and ps <= p1 and (hs < h1 or ps < p1)
    # frontier membership on glycaemic axes (all lower-better)
    sub = ep[(ep.intervention == ivn) & (ep.challenge == ch)]
    P = sub[["hypo_burden_mgdl_min", "hyper_burden_mgdl_min",
             "glucose_sd_mgdl"]].to_numpy()
    si = int((sub.modulation_fraction - u).abs().argmin())
    pt = P[si]
    dominated = ((P <= pt).all(1) & (P < pt).any(1)).any()
    parts = []
    if dom0: parts.append("dominates u=0")
    if dom1: parts.append("dominates u=1")
    if not parts: parts.append("trade-off vs endpoints")
    pareto = "; ".join(parts) + ("; dominated (endpoint-dependent)" if dominated
                                 else "; on frontier")
    g = gd[(gd.intervention == ivn) & (gd.challenge == ch)]
    grid = ("+".join(sorted(set(g.response_class)))
            + f" (u* {g.u_opt.min():.2f}-{g.u_opt.max():.2f})") if len(g) else "n/a"
    w = ws[(ws.intervention == ivn) & (ws.challenge == ch) & (ws.perturbation != "default")]
    wfrac = 100 * w.response_class.isin(["TypeII", "TypeII*"]).mean() if len(w) else np.nan
    s = st[(st.intervention == ivn) & (st.challenge == ch)]
    drep = dis[(dis.intervention == ivn) & (dis.challenge == ch)
               & (dis.response_class.isin(["TypeII", "TypeII*"]))]
    dstr = "; ".join(f"{s2}:u*={u2:.2f}" for s2, u2 in zip(drep.state, drep.u_opt)) or "-"
    rows.append(dict(
        intervention=ivn, challenge=ch, u_star=round(u, 2),
        loss_u0=round(L0, 2), loss_ustar=round(Ls, 2), loss_u1=round(L1, 2),
        hypo_u0=round(h0, 1), hypo_ustar=round(hs, 1), hypo_u1=round(h1, 1),
        hyper_u0=round(p0, 1), hyper_ustar=round(ps, 1), hyper_u1=round(p1, 1),
        nadir_ustar=round(epv(ivn, ch, u, "glucose_nadir_mgdl"), 1),
        peak_ustar=round(epv(ivn, ch, u, "glucose_peak_mgdl"), 1),
        insulin_auc_ustar=round(epv(ivn, ch, u, "insulin_auc_muL_min"), 0),
        pareto_status=pareto,
        grid_stability=grid,
        solver_stable="yes" if len(s) else "n/a",
        weight_sensitivity=(f"{wfrac:.0f}% keep TypeII/II*" if len(w) else "not covered"),
        disease_replication=dstr,
    ))

tb = pd.DataFrame(rows)
tb.to_csv(f"{T}/table3_typeII_evidence.csv", index=False)
print(tb[["intervention", "challenge", "u_star", "pareto_status",
          "weight_sensitivity", "disease_replication"]].to_string(index=False))
