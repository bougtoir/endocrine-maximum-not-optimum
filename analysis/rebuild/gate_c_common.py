"""Shared helpers for exploratory Gate C (corrected configuration C unless stated).

Configuration C = protocol-specific insulin-secretion parameters (Sorensen IV values for
non-oral protocols, BioSorSimo oral refit for OGTT) + plasma observation 0.925 x GlucPV.
Simulation semantics are identical to src/challenges.run_challenge; this module only
adds (i) explicit mods dictionaries so ablations can be combined with an intervention,
(ii) optional parameter overrides, (iii) algebraic flux traces, (iv) evaluation logging.
"""
import sys, time, pathlib, csv, os
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "analysis/rebuild"))
import sorensen_model as sm
from challenges import CHALLENGES
from endpoints import endpoint_values, MMOL_TO_MGDL, PM_TO_MU_L
from homeostatic_loss import composite_loss, classify_response
from interventions import INTERVENTIONS
from scan import U_GRID
from gate_a_reference_sims import SORENSEN_IV_SECRETION

OUT = ROOT / "results/rebuild/gate_c"
OUT.mkdir(parents=True, exist_ok=True)
PLASMA = 0.925
GI = sm.STATE_INDEX["GlucPV"]
CHALLENGES5 = ["fasting", "ivgtt", "ogtt", "ivitt", "civii"]
CLIP = 0.05
_EVALS = 0


def protocol_params(ch, cfg="C"):
    p = dict(CHALLENGES[ch]["params"])
    if cfg in ("C", "S", "CB") and ch != "ogtt":
        p.update(SORENSEN_IV_SECRETION)
    return p


def obs_factor(cfg="C"):
    return {"C": PLASMA, "O": PLASMA, "CB": 0.84}.get(cfg, 1.0)


def combine_mods(*ms):
    out = {}
    for m in ms:
        for k, v in (m or {}).items():
            out[k] = out.get(k, 1.0) * v
    return out


def run(ch, mods=None, cfg="C", overrides=None, t_span=None, rtol=1e-7, atol=1e-9):
    """Return t, Y (raw states) and Yobs (GlucPV scaled to the observation scale)."""
    global _EVALS
    c = CHALLENGES[ch]
    p = protocol_params(ch, cfg)
    if overrides:
        p.update(overrides)
    t, Y = sm.simulate(params=p, mods=mods, t_span=t_span or c["t_span"],
                       oral_dose_mmol=c.get("oral_dose_mmol"), dose_time=c.get("dose_time", 0.0),
                       rtol=rtol, atol=atol)
    _EVALS += 1
    Yobs = np.array(Y, copy=True); Yobs[GI] *= obs_factor(cfg)
    return t, Y, Yobs


def run_iv(ivn, u, ch, cfg="C", extra_mods=None, **kw):
    return run(ch, combine_mods(INTERVENTIONS[ivn].mods(float(u)), extra_mods), cfg, **kw)


def full_params(ch, cfg="C", overrides=None):
    p = dict(sm.BASE_PARAMS); p.update(protocol_params(ch, cfg))
    if overrides:
        p.update(overrides)
    return sm.derived_params(p)


def flux_traces(t, Y, ch, mods=None, cfg="C", overrides=None, dt=0.5, t0=None):
    """Algebraic fluxes/multipliers on a uniform grid (t >= t0)."""
    d = full_params(ch, cfg, overrides)
    t0 = t[0] if t0 is None else t0
    tu = np.arange(t0, t[-1] + 1e-9, dt)
    Yu = np.vstack([np.interp(tu, t, Y[i]) for i in range(Y.shape[0])])
    rows = [sm.algebraics(Yu[:, k], d, mods) for k in range(len(tu))]
    keys = rows[0].keys()
    return tu, Yu, {k: np.array([r[k] for r in rows]) for k in keys}


def glucose_mgdl(t, Yobs, dt=0.5, t0=0.0):
    tu = np.arange(t0, t[-1] + 1e-9, dt)
    return tu, np.interp(tu, t, Yobs[GI] * MMOL_TO_MGDL)


def direct_outcomes(t, Yobs, g_pre=None):
    """Predeclared direct glycaemic outcomes (docs: results/rebuild/gate_c/C2_PRESPEC.md)."""
    tu, g = glucose_mgdl(t, Yobs)
    gpre = g_pre if g_pre is not None else float(np.interp(-30.0, t, Yobs[GI] * MMOL_TO_MGDL))
    dt = tu[1] - tu[0]
    out = dict(
        g_pre_mgdl=gpre, g0_mgdl=g[0], drift_pre_mgdl=g[0] - gpre,
        nadir_mgdl=g.min(), t_nadir_min=tu[g.argmin()], peak_mgdl=g.max(), t_peak_min=tu[g.argmax()],
        min_below70=float((g[:-1] < 70).sum() * dt), min_below54=float((g[:-1] < 54).sum() * dt),
        min_above140=float((g[:-1] > 140).sum() * dt), min_above180=float((g[:-1] > 180).sum() * dt),
        hypo70_burden=float(np.trapezoid(np.clip(70 - g, 0, None), tu)),
        hyper140_burden=float(np.trapezoid(np.clip(g - 140, 0, None), tu)),
        g_end_mgdl=g[-1], end_minus_pre_mgdl=g[-1] - gpre,
    )
    far = np.where(np.abs(g - gpre) > 10.0)[0]
    out["last_outside_pre_pm10_min"] = float(tu[far[-1]]) if len(far) else 0.0
    out["returned_to_pre_pm10"] = bool(len(far) == 0 or far[-1] < len(g) - 1)
    return out


def loss_row(t, Yobs):
    ep = endpoint_values(t, Yobs); ep["composite_loss"] = composite_loss(ep)
    return ep


class Budget:
    """Logs evaluations and wall time per script to compute_log.csv."""
    def __init__(self, name, cap):
        self.name, self.cap, self.t0, self.e0 = name, cap, time.time(), _EVALS

    def check(self, planned):
        if planned > self.cap:
            raise RuntimeError(f"{self.name}: planned {planned} evaluations exceed cap {self.cap}")

    def close(self, evals=None):
        n = (_EVALS - self.e0) if evals is None else evals
        path = OUT / "compute_log.csv"; new = not path.exists()
        with open(path, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["script", "evaluations", "cap", "wall_s", "utc"])
            w.writerow([self.name, n, self.cap, round(time.time() - self.t0, 1),
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])
        print(f"[{self.name}] evaluations={n} cap={self.cap} wall={time.time()-self.t0:.1f}s")


def glucH0_for_plasma(target_mgdl, cfg="C"):
    """GlucH0 giving an initial observed plasma glucose of exactly target_mgdl (GlucPV0 is not proportional to GlucH0)."""
    from scipy.optimize import brentq
    def f(gh):
        p = dict(sm.BASE_PARAMS); p["GlucH0"] = gh
        return sm.initial_state(p)[GI] * obs_factor(cfg) * MMOL_TO_MGDL - target_mgdl
    return brentq(f, 3.0, 9.0, xtol=1e-10)
