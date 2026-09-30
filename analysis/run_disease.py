"""Disease-state extensions (run only after healthy-state analysis).

T2DM-like: insulin signalling efficacy held at 0.5 at all sites —
  interventions re-scanned around the insulin-resistant baseline.
T1DM-like: endogenous insulin secretion abolished (insulin_secretion=0).

Outputs results/disease/.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
import sorensen_model as sm
from scan import U_GRID
from interventions import INTERVENTIONS, ALL_INTERVENTIONS
from challenges import CHALLENGES
from endpoints import endpoint_values
from homeostatic_loss import composite_loss, classify_response, DEFAULT_WEIGHTS

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "disease")


def _sweep_mods(mods_fn, challenge, u_grid=U_GRID):
    ch = CHALLENGES[challenge]
    rows = []
    for u in u_grid:
        t, Y = sm.simulate(params=ch["params"], mods=mods_fn(u),
                           t_span=ch["t_span"],
                           oral_dose_mmol=ch.get("oral_dose_mmol"),
                           dose_time=ch.get("dose_time", 0.0))
        ep = endpoint_values(t, Y)
        ep["modulation_fraction"] = u
        ep["composite_loss"] = composite_loss(ep, DEFAULT_WEIGHTS)
        rows.append(ep)
    df = pd.DataFrame(rows)
    lab, u_opt, info = classify_response(u_grid, df["composite_loss"].values)
    cls = dict(response_class=lab, u_opt=u_opt,
               loss_baseline=float(df.composite_loss.iloc[0]),
               loss_opt=float(df.composite_loss.min()),
               loss_max=float(df.composite_loss.iloc[-1]),
               gain0=info.get("gain0"), gain1=info.get("gain1"))
    return df, cls


def main():
    os.makedirs(OUT, exist_ok=True)
    rows_cls = []
    for state, patch in (
        ("t2dm", lambda m: {**m,
            **{k: m.get(k, 1.0) * 0.5
               for k in ("insulin_pgu", "insulin_hgp", "insulin_hgu")}}),
        ("t1dm", lambda m: {**m, "insulin_secretion": 0.0}),
    ):
        for ivn in ALL_INTERVENTIONS:
            iv = INTERVENTIONS[ivn]
            for ch in ("fasting", "ogtt"):
                df, cls = _sweep_mods(lambda u, iv=iv, p=patch: p(iv.mods(u)), ch)
                df.to_csv(f"{OUT}/{state}_{ivn}__{ch}.csv", index=False)
                rows_cls.append(dict(state=state, intervention=ivn,
                                     challenge=ch, **cls))
    cl = pd.DataFrame(rows_cls)
    cl.to_csv(f"{OUT}/disease_classification.csv", index=False)
    print(cl.round(3).to_string())


if __name__ == "__main__":
    main()
