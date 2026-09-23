"""Tables + machine-readable manuscript values export.

Outputs:
  results/tables/table1_interventions.csv/.tex
  results/tables/table2_classification.csv/.tex
  manuscript_values.csv  (every number the manuscript cites, with provenance)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
from interventions import INTERVENTIONS, ALL_INTERVENTIONS

R = os.path.join(os.path.dirname(__file__), "..", "results")
TBL = os.path.join(R, "tables"); os.makedirs(TBL, exist_ok=True)

LABEL = {
    "insulin_signal_peripheral": "Insulin signalling (peripheral uptake)",
    "insulin_signal_hepatic": "Insulin signalling (hepatic)",
    "insulin_signal_global": "Insulin signalling (global)",
    "insulin_signal_global_inhibition": "Insulin signalling (inhibition)",
    "glucagon_signal_hepatic": "Glucagon signalling (hepatic HGP)",
    "glucagon_signal_inhibition": "Glucagon signalling (inhibition)",
    "insulin_secretion": "Insulin secretion (potentiation)",
    "insulin_secretion_inhibition": "Insulin secretion (impairment)",
    "glucagon_secretion": "Glucagon secretion (potentiation)",
    "glucagon_secretion_inhibition": "Glucagon secretion (suppression)",
}


def main():
    # --- Table 1: interventions
    rows = []
    for n in ALL_INTERVENTIONS:
        iv = INTERVENTIONS[n]
        rows.append(dict(intervention=n, label=iv.label, mode=iv.mode,
                         mod_key=iv.mod_key, f_u_max=iv.factor(1.0),
                         description=iv.description))
    t1 = pd.DataFrame(rows)
    t1.to_csv(f"{TBL}/table1_interventions.csv", index=False)

    # --- Table 2: classification summary (refined where available)
    cl = pd.read_csv(f"{R}/scans/full_classification.csv")
    try:
        ref = pd.read_csv(f"{R}/scans/refined_classification.csv")
        for i, r in cl.iterrows():
            m = ref[(ref.intervention == r.intervention)
                    & (ref.challenge == r.challenge)]
            if len(m):
                # refined grid gives better u_opt/loss_opt/gains; keep the
                # full-range response_class (endpoints 0/1 are outside the
                # refined window)
                for c in ("u_opt", "loss_opt", "gain0", "gain1"):
                    cl.loc[i, c] = m.iloc[0][c]
    except FileNotFoundError:
        pass
    cl["intervention_label"] = cl.intervention.map(LABEL)
    t2 = cl[["intervention_label", "challenge", "response_class", "u_opt",
             "loss_baseline", "loss_opt", "loss_max", "gain0", "gain1"]]
    t2.columns = ["Intervention", "Challenge", "Class", "u*",
                  "L(0)", "L(u*)", "L(1)", "G0", "G1"]
    t2.to_csv(f"{TBL}/table2_classification.csv", index=False)

    # --- manuscript_values.csv
    vals = []
    def add(key, value, source):
        vals.append(dict(key=key, value=value, source=source))
    for _, r in t2.iterrows():
        k = f"{r['Intervention']}|{r['Challenge']}"
        add(f"{k}|class", r["Class"], "results/scans/*_classification.csv")
        add(f"{k}|u_opt", r["u*"], "results/scans/*_classification.csv")
        add(f"{k}|L0", r["L(0)"], "results/scans/*_classification.csv")
        add(f"{k}|Lopt", r["L(u*)"], "results/scans/*_classification.csv")
        add(f"{k}|L1", r["L(1)"], "results/scans/*_classification.csv")
        add(f"{k}|G0", r["G0"], "results/scans/*_classification.csv")
        add(f"{k}|G1", r["G1"], "results/scans/*_classification.csv")
    mv = pd.DataFrame(vals)
    mv.to_csv(os.path.join(os.path.dirname(__file__), "..",
                           "manuscript_values.csv"), index=False)
    print(t2.round(3).to_string())
    print(f"\n{len(mv)} manuscript values exported")


if __name__ == "__main__":
    main()
