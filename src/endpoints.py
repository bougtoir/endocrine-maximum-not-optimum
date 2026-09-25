"""Homeostatic endpoints computed from simulated trajectories.

Glucose is measured on GlucPV (peripheral plasma, the clinically sampled
compartment), insulin on InsuPV [pM], glucagon on Cgon [pM].
All endpoint functions take the post-challenge window (t >= 0).

Every endpoint entry in ENDPOINTS carries:
  unit, orientation ('lower' or 'higher'), interpretation.
"""

import numpy as np
import sorensen_model as sm

MMOL_TO_MGDL = 18.016
PM_TO_MU_L = 1.0 / 6.944

GLUCOSE_TARGET_MGDL = 90.0          # mid-normal fasting set-point
GLUCOSE_HYPO_MGDL = 70.0            # standard hypoglycaemia threshold (3.9 mmol/L)
GLUCOSE_HYPER_MGDL = 140.0          # post-challenge hyperglycaemia threshold


def _window(t, Y, t_start=0.0):
    m = t >= t_start
    return t[m], Y[:, m]


def glucose_series(t, Y):
    return Y[sm.STATE_INDEX["GlucPV"]] * MMOL_TO_MGDL


def insulin_series(t, Y):
    return Y[sm.STATE_INDEX["InsuPV"]] * PM_TO_MU_L


def glucagon_series(t, Y):
    return Y[sm.STATE_INDEX["Cgon"]] * 1.0  # pM


def endpoint_values(t, Y, p=None, mods=None, t_start=0.0):
    tw, Yw = _window(t, Y, t_start)
    # Resample to a uniform time grid so endpoint statistics (SD, successive
    # differences) do not depend on the solver's internal step sizes.
    dt_eval = 0.5  # min; fixed across all runs
    tu = np.arange(tw[0], tw[-1] + 1e-9, dt_eval)
    g = np.interp(tu, tw, glucose_series(tw, Yw))
    ins = np.interp(tu, tw, insulin_series(tw, Yw))
    cgn = np.interp(tu, tw, glucagon_series(tw, Yw))
    tw = tu
    dur = tw[-1] - tw[0]

    hypo = np.trapezoid(np.clip(GLUCOSE_HYPO_MGDL - g, 0, None), tw)
    hyper = np.trapezoid(np.clip(g - GLUCOSE_HYPER_MGDL, 0, None), tw)
    dev = np.trapezoid(np.abs(g - GLUCOSE_TARGET_MGDL), tw)
    auc = np.trapezoid(g, tw)
    ins_auc = np.trapezoid(ins, tw)
    cgn_auc = np.trapezoid(cgn, tw)

    peak = g.max(); nadir = g.min()
    base = g[0]
    # recovery time: last time |g - basal| exceeds 10% of the peak excursion;
    # requires a genuine excursion (>0.5 mg/dL) — otherwise the system never
    # left the band and recovery time is 0 by definition.
    exc = max(abs(peak - base), abs(nadir - base))
    rec = 0.0
    if exc > 0.5:
        outside = np.where(np.abs(g - base) > 0.1 * exc)[0]
        rec = tw[outside[-1]] - tw[0] if len(outside) else 0.0
    # overshoot below baseline after challenge
    overshoot = max(0.0, base - nadir)
    # variability: SD of glucose in window + successive-difference RMS
    gsd = g.std()
    diffs = np.diff(g)
    rmsd = np.sqrt(np.mean(diffs**2)) if len(diffs) else 0.0

    return {
        "hypo_burden_mgdl_min": hypo,
        "hyper_burden_mgdl_min": hyper,
        "abs_dev_from_target_mgdl_min": dev,
        "glucose_auc_mgdl_min": auc,
        "glucose_sd_mgdl": gsd,
        "glucose_rmsd_mgdl": rmsd,
        "glucose_peak_mgdl": peak,
        "glucose_nadir_mgdl": nadir,
        "recovery_time_min": rec,
        "undershoot_mgdl": overshoot,
        "insulin_auc_muL_min": ins_auc,
        "glucagon_auc_pM_min": cgn_auc,
        "mean_glucose_mgdl": auc / dur if dur > 0 else np.nan,
        "mean_insulin_muL": ins_auc / dur if dur > 0 else np.nan,
        "mean_glucagon_pM": cgn_auc / dur if dur > 0 else np.nan,
    }


ENDPOINT_META = {
    "hypo_burden_mgdl_min":        ("mg/dL*min", "lower",  "time-integrated exposure below 70 mg/dL"),
    "hyper_burden_mgdl_min":       ("mg/dL*min", "lower",  "time-integrated exposure above 140 mg/dL"),
    "abs_dev_from_target_mgdl_min":("mg/dL*min", "lower",  "integral of |G - 90 mg/dL| over window"),
    "glucose_auc_mgdl_min":        ("mg/dL*min", "lower",  "total glucose exposure"),
    "glucose_sd_mgdl":             ("mg/dL",     "lower",  "glucose standard deviation"),
    "glucose_rmsd_mgdl":           ("mg/dL",     "lower",  "root-mean-square successive difference"),
    "glucose_peak_mgdl":           ("mg/dL",     "lower",  "peak post-challenge glucose"),
    "glucose_nadir_mgdl":          ("mg/dL",     "higher", "lowest glucose reached"),
    "recovery_time_min":           ("min",       "lower",  "time until |G-basal| < 10% of excursion"),
    "undershoot_mgdl":             ("mg/dL",     "lower",  "nadir below basal glucose"),
    "insulin_auc_muL_min":         ("mU/L*min",  "lower",  "insulin exposure (endocrine burden)"),
    "glucagon_auc_pM_min":         ("pM*min",    "lower",  "glucagon exposure (counter-regulatory burden)"),
    "mean_glucose_mgdl":           ("mg/dL",     "lower",  "mean post-challenge glucose"),
    "mean_insulin_muL":            ("mU/L",      "lower",  "mean insulin"),
    "mean_glucagon_pM":            ("pM",        "lower",  "mean glucagon"),
}
