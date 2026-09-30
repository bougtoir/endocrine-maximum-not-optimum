"""Feedback-mechanism analysis.

For key (intervention, challenge) cases, record the algebraic fluxes
(GammaHGP, GammaPGU, GammaHGU, secretion rates) and hormone trajectories
at u = 0, u*, 1 to identify the counter-regulatory mechanism responsible
for the interior optimum (or its absence).

Outputs results/feedback/*.csv (time series) and mechanism_summary.csv.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
import sorensen_model as sm
from interventions import INTERVENTIONS
from challenges import CHALLENGES
from endpoints import glucose_series, insulin_series, glucagon_series

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "feedback")

CASES = [
    ("insulin_secretion_inhibition", "ivgtt", [0.0, 0.8, 1.0]),
    ("glucagon_secretion", "ogtt", [0.0, 0.85, 1.0]),
    ("glucagon_signal_inhibition", "ogtt", [0.0, 0.10, 1.0]),
    ("insulin_signal_global_inhibition", "ivgtt", [0.0, 0.70, 1.0]),
    ("insulin_signal_global", "ogtt", [0.0, 0.5, 1.0]),
]

FLUX_KEYS = ["GammaHGP", "GammaPGU", "GammaHGU", "Secr", "GammaPCR",
             "MIPGU", "MIHGPinf", "MCHGP", "MIHGUinf"]


def run_case(ivn, ch, us):
    chd = CHALLENGES[ch]
    series = []
    for u in us:
        iv = INTERVENTIONS[ivn]
        t, Y = sm.simulate(params=chd["params"], mods=iv.mods(u),
                           t_span=chd["t_span"],
                           oral_dose_mmol=chd.get("oral_dose_mmol"),
                           dose_time=chd.get("dose_time", 0.0),
                           t_eval=np.arange(chd["t_span"][0], chd["t_span"][1] + 1, 2.0))
        p = sm.derived_params({**sm.BASE_PARAMS, **chd["params"]})
        alg = [sm.algebraics(Y[:, i], p, iv.mods(u)) for i in range(len(t))]
        d = dict(t=t, u=u,
                 glucose_mgdl=glucose_series(t, Y),
                 insulin_mU_L=insulin_series(t, Y),
                 glucagon_pM=glucagon_series(t, Y))
        for k in FLUX_KEYS:
            if k in alg[0]:
                d[k] = [a[k] for a in alg]
        series.append(pd.DataFrame(d))
    return pd.concat(series)


def main():
    os.makedirs(OUT, exist_ok=True)
    summ = []
    for ivn, ch, us in CASES:
        df = run_case(ivn, ch, us)
        fn = f"{OUT}/{ivn}__{ch}.csv"
        df.to_csv(fn, index=False)
        for u in us:
            sub = df[df.u == u]
            post = sub[sub.t >= 0]
            summ.append(dict(intervention=ivn, challenge=ch, u=u,
                peak_glucose=post.glucose_mgdl.max(),
                nadir_glucose=post.glucose_mgdl.min(),
                peak_insulin=post.insulin_mU_L.max(),
                peak_glucagon=post.glucagon_pM.max(),
                mean_HGP=post.GammaHGP.mean() if "GammaHGP" in post else np.nan,
                mean_PGU=post.GammaPGU.mean() if "GammaPGU" in post else np.nan,
                max_Secr=post.Secr.max() if "Secr" in post else np.nan))
    s = pd.DataFrame(summ)
    s.to_csv(f"{OUT}/mechanism_summary.csv", index=False)
    print(s.round(2).to_string())


if __name__ == "__main__":
    main()
