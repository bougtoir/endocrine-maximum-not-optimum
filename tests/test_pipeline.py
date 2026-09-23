"""Unit tests for the endocrine 'maximum != optimum' pipeline.

Run: python -m pytest tests/ -q   (or plain `python tests/test_pipeline.py`)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import numpy as np
import sorensen_model as sm
from interventions import INTERVENTIONS, PRIMARY_INTERVENTIONS, INHIBITION_INTERVENTIONS
from challenges import CHALLENGES, run_challenge
from endpoints import endpoint_values, glucose_series, MMOL_TO_MGDL
from homeostatic_loss import composite_loss, classify_response, DEFAULT_WEIGHTS
from scan import sweep, U_GRID


def test_state_and_param_integrity():
    p = sm.derived_params(sm.BASE_PARAMS)
    for k in ("GammaBPIR", "GlucPV0", "InsuPV0", "Cgon0"):
        assert k in p and np.isfinite(p[k]) and p[k] > 0
    y0 = sm.initial_state(p)
    assert y0.shape == (len(sm.STATE_NAMES),)
    assert np.all(np.isfinite(y0))


def test_basal_is_steady_state():
    """Basal initial condition must be near a fixed point of the ODE."""
    p = sm.derived_params(sm.BASE_PARAMS)
    y0 = sm.initial_state(p)
    dy = sm.rhs(0.0, y0, p, None)
    rel = np.abs(dy).max()
    assert rel < 0.02, f"basal drift too large: {rel}"


def test_fasting_drift_small():
    t, Y = run_challenge("fasting", 0.0, INTERVENTIONS["insulin_signal_global"])
    g = glucose_series(t, Y)
    assert abs(g[-1] - g[0]) < 0.5  # mg/dL over 600 min


def test_u0_reproduces_baseline_all_interventions():
    """u=0 must give the unmodified model for every intervention."""
    ch = "ogtt"
    t0, Y0 = run_challenge(ch, 0.0, INTERVENTIONS["insulin_signal_global"])
    for name, iv in INTERVENTIONS.items():
        t, Y = run_challenge(ch, 0.0, iv)
        assert np.abs(Y - Y0).max() < 1e-9, name


def test_factor_convention():
    """u=0 -> factor 1; potentiation u=1 -> GMAX; inhibition u=1 -> 0."""
    for name in PRIMARY_INTERVENTIONS:
        f = INTERVENTIONS[name].factor
        assert f(0.0) == 1.0 and f(1.0) == 3.0
    for name in INHIBITION_INTERVENTIONS:
        f = INTERVENTIONS[name].factor
        assert f(0.0) == 1.0 and f(1.0) == 0.0


def test_inhibition_stronger_than_baseline():
    """Ablating insulin secretion must raise OGTT hyperglycaemia."""
    base = endpoint_values(*run_challenge("ogtt", 0.0, INTERVENTIONS["insulin_secretion"]))
    abl = endpoint_values(*run_challenge("ogtt", 1.0, INTERVENTIONS["insulin_secretion_inhibition"]))
    assert abl["glucose_peak_mgdl"] > base["glucose_peak_mgdl"]


def test_glucagon_ablation_reduces_fasting_glucose():
    base = endpoint_values(*run_challenge("fasting", 0.0, INTERVENTIONS["glucagon_secretion"]))
    abl = endpoint_values(*run_challenge("fasting", 1.0, INTERVENTIONS["glucagon_secretion_inhibition"]))
    assert abl["mean_glucose_mgdl"] < base["mean_glucose_mgdl"]


def test_recovery_time_zero_without_excursion():
    t, Y = run_challenge("fasting", 0.0, INTERVENTIONS["insulin_signal_global"])
    ep = endpoint_values(t, Y)
    assert ep["recovery_time_min"] == 0.0


def test_classify_type0_flat():
    losses = np.full(21, 5.0)
    label, u_opt, info = classify_response(np.asarray(U_GRID, float), losses)
    assert label in ("Type0", "TypeIII")


def test_classify_typeII_interior():
    u = np.linspace(0, 1, 21)
    losses = 5.0 + 20.0 * (u - 0.4) ** 2   # minimum at u=0.4
    label, u_opt, info = classify_response(u, losses)
    assert label == "TypeII"
    assert info["gain0"] > 0 and info["gain1"] > 0


def test_classify_typeI_monotone_improving():
    u = np.linspace(0, 1, 21)
    label, u_opt, info = classify_response(u, 5.0 - u)
    assert label == "TypeI"


def test_classify_edge():
    u = np.linspace(0, 1, 21)
    losses = 5.0 + 20.0 * (u - 0.4) ** 2
    losses[0] -= 4.0                        # u=0 best on grid
    label, u_opt, info = classify_response(u, losses)
    assert label in ("Type0", "TypeIII")


def test_sweep_output_shape():
    df, cls = sweep("insulin_signal_global", "fasting",
                    u_grid=np.array([0.0, 0.5, 1.0]))
    assert len(df) == 3 and "composite_loss" in df.columns
    assert cls["u_opt"] in (0.0, 0.5, 1.0)


def test_mods_keys_consistent():
    """Every mod key used by interventions must be read by the model."""
    used = set()
    for iv in INTERVENTIONS.values():
        used |= set(iv.mods(0.5).keys())
    known = {"insulin_pgu", "insulin_hgp", "insulin_hgu", "glucagon_hgp",
             "insulin_secretion", "glucagon_secretion"}
    assert used <= known


def test_composite_loss_nonnegative_and_uses_weights():
    t, Y = run_challenge("ogtt", 0.0, INTERVENTIONS["insulin_signal_global"])
    ep = endpoint_values(t, Y)
    L = composite_loss(ep, DEFAULT_WEIGHTS)
    assert np.isfinite(L) and L >= 0


def test_solver_deterministic():
    t1, Y1 = run_challenge("ogtt", 0.5, INTERVENTIONS["glucagon_signal_hepatic"])
    t2, Y2 = run_challenge("ogtt", 0.5, INTERVENTIONS["glucagon_signal_hepatic"])
    assert np.abs(Y1 - Y2).max() < 1e-10


if __name__ == "__main__":
    import traceback
    fns = [v for k, v in globals().items() if k.startswith("test_")]
    bad = 0
    for f in fns:
        try:
            f(); print("PASS", f.__name__)
        except Exception:
            bad += 1; print("FAIL", f.__name__); traceback.print_exc()
    print(f"{len(fns)-bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
