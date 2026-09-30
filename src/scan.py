"""Modulation-grid scans: sweep u for each intervention x challenge.

Outputs follow the master data schema:
  trajectories.parquet / endpoints.csv / classification.csv
"""

from __future__ import annotations

import numpy as np
import pandas as pd

import sorensen_model as sm
from challenges import CHALLENGES, run_challenge
from endpoints import endpoint_values, ENDPOINT_META
from homeostatic_loss import composite_loss, classify_response
from interventions import INTERVENTIONS

U_GRID = np.round(np.arange(0.0, 1.0 + 1e-9, 0.05), 2)


def sweep(intervention_name: str, challenge: str, u_grid=U_GRID,
          extra_params=None, weights=None, keep_traces=False):
    """Run one intervention x challenge over the u grid."""
    iv = INTERVENTIONS[intervention_name]
    rows = []
    traces = {}
    for u in u_grid:
        t, Y = run_challenge(challenge, float(u), iv, extra_params=extra_params)
        ep = endpoint_values(t, Y)
        ep["composite_loss"] = composite_loss(ep, weights)
        row = dict(
            intervention=intervention_name, label=iv.label,
            intervention_type=iv.mode, direction_definition="u:0=none,1=max",
            challenge=challenge, modulation_fraction=float(u),
            native_parameter_value=iv.factor(float(u)),
            simulation_status="ok",
        )
        row.update(ep)
        rows.append(row)
        if keep_traces:
            traces[float(u)] = (t, Y)
    df = pd.DataFrame(rows)
    lab, u_opt, info = classify_response(df["modulation_fraction"].values,
                                         df["composite_loss"].values)
    cls = dict(intervention=intervention_name, challenge=challenge,
               response_class=lab, u_opt=u_opt,
               loss_baseline=float(df["composite_loss"].iloc[0]),
               loss_opt=float(df["composite_loss"].min()),
               loss_max=float(df["composite_loss"].iloc[-1]),
               **info)
    if keep_traces:
        return df, cls, traces
    return df, cls


def run_grid(interventions, challenges, u_grid=U_GRID, extra_params=None,
             weights=None):
    dfs, cls_rows = [], []
    for ch in challenges:
        for ivn in interventions:
            df, cls = sweep(ivn, ch, u_grid, extra_params=extra_params,
                            weights=weights)
            dfs.append(df); cls_rows.append(cls)
    return pd.concat(dfs, ignore_index=True), pd.DataFrame(cls_rows)
