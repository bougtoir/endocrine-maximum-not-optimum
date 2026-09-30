"""Dynamic challenge conditions for the simulation experiments."""

import numpy as np

# Each challenge: params override + simulation options.
# Times in minutes. Window endpoints evaluated on t >= 0 unless stated.

IVGTT_RATE = 64.81          # mmol/min for 3 min  (0.5 g/kg over 3 min, 70 kg)
IVITT_RATE = 0.04 * 70 * 6944 / 3.0   # pmol/min: 0.04 U/kg insulin over 3 min
CIVII_RATE = 0.25 * 70 * 6.944 / 1000.0  # pmol/min? -> see below

# IVITT 0.04 U/kg * 70 kg = 2.8 U = 2800 mU -> pmol = 2800*6.944 = 19443 pmol
# over 3 min -> 6481 pmol/min
IVITT_RATE = 2800.0 * 6.944 / 3.0
# CIVII: 0.25 mU/kg/min * 70 kg = 17.5 mU/min = 121.5 pmol/min, 150 min
CIVII_RATE = 17.5 * 6.944

CHALLENGES = {
    "fasting": dict(
        params={}, oral_dose_mmol=None, t_span=(-30.0, 600.0),
        label="Prolonged fasting (basal hold, 600 min)"),
    "ivgtt": dict(
        params={"GammaIVGin": IVGTT_RATE, "TimeIVG": 0.0, "TimeIVGend": 3.0},
        oral_dose_mmol=None, t_span=(-30.0, 180.0),
        label="Intravenous glucose tolerance test (0.5 g/kg over 3 min)"),
    "ogtt": dict(
        params={}, oral_dose_mmol=555.56, dose_time=0.0,
        t_span=(-30.0, 300.0),
        label="Oral glucose tolerance test (100 g)"),
    "ivitt": dict(
        params={"GammaIVIin": IVITT_RATE, "TimeIVI": 0.0, "TimeIVIend": 3.0},
        oral_dose_mmol=None, t_span=(-30.0, 180.0),
        label="Intravenous insulin tolerance test (0.04 U/kg over 3 min)"),
    "civii": dict(
        params={"GammaIVIin": CIVII_RATE, "TimeIVI": 0.0, "TimeIVIend": 150.0},
        oral_dose_mmol=None, t_span=(-30.0, 330.0),
        label="Continuous IV insulin infusion (0.25 mU/kg/min, 150 min)"),
}

PRIMARY_CHALLENGES = ["fasting", "ivgtt", "ogtt", "ivitt"]


def run_challenge(name: str, u: float, intervention, extra_params=None):
    """Simulate challenge `name` under intervention at modulation u."""
    import sorensen_model as sm
    ch = CHALLENGES[name]
    params = dict(ch["params"])
    if extra_params:
        params.update(extra_params)
    t, Y = sm.simulate(params=params, mods=intervention.mods(u),
                       t_span=ch["t_span"],
                       oral_dose_mmol=ch.get("oral_dose_mmol"),
                       dose_time=ch.get("dose_time", 0.0))
    return t, Y
