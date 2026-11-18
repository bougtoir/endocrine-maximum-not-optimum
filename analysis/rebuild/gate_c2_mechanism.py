"""Gate C2: targeted, pre-specified perturbations for the three corrected-C strict Type II
cases (results/rebuild/gate_c/C2_PRESPEC.md). Exploratory."""
import numpy as np, pandas as pd, pathlib
from multiprocessing import Pool
from scipy.integrate import solve_ivp
import gate_c_common as G
from challenges import CHALLENGES, CIVII_RATE

sm = G.sm
B = sm.BASE_PARAMS
CASES = {"a": ("insulin_secretion", "ogtt"), "b": ("insulin_secretion_inhibition", "civii"),
         "c": ("glucagon_secretion_inhibition", "ogtt")}
STO = sm.STATE_INDEX["Sto"]; GK = sm.STATE_INDEX["GlucK"]
TRAJ = G.OUT / "C2_TRAJECTORY_COMPARISONS"; TRAJ.mkdir(exist_ok=True)


def kpp(ch, k):
    return {"KappaPotnPtgt": G.protocol_params(ch).get("KappaPotnPtgt", B["KappaPotnPtgt"]) * k}


def sorensen_basal_civii(ch):
    d = G.full_params(ch)
    target_gpv = (90.0 / 0.925) / G.MMOL_TO_MGDL
    return {"GlucH0": B["GlucH0"] + (target_gpv - d["GlucPV0"]), "InsuPV0": 11.0 / G.PM_TO_MU_L}


PERT = {
    "A0": dict(),
    "A1_alpha_feedback_clamped": dict(ov=lambda ch: dict(beta0PCR=1.0, beta1PCR=0.0, beta4PCR=1.0, beta5PCR=0.0)),
    "A2_hepatic_glucagon_action_clamped": dict(mods={"glucagon_hgp": 0.0}),
    "A3_hepatic_glucose_autoreg_clamped": dict(ov=lambda ch: dict(beta6HGP=1.0, beta7HGP=0.0, beta2HGU=1.0, beta3HGU=0.0)),
    "A4_hepatic_insulin_action_clamped": dict(mods={"insulin_hgp": 0.0, "insulin_hgu": 0.0}),
    "A5_peripheral_insulin_action_clamped": dict(mods={"insulin_pgu": 0.0}),
    "A6_first_phase_secretion_removed": dict(ov=lambda ch: dict(EMME2=0.0)),
    "A7a_potentiator_fast_x0.5tau": dict(ov=lambda ch: kpp(ch, 2.0)),
    "A7b_potentiator_slow_x2tau": dict(ov=lambda ch: kpp(ch, 0.5)),
    "A8a_insulin_action_delay_x0.5": dict(ov=lambda ch: dict(tauInsu=B["tauInsu"] * 0.5)),
    "A8b_insulin_action_delay_x2": dict(ov=lambda ch: dict(tauInsu=B["tauInsu"] * 2.0)),
    "P1_onset_at_t0": dict(onset=0.0),
    "P3_reequilibrated_start": dict(preeq=True),
    "N1_renal_excretion_ablated": dict(ov=lambda ch: dict(beta4KGE=0.0, beta5KGE=0.0)),
    "N2_brain_uptake_x1.02": dict(ov=lambda ch: dict(GammaBGU=B["GammaBGU"] * 1.02)),
}
EXTRA = {
    "b": {"P2_sorensen_basal_civii": dict(ov=sorensen_basal_civii),
          **{f"C_infusion_x{k}": dict(ov=(lambda k: lambda ch: dict(GammaIVIin=CIVII_RATE * k))(k))
             for k in (0.5, 0.75, 1.25, 1.6)}},
    "a": {"D1_oral_50g": dict(dose=277.78), "D2_oral_75g": dict(dose=416.67)},
    "c": {"D1_oral_50g": dict(dose=277.78), "D2_oral_75g": dict(dose=416.67)},
}


def sim(ch, mods, ov=None, onset=-30.0, preeq=False, dose=None):
    c = CHALLENGES[ch]; d = G.full_params(ch, overrides=ov)
    t0, t1 = c["t_span"]; dose = c.get("oral_dose_mmol") if dose is None else dose
    y = sm.initial_state(d)
    if preeq:
        s = solve_ivp(lambda t, y: sm.rhs(t, y, d, mods), (t0 - 3000.0, t0), y, method="LSODA", rtol=1e-7, atol=1e-9)
        y = s.y[:, -1].copy()
    br = sorted({t0, t1, *(b for b in (onset, 0.0 if dose else None) if b is not None and t0 < b < t1)})
    ts, ys = [], []
    for a, b in zip(br[:-1], br[1:]):
        m = mods if a >= onset - 1e-12 else None
        s = solve_ivp(lambda t, y: sm.rhs(t, y, d, m), (a, b), y, method="LSODA", rtol=1e-7, atol=1e-9)
        if not s.success:
            raise RuntimeError(s.message)
        ts.append(s.t); ys.append(s.y); y = s.y[:, -1].copy()
        if dose and abs(b) < 1e-12:
            y[STO] += dose
    G._EVALS += 1 + int(preeq)
    t = np.concatenate(ts); Y = np.concatenate(ys, axis=1)
    Yo = Y.copy(); Yo[G.GI] *= G.PLASMA
    return t, Y, Yo, d


