"""Exploratory HPT-axis scan (secondary system, hypothesis-generating only).

Interventions (same u convention):
  hpt_feedback_potentiation  s_fb = 1 + 2u   (stronger T3->TSH suppression)
  hpt_feedback_inhibition    s_fb = 1 - u
  hpt_thyroid_potentiation   s_th = 1 + 2u
  hpt_thyroid_inhibition     s_th = 1 - u

Challenge: T4 infusion 2.0 nmol/L/min for 60 min; horizon (-60, 360).
Loss mirrors the glucose composite: T3 band burdens (hypo <1.5, hyper >3),
|T3 - 2| deviation, TSH exposure cost.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
import hpt_model as H
from homeostatic_loss import classify_response

OUT = os.path.join(os.path.dirname(__file__), "..", "results", "hpt")
U = np.arange(0, 1.01, 0.05)

IVS = {
    "hpt_feedback_potentiation": lambda u: dict(s_fb=1 + 2 * u),
    "hpt_feedback_inhibition": lambda u: dict(s_fb=1 - u),
    "hpt_thyroid_potentiation": lambda u: dict(s_th=1 + 2 * u),
    "hpt_thyroid_inhibition": lambda u: dict(s_th=1 - u),
}


def loss(t, Y):
    m = t >= 0
    t3 = Y[2][m]
    hypo = np.trapezoid(np.clip(1.5 - t3, 0, None), t[m])
    hyper = np.trapezoid(np.clip(t3 - 3.0, 0, None), t[m])
    dev = np.trapezoid(np.abs(t3 - 2.0), t[m])
    tsh = np.trapezoid(Y[0][m], t[m])
    return (10 * hypo / 10.0 + 5 * hyper / 20.0 + dev / 400.0
            + 0.002 * tsh / 3000.0 + 20 * (t3.std() / 20.0))


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, curves = [], []
    for name, fn in IVS.items():
        L = []
        for u in U:
            kw = fn(u)
            t, Y = H.simulate(**kw, load_rate=2.0, load_t=(0, 60))
            li = loss(t, Y)
            L.append(li)
            curves.append(dict(intervention=name, u=u, loss=li,
                               t3_nadir=Y[2][t >= 0].min(),
                               t3_peak=Y[2][t >= 0].max(),
                               tsh_nadir=Y[0][t >= 0].min()))
        lab, u_opt, info = classify_response(U, np.array(L))
        rows.append(dict(intervention=name, response_class=lab, u_opt=u_opt,
                         loss_baseline=L[0], loss_opt=min(L), loss_max=L[-1],
                         gain0=info.get("gain0"), gain1=info.get("gain1")))
    pd.DataFrame(curves).to_csv(f"{OUT}/hpt_endpoints.csv", index=False)
    cls = pd.DataFrame(rows)
    cls.to_csv(f"{OUT}/hpt_classification.csv", index=False)
    print(cls.round(3).to_string())


if __name__ == "__main__":
    main()
