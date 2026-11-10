"""Gate A2-A4: protocol-specific reference simulations.

Compares the manuscript implementation (BioSorSimo OGTT-refit insulin-secretion
parameters used for ALL protocols) against the upstream protocol-specific
parameterisation (Sorensen IV parameters for IVGTT/IVITT/CIVII; BioSorSimo for
OGTT), and reports raw GlucPV alongside the Panunzi et al. 2020 observation
transforms (x0.84 venous blood glucose, IVGTT; x0.925 venous plasma glucose,
IVITT/CIVII). No transform is applied inside the model."""
import sys, pathlib
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import sorensen_model as sm
from challenges import CHALLENGES
from endpoints import MMOL_TO_MGDL, PM_TO_MU_L

SORENSEN_IV_SECRETION = dict(beta1PIR=3.27, beta2PIR=7.33333, beta3PIR=2.879, beta4PIR=3.02,
                             beta5PIR=1.11, KappaRinsu=0.00794, KappaRinsuPotn=4025.0,
                             KappaPotnPtgt=0.0482, KappaPinhPrp=0.931, EMME1=0.00747, EMME2=0.0958)
OBS_FACTOR = {"ivgtt": 0.84, "ivitt": 0.925, "civii": 0.925, "ogtt": None}
OBS_LABEL = {"ivgtt": "venous blood glucose (x0.84, Panunzi 2020 Fig 2)",
             "ivitt": "venous plasma glucose (x0.925, Panunzi 2020 Fig 3)",
             "civii": "venous plasma glucose (x0.925, Panunzi 2020 Fig 3)",
             "ogtt": "no transform stated for OGTT (Panunzi 2020 Fig 4 / Data.xlsx 'GlucPV')"}
PARAM_SETS = {"manuscript_impl_biosorsimo_secretion": {},
              "upstream_sorensen_iv_secretion": SORENSEN_IV_SECRETION}


def run(ch, pset):
    c = CHALLENGES[ch]
    p = dict(c["params"]); p.update(PARAM_SETS[pset])
    t, Y = sm.simulate(params=p, t_span=c["t_span"], oral_dose_mmol=c.get("oral_dose_mmol"),
                       dose_time=c.get("dose_time", 0.0))
    tu = np.arange(c["t_span"][0], c["t_span"][1] + 1e-9, 0.5)
    g = np.interp(tu, t, Y[sm.STATE_INDEX["GlucPV"]]) * MMOL_TO_MGDL
    ins = np.interp(tu, t, Y[sm.STATE_INDEX["InsuPV"]]) * PM_TO_MU_L
    cg = np.interp(tu, t, Y[sm.STATE_INDEX["Cgon"]])
    return tu, g, ins, cg


def summary(ch, pset):
    tu, g, ins, cg = run(ch, pset)
    m = tu >= 0
    f = OBS_FACTOR[ch]
    r = dict(challenge=ch, parameter_set=pset, observation=OBS_LABEL[ch],
             basal_GlucPV_mgdl=g[tu <= -1][-1], basal_insulin_muL=ins[tu <= -1][-1],
             basal_glucagon_pM=cg[tu <= -1][-1],
             peak_GlucPV_mgdl=g[m].max(), t_peak_glucose_min=tu[m][g[m].argmax()],
             nadir_GlucPV_mgdl=g[m].min(), t_nadir_glucose_min=tu[m][g[m].argmin()],
             peak_insulin_muL=ins[m].max(), t_peak_insulin_min=tu[m][ins[m].argmax()],
             peak_glucagon_pM=cg[m].max(), min_glucagon_pM=cg[m].min(),
             end_GlucPV_mgdl=g[-1], end_insulin_muL=ins[-1])
    if f:
        r.update(obs_factor=f, basal_obs_mgdl=r["basal_GlucPV_mgdl"] * f,
                 peak_obs_mgdl=r["peak_GlucPV_mgdl"] * f, nadir_obs_mgdl=r["nadir_GlucPV_mgdl"] * f)
    return r


def main():
    out = ROOT / "results/rebuild/gate_a"
    rows = [summary(ch, ps) for ch in ["ivgtt", "ogtt", "ivitt", "civii"] for ps in PARAM_SETS]
    df = pd.DataFrame(rows)
    df.to_csv(out / "GATE_A_PROTOCOL_COMPARISON.csv", index=False)
    traces = []
    for ch in ["ivgtt", "ogtt", "ivitt", "civii"]:
        for ps in PARAM_SETS:
            tu, g, ins, cg = run(ch, ps)
            traces.append(pd.DataFrame(dict(challenge=ch, parameter_set=ps, t_min=tu,
                                            GlucPV_mgdl=g, InsuPV_muL=ins, Cgon_pM=cg)))
    pd.concat(traces).to_csv(out / "reference_traces.csv", index=False)
    pd.set_option("display.width", 250)
    print(df.drop(columns=["observation"]).round(2).T.to_string())


if __name__ == "__main__":
    main()