def fluxes(t, Y, d, mods):
    tu = np.arange(0.0, t[-1] + 1e-9, 0.5)
    Yu = np.vstack([np.interp(tu, t, Y[i]) for i in range(Y.shape[0])])
    rows = [sm.algebraics(Yu[:, k], d, mods) for k in range(len(tu))]
    a = {k: np.array([r[k] for r in rows]) for k in ("GammaPIR", "GammaPCR", "GammaHGP", "GammaHGU", "GammaPGU", "MCHGP", "MIHGP_dummy")
         if k in rows[0]}
    out = {f"auc_{k}": float(np.trapezoid(a[k], tu)) for k in ("GammaPIR", "GammaPCR", "GammaHGP", "GammaHGU", "GammaPGU")}
    out["max_GlucK_mM"] = float(Yu[GK].max())
    return out, tu, Yu, a


def job(args):
    cid, pid = args
    ivn, ch = CASES[cid]
    spec = {**PERT, **EXTRA.get(cid, {})}[pid]
    rows, keep = [], {}
    for u in G.U_GRID:
        mods = G.combine_mods(G.INTERVENTIONS[ivn].mods(float(u)), spec.get("mods"))
        ov = spec["ov"](ch) if "ov" in spec else None
        t, Y, Yo, d = sim(ch, mods, ov, spec.get("onset", -30.0), spec.get("preeq", False), spec.get("dose"))
        ep = G.loss_row(t, Yo); do = G.direct_outcomes(t, Yo)
        fx, tu, Yu, a = fluxes(t, Y, d, mods)
        rows.append(dict(case=cid, intervention=ivn, challenge=ch, perturbation=pid, u=float(u),
                         composite_loss=ep["composite_loss"], **{f"ep_{k}": v for k, v in ep.items() if k != "composite_loss"},
                         **do, **fx))
        keep[round(float(u), 2)] = (tu, Yu, a)
    return rows, (cid, pid, keep)


def nonmono(x):
    x = np.asarray(x, float)
    rise = max(x[j] - x[i] for i in range(len(x)) for j in range(i + 1, len(x)))
    fall = max(x[i] - x[j] for i in range(len(x)) for j in range(i + 1, len(x)))
    return float(min(rise, fall))


DIRECT = ["nadir_mgdl", "peak_mgdl", "min_below70", "min_above140", "hypo70_burden", "hyper140_burden",
          "g0_mgdl", "g_end_mgdl", "last_outside_pre_pm10_min", "ep_recovery_time_min", "ep_undershoot_mgdl",
          "ep_glucose_sd_mgdl", "auc_GammaPIR", "auc_GammaHGP", "auc_GammaPGU"]


def summarise(df):
    out = []
    for (cid, pid), g in df.groupby(["case", "perturbation"], sort=False):
        g = g.sort_values("u"); a0 = df[(df.case == cid) & (df.perturbation == "A0")].sort_values("u")
        lab, uo, info = G.classify_response(g.u.values, g.composite_loss.values)
        r = dict(case=cid, intervention=g.intervention.iloc[0], challenge=g.challenge.iloc[0], perturbation=pid,
                 response_class=lab, u_opt=uo, loss_u0=g.composite_loss.iloc[0], loss_min=g.composite_loss.min(),
                 loss_u1=g.composite_loss.iloc[-1],
                 d_nadir_u0_vs_A0=g.nadir_mgdl.iloc[0] - a0.nadir_mgdl.iloc[0],
                 d_peak_u0_vs_A0=g.peak_mgdl.iloc[0] - a0.peak_mgdl.iloc[0],
                 max_GlucK_mM=g.max_GlucK_mM.max())
        r["comparable_at_u0"] = bool(abs(r["d_nadir_u0_vs_A0"]) <= 2 and abs(r["d_peak_u0_vs_A0"]) <= 5)
        for k in DIRECT:
            r[f"{k}_u0"] = g[k].iloc[0]; r[f"{k}_u1"] = g[k].iloc[-1]; r[f"{k}_nonmono"] = nonmono(g[k].values)
        out.append(r)
    return pd.DataFrame(out)


