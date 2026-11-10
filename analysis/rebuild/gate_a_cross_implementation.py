"""Gate A3: cross-implementation check. Upstream frozen Sorensen MATLAB autocode (run in GNU Octave,
RK4 dt=0.1 min; analysis/rebuild/octave/run_upstream.m) vs the Python port with the same protocol-specific
(Sorensen IV) secretion parameters and identical infusion timing. Also reports the historical Python
configuration (BioSorSimo secretion) against the same upstream reference."""
import sys, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src")); sys.path.insert(0, str(ROOT / "analysis/rebuild"))
import sorensen_model as sm
from challenges import CHALLENGES
from endpoints import MMOL_TO_MGDL, PM_TO_MU_L
from gate_a_reference_sims import SORENSEN_IV_SECRETION

UP = ROOT / "results/rebuild/gate_a/upstream_octave"
TIMING = {"ivgtt": dict(TimeIVG=-3.0, TimeIVGend=0.0, t_span=(-30.0, 200.0)),
          "ivitt": dict(t_span=(-30.0, 180.0)), "civii": dict(t_span=(-30.0, 330.0)),
          "fasting": dict(t_span=(-30.0, 200.0))}
FACTOR = {"ivgtt": 0.84, "ivitt": 0.925, "civii": 0.925, "fasting": 0.925}


def py(ch, secretion):
    tm = dict(TIMING[ch]); ts = tm.pop("t_span")
    p = dict(CHALLENGES[ch]["params"]); p.update(tm); p.update(secretion)
    t, Y = sm.simulate(params=p, t_span=ts)
    return t, Y


def main():
    rows = []
    for run in list(TIMING) + ["ivitt_nocap"]:
        ch = run.replace("_nocap", "")
        f = UP / f"{run}.csv"
        if not f.exists():
            continue
        u = np.loadtxt(f, delimiter=",")
        tu, gu, iu, cu = u[:, 0], u[:, 1] * MMOL_TO_MGDL, u[:, 2] * PM_TO_MU_L, u[:, 3]
        for lab, sec in [("python_sorensen_iv_secretion", SORENSEN_IV_SECRETION), ("python_historical_biosorsimo", {})]:
            t, Y = py(ch, sec)
            g = np.interp(tu, t, Y[sm.STATE_INDEX["GlucPV"]]) * MMOL_TO_MGDL
            i = np.interp(tu, t, Y[sm.STATE_INDEX["InsuPV"]]) * PM_TO_MU_L
            c = np.interp(tu, t, Y[sm.STATE_INDEX["Cgon"]])
            m = tu >= 0
            rows.append(dict(challenge=ch, upstream_run=run, python_config=lab,
                             upstream_glucose_peak=gu[m].max(), python_glucose_peak=g[m].max(),
                             upstream_glucose_nadir=gu[m].min(), python_glucose_nadir=g[m].min(),
                             upstream_insulin_peak=iu[m].max(), python_insulin_peak=i[m].max(),
                             max_abs_diff_glucose_mgdl=np.abs(g - gu).max(),
                             max_abs_diff_insulin_muL=np.abs(i - iu).max(),
                             max_abs_diff_glucagon_pM=np.abs(c - cu).max(),
                             obs_factor=FACTOR[ch],
                             upstream_obs_glucose_nadir=FACTOR[ch] * gu[m].min()))
    df = pd.DataFrame(rows)
    df.to_csv(ROOT / "results/rebuild/gate_a/GATE_A_CROSS_IMPLEMENTATION.csv", index=False)
    print(df.round(3).T.to_string())


if __name__ == "__main__":
    main()
