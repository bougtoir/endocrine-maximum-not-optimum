"""Composite homeostatic loss and classification of dose-response shape.

Primary loss (physiologically motivated, per-minute normalised):
    L = w_hypo*hypo + w_hyper*hyper + w_var*variability + w_ins*insulin_auc
         + w_rec*recovery
Weights are explicitly documented and varied in sensitivity analysis.
"""

import numpy as np

# Each term is normalised by a reference scale so weights are comparable.
DEFAULT_WEIGHTS = {
    "hypo_burden_mgdl_min":         10.0,   # hypoglycaemia is most dangerous
    "hyper_burden_mgdl_min":        5.0,
    "abs_dev_from_target_mgdl_min": 0.0,
    "glucose_auc_mgdl_min":         0.0,
    "glucose_sd_mgdl":              5.0,
    "glucose_rmsd_mgdl":            20.0,
    "glucose_peak_mgdl":            0.0,
    "glucose_nadir_mgdl":           0.0,
    "recovery_time_min":            0.5,
    "undershoot_mgdl":              2.0,
    "insulin_auc_muL_min":          0.02,   # endocrine burden
    "glucagon_auc_pM_min":          0.002,
    "mean_glucose_mgdl":            0.0,
    "mean_insulin_muL":             0.0,
    "mean_glucagon_pM":             0.0,
}

# normalising scale per endpoint (order-of-magnitude of typical values)
NORM = {
    "hypo_burden_mgdl_min": 100.0, "hyper_burden_mgdl_min": 2000.0,
    "abs_dev_from_target_mgdl_min": 1e4, "glucose_auc_mgdl_min": 3e4,
    "glucose_sd_mgdl": 20.0, "glucose_rmsd_mgdl": 5.0,
    "glucose_peak_mgdl": 150.0, "glucose_nadir_mgdl": 70.0,
    "recovery_time_min": 120.0, "undershoot_mgdl": 20.0,
    "insulin_auc_muL_min": 1e4, "glucagon_auc_pM_min": 3e3,
    "mean_glucose_mgdl": 100.0, "mean_insulin_muL": 30.0, "mean_glucagon_pM": 12.0,
}


def composite_loss(ep: dict, weights: dict | None = None) -> float:
    w = DEFAULT_WEIGHTS if weights is None else weights
    total = 0.0
    for k, wk in w.items():
        v = ep.get(k)
        if v is None or not np.isfinite(v):
            continue
        total += wk * v / NORM.get(k, 1.0)
    return total


def classify_response(us, losses, rel_thresh=0.02):
    """Classify dose-response shape.

    Returns (label, u_opt, info). Labels:
      'Type0'  no meaningful improvement over baseline
      'TypeI'  monotonic benefit, optimum at/near maximum
      'TypeII' interior optimum: best u inside (0,1) beats both ends
      'TypeIII' plateau / broad optimum
      'TypeIV' (assigned by caller when optimum differs across challenges)
    """
    us = np.asarray(us, float); L = np.asarray(losses, float)
    i0 = int(np.argmin(us))
    i1 = int(np.argmax(us))
    L0, L1 = L[i0], L[i1]
    j = int(np.argmin(L)); u_opt = float(us[j]); Lopt = L[j]
    eps = rel_thresh * max(abs(L0), abs(L1), 1e-12)
    beat0 = Lopt < L0 - eps
    beat1 = Lopt < L1 - eps
    interior = 1e-9 < u_opt < 1 - 1e-9
    span = L.max() - L.min()
    if span <= eps and not (beat0 and beat1):
        return "TypeIII", u_opt, dict(span=span)
    if interior and beat0 and beat1:
        return "TypeII", u_opt, dict(span=span, gain0=L0 - Lopt, gain1=L1 - Lopt)
    if not beat0:
        # nothing beats baseline
        if abs(u_opt - 1.0) < 1e-9 or u_opt > 0.9:
            return "Type0", u_opt, dict(span=span)
        return "Type0", u_opt, dict(span=span)
    if u_opt >= 0.9:
        return "TypeI", u_opt, dict(span=span)
    # beats baseline but not maximum -> partial benefit region at low u only
    if interior and beat0:
        return "TypeII*", u_opt, dict(span=span, gain0=L0 - Lopt, gain1=L1 - Lopt,
                                      note="beats baseline, not max")
    return "TypeI", u_opt, dict(span=span)
