"""Gate C1: intervention action/flux audit, re-equilibration, clipping frequency,
basal-state alternatives (configuration C). Outputs to results/rebuild/gate_c/."""
import numpy as np, pandas as pd
from multiprocessing import Pool
import gate_c_common as G

IVS = list(G.INTERVENTIONS)
FLUX = ["Secr", "GammaPIR", "GammaPCR", "GammaPGU", "GammaHGP", "GammaHGU", "MIPGU", "MIHGPinf", "MCHGP", "MIHGUinf"]
MULT = {"MIPGU": "insulin_pgu", "MIHGPinf": "insulin_hgp", "MCHGP": "glucagon_hgp", "MIHGUinf": "insulin_hgu"}


def flux_at_start(ivn, u, ch):
    """Instantaneous effect at t=-30 (basal state) of switching on the intervention."""
    d = G.full_params(ch); y = G.sm.initial_state(d)
    a0 = G.sm.algebraics(y, d, None); a1 = G.sm.algebraics(y, d, G.INTERVENTIONS[ivn].mods(u))
    return {f"{k}_ratio_t-30": (a1[k] / a0[k] if a0[k] else np.nan) for k in FLUX}


def reequilibrate(ivn, u, ch):
    """Long fasting hold (5000 min) with intervention on, protocol-specific parameters."""
    d = G.protocol_params(ch)
    t, Y = G.sm.simulate(params=d, mods=G.INTERVENTIONS[ivn].mods(u), t_span=(-30.0, 5000.0))
    G._EVALS += 1
    gi, ii, ci = G.sm.STATE_INDEX["GlucPV"], G.sm.STATE_INDEX["InsuPV"], G.sm.STATE_INDEX["Cgon"]
    k0 = np.searchsorted(t, 0.0)
    return dict(G_pre=Y[gi, 0] * G.PLASMA * G.MMOL_TO_MGDL,
                G_t0=np.interp(0.0, t, Y[gi]) * G.PLASMA * G.MMOL_TO_MGDL,
                G_ss=Y[gi, -1] * G.PLASMA * G.MMOL_TO_MGDL,
                I_pre=Y[ii, 0] * G.PM_TO_MU_L, I_t0=np.interp(0.0, t, Y[ii]) * G.PM_TO_MU_L,
                I_ss=Y[ii, -1] * G.PM_TO_MU_L,
                C_pre=Y[ci, 0], C_t0=np.interp(0.0, t, Y[ci]), C_ss=Y[ci, -1])


def part_a():
    rows = []
    for ivn in IVS:
        for u in (0.0, 0.5, 1.0):
            for ch, lab in (("fasting", "IV-secretion params"), ("ogtt", "oral-refit params")):
                r = dict(intervention=ivn, u=u, factor=G.INTERVENTIONS[ivn].factor(u), param_set=lab)
                r.update(flux_at_start(ivn, u, ch)); r.update(reequilibrate(ivn, u, ch))
                rows.append(r)
    return pd.DataFrame(rows)


def clip_case(args):
    ivn, ch = args
    rows = []
    for u in G.U_GRID:
        mods = G.INTERVENTIONS[ivn].mods(float(u))
        t, Y, Yo = G.run(ch, mods)
        tu, Yu, a = G.flux_traces(t, Y, ch, mods, t0=-30.0)
        d = G.full_params(ch)
        r = dict(intervention=ivn, challenge=ch, u=float(u))
        any_clip = np.zeros(len(tu), bool)
        for M, key in MULT.items():
            s = mods.get(key, 1.0)
            # recompute raw multiplier from effective value when not clipped
            eff = a[M]
            clipped = eff <= G.CLIP + 1e-12
            if M in ("MIPGU", "MIHGPinf", "MIHGUinf", "MCHGP") and s == 1.0:
                clipped = clipped & False if eff.min() > G.CLIP else clipped
            any_clip |= clipped
            r[f"{M}_frac_clipped"] = float(clipped.mean())
            r[f"{M}_min_eff"] = float(eff.min()); r[f"{M}_max_eff"] = float(eff.max())
        r["any_clipped_frac"] = float(any_clip.mean())
        r["any_clipped_frac_t>=0"] = float(any_clip[tu >= 0].mean())
        rows.append(r)
    return rows


def basal_alternatives():
    """Alternative basal starting states (inputs GlucH0, InsuPV0, Cgon0) for IVITT/CIVII,
    insulin_secretion_inhibition curve and baseline direct outcomes."""
    base = G.sm.BASE_PARAMS
    alts = {
        "B0_reference": {},
        "B1_plasma_glucose_90": {"GlucH0": base["GlucH0"] * 90.0 / 82.40},
        "B2_insulin_0.7x": {"InsuPV0": base["InsuPV0"] * 0.7},
        "B3_insulin_1.3x": {"InsuPV0": base["InsuPV0"] * 1.3},
        "B4_glucagon_0.7x": {"Cgon0": base["Cgon0"] * 0.7},
        "B5_glucagon_1.3x": {"Cgon0": base["Cgon0"] * 1.3},
    }
    rows = []
    for an, ov in alts.items():
        d = G.full_params("civii", overrides=ov)
        resid = float(np.abs(G.sm.rhs(-30.0, G.sm.initial_state(d), d)).max())
        for ch in ("ivitt", "civii", "ogtt"):
            for ivn in ("insulin_secretion_inhibition", "insulin_secretion", "glucagon_secretion_inhibition"):
                curve = []
                for u in G.U_GRID:
                    t, Y, Yo = G.run_iv(ivn, u, ch, overrides=ov)
                    ep = G.loss_row(t, Yo); do = G.direct_outcomes(t, Yo)
                    curve.append(ep["composite_loss"])
                    if u in (0.0, 1.0) or abs(u - 0.5) < 1e-9:
                        rows.append(dict(basal_alt=an, steady_state_resid=resid, challenge=ch, intervention=ivn,
                                         u=float(u), composite_loss=ep["composite_loss"], **do))
                lab, uo, info = G.classify_response(G.U_GRID, np.array(curve))
                rows.append(dict(basal_alt=an, steady_state_resid=resid, challenge=ch, intervention=ivn,
                                 u=np.nan, response_class=lab, u_opt=uo))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    B = G.Budget("gate_c1_audit", 1500)
    B.check(10 * 3 * 2 + 50 * 11 + 6 * 3 * 3 * 11)
    A = part_a(); A.to_csv(G.OUT / "C1_INTERVENTION_FLUX_AND_REEQUILIBRATION.csv", index=False)
    with Pool(2) as p:
        res = p.map(clip_case, [(i, c) for i in IVS for c in G.CHALLENGES5], chunksize=1)
    clip = pd.DataFrame([r for rr in res for r in rr]); n_clip = len(clip)
    Bs = basal_alternatives(); Bs.to_csv(G.OUT / "C1_BASAL_STATE_ALTERNATIVES.csv", index=False)
    clip.to_csv(G.OUT / "C1_CLIPPING_AND_INTERVENTION_SENSITIVITY.csv", index=False)
    B.close(G._EVALS - B.e0 + n_clip)
    print(clip.groupby(["intervention"])[["any_clipped_frac_t>=0"]].max())
    print(Bs[Bs.u.isna()][["basal_alt", "challenge", "intervention", "response_class", "u_opt"]].to_string(index=False))