def figures(keep, summ):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    ii, ci = sm.STATE_INDEX["InsuPV"], sm.STATE_INDEX["Cgon"]
    for cid in CASES:
        uo = float(summ[(summ.case == cid) & (summ.perturbation == "A0")].u_opt.iloc[0])
        fig, ax = plt.subplots(2, 3, figsize=(13, 7))
        recs = []
        for pid, ls in (("A0", "-"), ("P1_onset_at_t0", "--"), ("P3_reequilibrated_start", ":")):
            for u, col in ((0.0, "k"), (round(uo, 2), "tab:blue"), (1.0, "tab:red")):
                tu, Yu, a = keep[(cid, pid)][u]
                g = Yu[G.GI] * G.PLASMA * G.MMOL_TO_MGDL
                lab = f"{pid.split('_')[0]} u={u:g}"
                for k, (y, nm) in enumerate(((g, "plasma glucose (mg/dL)"), (Yu[ii] * G.PM_TO_MU_L, "insulin (mU/L)"),
                                              (Yu[ci], "glucagon (pM)"), (a["GammaHGP"], "HGP (mmol/min)"),
                                              (a["GammaPGU"], "peripheral uptake (mmol/min)"), (a["GammaPIR"], "insulin secretion (pmol/min)"))):
                    axx = ax.flat[k]; axx.plot(tu, y, ls=ls, color=col, lw=1.2, label=lab if k == 0 else None); axx.set_title(nm, fontsize=9)
                recs.append(pd.DataFrame(dict(perturbation=pid, u=u, t_min=tu, plasma_glucose_mgdl=g,
                                              insulin_muL=Yu[ii] * G.PM_TO_MU_L, glucagon_pM=Yu[ci],
                                              HGP=a["GammaHGP"], PGU=a["GammaPGU"], insulin_secretion=a["GammaPIR"],
                                              glucagon_secretion=a["GammaPCR"])))
        for axx in ax.flat:
            axx.set_xlabel("min")
        ax.flat[0].axhline(70, color="grey", lw=0.6); ax.flat[0].axhline(140, color="grey", lw=0.6)
        ax.flat[0].legend(fontsize=6, ncol=1)
        ivn, ch = CASES[cid]
        fig.suptitle(f"case {cid}: {ivn} x {ch.upper()} (config C) — solid A0, dashed P1 onset t=0, dotted P3 re-equilibrated", fontsize=10)
        fig.tight_layout(); fig.savefig(TRAJ / f"case_{cid}_{ivn}_{ch}.png", dpi=130); plt.close(fig)
        pd.concat(recs)[lambda x: x.t_min % 1 == 0].to_csv(TRAJ / f"case_{cid}_{ivn}_{ch}.csv", index=False)


if __name__ == "__main__":
    Bd = G.Budget("gate_c2_mechanism", 2000)
    jobs = [(c, p) for c in CASES for p in {**PERT, **EXTRA.get(c, {})}]
    Bd.check(len(jobs) * len(G.U_GRID) + 3 * len(G.U_GRID))
    # equivalence check: custom integrator vs historical run_challenge path
    for cid, (ivn, ch) in CASES.items():
        t1, _, Yo1 = G.run_iv(ivn, 0.5, ch); t2, _, Yo2, _ = sim(ch, G.INTERVENTIONS[ivn].mods(0.5))
        g1 = np.interp(np.arange(0, 300, 1.0), t1, Yo1[G.GI]); g2 = np.interp(np.arange(0, 300, 1.0), t2, Yo2[G.GI])
        print(cid, "max |dG| custom vs run_challenge (mg/dL):", float(np.abs(g1 - g2).max() * G.MMOL_TO_MGDL))
    with Pool(2) as p:
        res = p.map(job, jobs, chunksize=1)
    df = pd.DataFrame([r for rr, _ in res for r in rr])
    keep = {(c, pid): k for _, (c, pid, k) in res}
    df.to_csv(G.OUT / "C2_TARGETED_ABLATIONS.csv", index=False)
    summ = summarise(df); summ.to_csv(G.OUT / "C2_TARGETED_ABLATIONS_SUMMARY.csv", index=False)
    figures(keep, summ)
    Bd.close(len(jobs) * len(G.U_GRID) + 3 * len(G.U_GRID) + 6)
    pd.set_option("display.width", 250)
    print(summ[["case", "perturbation", "response_class", "u_opt", "comparable_at_u0", "d_nadir_u0_vs_A0",
                "nadir_mgdl_u0", "nadir_mgdl_u1", "nadir_mgdl_nonmono", "peak_mgdl_u0", "peak_mgdl_u1", "peak_mgdl_nonmono",
                "hypo70_burden_nonmono", "hyper140_burden_nonmono", "max_GlucK_mM"]].round(2).to_string(index=False))
