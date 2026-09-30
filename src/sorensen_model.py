"""Python port of the revised Sorensen glucose-insulin-glucagon whole-body model.

Provenance: iasi-cnr/A-Revised-Sorensen-Model (commit 1ad94954a708a4ae1f4415c494f94716ef2ff144),
Panunzi et al. 2020 PLoS ONE 15(8):e0237215 (CC-BY). The upstream MATLAB autocode in
models/primary/upstream/ is the frozen source of truth (see SHA256SUMS.txt).

This file unifies the two upstream variants:
  - 'Sorensen'   : IV glucose (GammaIVG) and IV insulin (GammaIVI) infusion windows
  - 'BioSorSimo' : oral glucose dose via GI transit chain (Sto -> Jej -> Rit -> Ile -> Roga)

State vector (26 differential states, in fixed order):
    0  GlucBV   brain vascular glucose        [mmol/L]
    1  GlucBI   brain interstitial glucose    [mmol/L]
    2  GlucH    heart/lung glucose            [mmol/L]  (arterial)
    3  GlucJ    gut glucose                   [mmol/L]
    4  GlucL    liver glucose                 [mmol/L]
    5  GlucK    kidney glucose                [mmol/L]
    6  GlucPV   peripheral vascular glucose   [mmol/L]
    7  GlucPI   peripheral interstitial gluc. [mmol/L]
    8  MIHGP    delayed insulin action on HGP [-]
    9  Fun2     glucagon-effect offset state  [-]
    10 MIHGU    delayed insulin action on HGU [-]
    11 InsuB    brain insulin                 [pM]
    12 InsuH    heart insulin                 [pM]
    13 InsuJ    gut insulin                   [pM]
    14 InsuL    liver insulin                 [pM]
    15 InsuK    kidney insulin                [pM]
    16 InsuPV   peripheral vascular insulin   [pM]
    17 InsuPI   peripheral interstitial ins.  [pM]
    18 Potn     potentiator state             [-]
    19 Pinh     inhibitor state               [-]
    20 Rinsu    labile insulin pool           [pmol]
    21 Cgon     plasma glucagon               [pM]
    22 Sto      stomach glucose               [mmol]
    23 Jej      jejunum glucose               [mmol]
    24 Rit      residence/ileal transit gluc. [mmol]
    25 Ile      ileum glucose                 [mmol]
"""

from __future__ import annotations

import numpy as np

STATE_NAMES = [
    "GlucBV", "GlucBI", "GlucH", "GlucJ", "GlucL", "GlucK", "GlucPV", "GlucPI",
    "MIHGP", "Fun2", "MIHGU",
    "InsuB", "InsuH", "InsuJ", "InsuL", "InsuK", "InsuPV", "InsuPI",
    "Potn", "Pinh", "Rinsu", "Cgon",
    "Sto", "Jej", "Rit", "Ile",
]
STATE_INDEX = {n: i for i, n in enumerate(STATE_NAMES)}

# Independent (user-settable) parameters, in the same order as upstream
# SorensenInitializeParvals bigtheta 001..097, plus unified input/GI params.
BASE_PARAMS = {
    # simulation control (overridden by simulate() kwargs)
    "Tzero": -30.0, "Tend": 200.0, "Tdelta": 0.1,
    # ---- glucose subsystem ----
    "QfloGB": 0.59, "VolGBV": 0.35, "VolBI": 0.45, "TdifB": 2.1,
    "GlucH0": 5.07333, "GammaBGU": 0.388889,
    "QfloGL": 1.26, "QfloGK": 1.01, "QfloGP": 1.51, "QfloGH": 4.37,
    "GammaRBCU": 0.0555556, "VolGH": 1.38,
    "QfloGJ": 1.01, "VolGJ": 1.12, "GammaJGU": 0.111111,
    "QfloGA": 0.25, "VolGL": 2.51, "VolGK": 0.66, "VolGPV": 1.04,
    "VolPI": 6.74, "TdifGP": 5.0, "GammaBPGU": 0.194444,
    "beta0PGU": 7.03, "beta1PGU": 6.52, "beta2PGU": 0.338, "beta3PGU": 5.82,
    # hepatic glucose production: glucagon/insulin/glucose multipliers
    "beta0HGP": 2.7, "beta1HGP": 0.388852, "tauCgon": 65.0,
    "beta2HGP": 1.21, "beta3HGP": 1.14, "beta4HGP": 1.66, "beta5HGP": 0.887748,
    "tauInsu": 25.0,
    "beta6HGP": 1.42, "beta7HGP": 1.41, "beta8HGP": 0.62, "beta9HGP": 0.504543,
    "GammaHGP0": 0.861111,
    # hepatic glucose uptake
    "beta0HGU": 2.0, "beta1HGU": 0.549306, "beta2HGU": 5.66, "beta3HGU": 5.66,
    "beta4HGU": 2.44, "beta5HGU": 1.4783, "GammaHGU0": 0.111111,
    # renal glucose excretion
    "beta0KGE": 0.394444, "beta1KGE": 0.394444, "beta2KGE": 0.198,
    "beta3KGE": 25.5556, "beta4KGE": 1.834, "beta5KGE": 0.0872,
    # ---- insulin subsystem ----
    "QfloIB": 0.45, "VolIB": 0.26, "VolIH": 0.99,
    "QfloIL": 0.9, "QfloIK": 0.72, "QfloIP": 1.05, "QfloIH": 3.12,
    "VolIJ": 0.94, "QfloIJ": 0.72, "VolIL": 1.14, "QfloIA": 0.18,
    "FracLIC": 0.4, "FracKIC": 0.3, "VolIK": 0.51, "VolIPV": 0.74,
    "TdifIP": 20.0, "FracPIC": 0.15,
    # pancreatic insulin release (Potn/Pinh/Rinsu system)
    # NOTE: values are the BioSorSimo refit for the oral glucose challenge
    # (upstream V01.01.45); the original IV-protocol values were
    # beta1PIR=3.27 beta2PIR=7.33333 beta3PIR=2.879 beta4PIR=3.02 beta5PIR=1.11
    # KappaRinsu=0.00794 KappaRinsuPotn=4025 KappaPotnPtgt=0.0482
    # KappaPinhPrp=0.931 EMME1=0.00747 EMME2=0.0958
    "beta1PIR": 6.51625, "beta2PIR": 4.13532, "beta3PIR": 4.34599,
    "beta4PIR": 5.57083, "beta5PIR": 2.28432,
    "KappaRinsu": 0.0137576, "Rinsu0": 44310.0, "KappaRinsuPotn": 3300.71,
    "KappaPotnPtgt": 0.0169775, "KappaPinhPrp": 15.212,
    "EMME1": 0.000241686, "EMME2": 0.304906,
    # ---- glucagon subsystem ----
    "InsuPV0": 91.0, "Cgon0": 11.48, "GammaMCC": 0.91, "VolC": 11.31,
    "beta0PCR": 2.93, "beta1PCR": 2.1, "beta2PCR": 4.18, "beta3PCR": 0.621325,
    "beta4PCR": 1.31, "beta5PCR": 0.61, "beta6PCR": 1.06, "beta7PCR": 0.471419,
    "Func20": 0.0,
    # ---- exogenous inputs (unified union of both upstream variants) ----
    # IV glucose infusion window [mmol/min]
    "GammaIVG0": 0.0, "GammaIVGin": 0.0, "TimeIVG": 0.0, "TimeIVGend": 0.0,
    # IV insulin infusion window [pmol/min]
    "GammaIVI0": 0.0, "GammaIVIin": 0.0, "TimeIVI": 0.0, "TimeIVIend": 0.0,
    # oral glucose dose [mmol] and GI transit chain [1/min]
    "Dose": 0.0, "DoseTime": 0.0,   # BioSorSimo applies Dose to Sto at t==0
    "kjs": 0.0365887, "kgj": 0.0245626, "krj": 0.0277149,
    "klr": 0.0248468, "kgl": 0.0261629, "frac": 1.0,
}


def derived_params(p: dict) -> dict:
    """Compute derived baseline quantities exactly as upstream DetermineParameters."""
    d = dict(p)
    InsuH0 = p["InsuPV0"] / (1.0 - p["FracPIC"])
    d["InsuH0"] = InsuH0
    d["InsuK0"] = InsuH0 * (1.0 - p["FracKIC"])
    d["InsuB0"] = InsuH0
    d["InsuJ0"] = InsuH0
    d["InsuPI0"] = p["InsuPV0"] - (p["QfloIP"] * p["TdifIP"] / p["VolPI"]) * (InsuH0 - p["InsuPV0"])
    d["InsuL0"] = (p["QfloIH"] * InsuH0 - p["QfloIB"] * InsuH0
                   - p["QfloIK"] * d["InsuK0"] - p["QfloIP"] * p["InsuPV0"]) / p["QfloIL"]
    d["GammaBPIR"] = (p["QfloIL"] / (1.0 - p["FracLIC"])) * d["InsuL0"] \
        - p["QfloIJ"] * InsuH0 - p["QfloIA"] * InsuH0
    d["GammaPIC0"] = d["InsuPI0"] / (((1.0 - p["FracPIC"]) / p["FracPIC"]) * (1.0 / p["QfloIP"])
                                     - p["TdifIP"] / p["VolPI"])
    Gh0 = p["GlucH0"]
    Pprp0 = Gh0 ** p["beta1PIR"] / (p["beta2PIR"] ** p["beta1PIR"]
                                    + p["beta3PIR"] * Gh0 ** p["beta4PIR"])
    d["Pprp0"] = Pprp0
    d["Ptgt0"] = Pprp0 ** p["beta5PIR"]
    d["Pinh0"] = Pprp0
    d["Potn0"] = d["Ptgt0"]
    d["InitialRinsu0"] = ((p["KappaRinsu"] * p["Rinsu0"]
                           + p["KappaRinsuPotn"] * d["Potn0"])
                          / (p["KappaRinsu"] + p["EMME1"] * d["Potn0"]))
    d["Secr0"] = p["EMME1"] * d["Ptgt0"] * d["InitialRinsu0"]
    d["GlucPV0"] = Gh0 - p["GammaBPGU"] / p["QfloGP"]
    d["GlucK0"] = Gh0
    d["GlucBV0"] = Gh0 - p["GammaBGU"] / p["QfloGB"]
    d["GlucJ0"] = Gh0 - p["GammaJGU"] / p["QfloGJ"]
    d["GlucL0"] = (p["QfloGA"] * Gh0 + p["QfloGJ"] * d["GlucJ0"]
                   + p["GammaHGP0"] - p["GammaHGU0"]) / p["QfloGL"]
    d["GlucBI0"] = d["GlucBV0"] - (p["GammaBGU"] * p["TdifB"]) / p["VolBI"]
    d["GlucPI0"] = d["GlucPV0"] - p["GammaBPGU"] * p["TdifGP"] / p["VolPI"]
    d["MIPGU0"] = p["beta0PGU"] + p["beta1PGU"] * np.tanh(p["beta2PGU"] * (1.0 - p["beta3PGU"]))
    d["MC0HGP0"] = p["beta0HGP"] * np.tanh(p["beta1HGP"])
    d["MCHGP0"] = d["MC0HGP0"] - p["Func20"]
    d["MIHGPinf0"] = p["beta2HGP"] - p["beta3HGP"] * np.tanh(p["beta4HGP"] * (1.0 - p["beta5HGP"]))
    d["MIHGP0"] = d["MIHGPinf0"]
    d["MGHGP0"] = p["beta6HGP"] - p["beta7HGP"] * np.tanh(p["beta8HGP"] * (1.0 - p["beta9HGP"]))
    d["MIHGUinf0"] = p["beta0HGU"] * np.tanh(p["beta1HGU"])
    d["MIHGU0"] = d["MIHGUinf0"]
    d["MGHGU0"] = p["beta2HGU"] + p["beta3HGU"] * np.tanh(p["beta4HGU"] * (1.0 - p["beta5HGU"]))
    GlucK0 = Gh0
    d["GammaKGE0"] = ((GlucK0 < p["beta3KGE"])
                      * (p["beta0KGE"] + p["beta1KGE"] * np.tanh(p["beta2KGE"] * (GlucK0 - p["beta3KGE"])))
                      + (GlucK0 >= p["beta3KGE"]) * (-p["beta4KGE"] + p["beta5KGE"] * GlucK0))
    d["GammaLIC0"] = p["FracLIC"] * (p["QfloIA"] * InsuH0 + p["QfloIJ"] * InsuH0 + d["GammaBPIR"])
    d["GammaKIC0"] = p["FracKIC"] * p["QfloIK"] * InsuH0
    d["MGPCR0"] = p["beta0PCR"] - p["beta1PCR"] * np.tanh(p["beta2PCR"] * (1.0 - p["beta3PCR"]))
    d["MIPCR0"] = p["beta4PCR"] - p["beta5PCR"] * np.tanh(p["beta6PCR"] * (1.0 - p["beta7PCR"]))
    d["GammaPCC0"] = p["Cgon0"] * p["GammaMCC"]
    d["GammaBPCR"] = d["GammaPCC0"]
    return d


def initial_state(p: dict) -> np.ndarray:
    """Full 26-state initial condition at the basal steady state."""
    d = derived_params(p)
    y = np.zeros(len(STATE_NAMES))
    vals = {
        "GlucBV": d["GlucBV0"], "GlucBI": d["GlucBI0"], "GlucH": p["GlucH0"],
        "GlucJ": d["GlucJ0"], "GlucL": d["GlucL0"], "GlucK": d["GlucK0"],
        "GlucPV": d["GlucPV0"], "GlucPI": d["GlucPI0"],
        "MIHGP": d["MIHGP0"], "Fun2": p["Func20"], "MIHGU": d["MIHGU0"],
        "InsuB": d["InsuB0"], "InsuH": d["InsuH0"], "InsuJ": d["InsuJ0"],
        "InsuL": d["InsuL0"], "InsuK": d["InsuK0"],
        "InsuPV": p["InsuPV0"], "InsuPI": d["InsuPI0"],
        "Potn": d["Potn0"], "Pinh": d["Pinh0"], "Rinsu": d["InitialRinsu0"],
        "Cgon": p["Cgon0"],
        "Sto": 0.0, "Jej": 0.0, "Rit": 0.0, "Ile": 0.0,
    }
    for name, v in vals.items():
        y[STATE_INDEX[name]] = v
    return y


def rhs(t: float, y: np.ndarray, p: dict, mods: dict | None = None) -> np.ndarray:
    """Right-hand side of the unified model.

    `mods` is an optional dict of intervention multipliers applied to named
    signals (see interventions.py). Keys:
      insulin_pgu, insulin_hgp, insulin_hgu, glucagon_hgp - signalling
        efficacy factors s(u): action multiplier becomes 1 + s*(M - 1)
        (s=1 baseline, s>1 potentiation, s=0 complete ablation)
      insulin_secretion, glucagon_secretion   - direct secretion-rate factors
    """
    d = p if "GammaBPIR" in p else derived_params(p)

    (GlucBV, GlucBI, GlucH, GlucJ, GlucL, GlucK, GlucPV, GlucPI,
     MIHGP, Fun2, MIHGU,
     InsuB, InsuH, InsuJ, InsuL, InsuK, InsuPV, InsuPI,
     Potn, Pinh, Rinsu, Cgon,
     Sto, Jej, Rit, Ile) = y

    GlucNH = GlucH / d["GlucH0"]
    GlucNL = GlucL / d["GlucL0"]
    GlucNPI = GlucPI / d["GlucPI0"]
    InsuNH = InsuH / d["InsuH0"]
    InsuNL = InsuL / d["InsuL0"]
    InsuNPI = InsuPI / d["InsuPI0"]
    CgonN = Cgon / d["Cgon0"]

    m = mods or {}
    # intervention semantics: each signalling-efficacy factor s(u) rescales the
    # DEVIATION of the hormone's action multiplier from its neutral value 1:
    #     M_eff = 1 + s(u) * (M - 1)
    # u=0 -> s=1 (baseline); potentiation amplifies the hormone's effect;
    # inhibition drives the effect to zero (floor CLIP keeps it physical).
    CLIP = 0.05
    s_pgu = m.get("insulin_pgu", 1.0)
    s_hgp = m.get("insulin_hgp", 1.0)
    s_hgu = m.get("insulin_hgu", 1.0)
    s_cgp = m.get("glucagon_hgp", 1.0)

    secr_scale = m.get("insulin_secretion", 1.0)
    pcr_scale = m.get("glucagon_secretion", 1.0)

    # --- algebraic metabolic terms ---
    MIPGU_raw = d["beta0PGU"] + d["beta1PGU"] * np.tanh(d["beta2PGU"] * (InsuNPI - d["beta3PGU"]))
    MIPGU = max(CLIP, 1.0 + s_pgu * (MIPGU_raw - 1.0))
    GammaPGU = d["GammaBPGU"] * GlucNPI * MIPGU

    MIHGPinf_raw = d["beta2HGP"] - d["beta3HGP"] * np.tanh(d["beta4HGP"] * (InsuNL - d["beta5HGP"]))
    MIHGPinf = max(CLIP, 1.0 + s_hgp * (MIHGPinf_raw - 1.0))
    MC0HGP = d["beta0HGP"] * np.tanh(d["beta1HGP"] * CgonN)
    MCHGP_raw = MC0HGP - Fun2
    MCHGP = max(CLIP, 1.0 + s_cgp * (MCHGP_raw - 1.0))
    MGHGP = d["beta6HGP"] - d["beta7HGP"] * np.tanh(d["beta8HGP"] * (GlucNL - d["beta9HGP"]))
    GammaHGP = d["GammaHGP0"] * MIHGP * MCHGP * MGHGP

    MIHGUinf_raw = d["beta0HGU"] * np.tanh(d["beta1HGU"] * InsuNL)
    MIHGUinf = max(CLIP, 1.0 + s_hgu * (MIHGUinf_raw - 1.0))
    MGHGU = d["beta2HGU"] + d["beta3HGU"] * np.tanh(d["beta4HGU"] * (GlucNL - d["beta5HGU"]))
    GammaHGU = d["GammaHGU0"] * MIHGU * MGHGU

    if GlucK < d["beta3KGE"]:
        GammaKGE = d["beta0KGE"] + d["beta1KGE"] * np.tanh(d["beta2KGE"] * (GlucK - d["beta3KGE"]))
    else:
        GammaKGE = -d["beta4KGE"] + d["beta5KGE"] * GlucK

    # insulin secretion (potentiator/inhibitor/labile-pool)
    Pprp = GlucH ** d["beta1PIR"] / (d["beta2PIR"] ** d["beta1PIR"]
                                     + d["beta3PIR"] * GlucH ** d["beta4PIR"])
    Ptgt = Pprp ** d["beta5PIR"]
    if Pprp > Pinh:
        Secr = (d["EMME1"] * Ptgt + d["EMME2"] * (Pprp - Pinh)) * Rinsu
    else:
        Secr = d["EMME1"] * Ptgt * Rinsu
    Secr *= secr_scale
    SecrN = Secr / d["Secr0"]
    GammaPIR = SecrN * d["GammaBPIR"]
    GammaLIC = d["FracLIC"] * (d["QfloIA"] * InsuH + d["QfloIJ"] * InsuJ + GammaPIR)
    GammaKIC = d["FracKIC"] * d["QfloIK"] * InsuH
    GammaPIC = InsuPI / (((1.0 - d["FracPIC"]) / d["FracPIC"]) * (1.0 / d["QfloIP"])
                          - d["TdifIP"] / d["VolPI"])

    # glucagon secretion (glucose- and insulin-controlled) and clearance
    MGPCR = d["beta0PCR"] - d["beta1PCR"] * np.tanh(d["beta2PCR"] * (GlucNH - d["beta3PCR"]))
    MIPCR = d["beta4PCR"] - d["beta5PCR"] * np.tanh(d["beta6PCR"] * (InsuNH - d["beta7PCR"]))
    GammaPCR = d["GammaBPCR"] * MGPCR * MIPCR * pcr_scale
    GammaPCC = d["GammaMCC"] * Cgon

    # exogenous inputs
    GammaIVG = d["GammaIVG0"] + (d["GammaIVGin"]
                                 * float(d["TimeIVG"] <= t <= d["TimeIVGend"]))
    GammaIVI = d["GammaIVI0"] + (d["GammaIVIin"]
                                 * float(d["TimeIVI"] <= t <= d["TimeIVIend"]))
    Roga = d["frac"] * (d["kgj"] * Jej + d["kgl"] * Ile)

    # --- derivatives ---
    dy = np.empty_like(y)
    dy[0] = (GlucH - GlucBV) * d["QfloGB"] / d["VolGBV"] \
        - d["VolBI"] / (d["TdifB"] * d["VolGBV"]) * (GlucBV - GlucBI)
    dy[1] = (GlucBV - GlucBI) / d["TdifB"] - d["GammaBGU"] / d["VolBI"]
    dy[2] = (d["QfloGB"] * GlucBV + d["QfloGL"] * GlucL + d["QfloGK"] * GlucK
             + d["QfloGP"] * GlucPV - d["QfloGH"] * GlucH - d["GammaRBCU"]
             + GammaIVG) / d["VolGH"]
    dy[3] = (GlucH - GlucJ) * d["QfloGJ"] / d["VolGJ"] - d["GammaJGU"] / d["VolGJ"] \
        + Roga / d["VolGJ"]
    dy[4] = (d["QfloGA"] * GlucH + d["QfloGJ"] * GlucJ - d["QfloGL"] * GlucL
             + GammaHGP - GammaHGU) / d["VolGL"]
    dy[5] = (GlucH - GlucK) * d["QfloGK"] / d["VolGK"] - GammaKGE / d["VolGK"]
    dy[6] = d["QfloGP"] / d["VolGPV"] * (GlucH - GlucPV) \
        - d["VolPI"] / (d["TdifGP"] * d["VolGPV"]) * (GlucPV - GlucPI)
    dy[7] = (GlucPV - GlucPI) / d["TdifGP"] - GammaPGU / d["VolPI"]
    dy[8] = (MIHGPinf - MIHGP) / d["tauInsu"]
    dy[9] = ((MC0HGP - 1.0) / 2.0 - Fun2) / d["tauCgon"]
    dy[10] = (MIHGUinf - MIHGU) / d["tauInsu"]
    dy[11] = d["QfloIB"] / d["VolIB"] * (InsuH - InsuB)
    dy[12] = (d["QfloIB"] * InsuB + d["QfloIL"] * InsuL + d["QfloIK"] * InsuK
              + d["QfloIP"] * InsuPV - d["QfloIH"] * InsuH + GammaIVI) / d["VolIH"]
    dy[13] = d["QfloIJ"] / d["VolIJ"] * (InsuH - InsuJ)
    dy[14] = (d["QfloIA"] * InsuH + d["QfloIJ"] * InsuJ - d["QfloIL"] * InsuL
              + GammaPIR - GammaLIC) / d["VolIL"]
    dy[15] = d["QfloIK"] / d["VolIK"] * (InsuH - InsuK) - GammaKIC / d["VolIK"]
    dy[16] = d["QfloIP"] / d["VolIPV"] * (InsuH - InsuPV) \
        - d["VolPI"] / (d["VolIPV"] * d["TdifIP"]) * (InsuPV - InsuPI)
    dy[17] = (InsuPV - InsuPI) / d["TdifIP"] - GammaPIC / d["VolPI"]
    dy[18] = d["KappaPotnPtgt"] * (Ptgt - Potn)
    dy[19] = d["KappaPinhPrp"] * (Pprp - Pinh)
    dy[20] = d["KappaRinsu"] * (d["Rinsu0"] - Rinsu) + d["KappaRinsuPotn"] * Potn - Secr
    dy[21] = (GammaPCR - GammaPCC) / d["VolC"]
    dy[22] = -d["kjs"] * Sto
    dy[23] = d["kjs"] * Sto - d["kgj"] * Jej - d["krj"] * Jej
    dy[24] = -d["klr"] * Rit + d["krj"] * Jej
    dy[25] = d["klr"] * Rit - d["kgl"] * Ile
    return dy


def simulate(params: dict | None = None, t_eval: np.ndarray | None = None,
             mods: dict | None = None, t_span: tuple[float, float] | None = None,
             oral_dose_mmol: float | None = None, dose_time: float = 0.0,
             rtol: float = 1e-7, atol: float = 1e-9):
    """Integrate the model. Returns (t, Y) with Y[:,i] per STATE_NAMES.

    The oral dose is applied as a Dirac jump Sto += Dose at t == dose_time
    (implemented by splitting the integration at dose_time), matching the
    upstream ComputeDiracs semantics.
    """
    from scipy.integrate import solve_ivp

    p = dict(BASE_PARAMS)
    if params:
        p.update(params)
    p = derived_params(p)
    y0 = initial_state(p)
    t0 = p["Tzero"]
    t1 = p["Tend"] if t_span is None else t_span[1]
    if t_span is not None:
        t0 = t_span[0]

    if oral_dose_mmol:
        p = dict(p)
        # piecewise integration across the dose instant
        segs = [(t0, dose_time), (dose_time, t1)]
        ts, ys = [], []
        for k, (a, b) in enumerate(segs):
            if b <= a:
                continue
            sol = solve_ivp(lambda t, y: rhs(t, y, p, mods), (a, b), y0,
                            method="LSODA", rtol=rtol, atol=atol,
                            dense_output=False,
                            t_eval=None)
            if not sol.success:
                raise RuntimeError(f"solver failed: {sol.message}")
            if k == 0:
                # jump at dose_time
                y0 = sol.y[:, -1].copy()
                y0[STATE_INDEX["Sto"]] += oral_dose_mmol
            ts.append(sol.t)
            ys.append(sol.y)
        t = np.concatenate(ts)
        Y = np.concatenate(ys, axis=1)
    else:
        sol = solve_ivp(lambda t, y: rhs(t, y, p, mods), (t0, t1), y0,
                        method="LSODA", rtol=rtol, atol=atol)
        if not sol.success:
            raise RuntimeError(f"solver failed: {sol.message}")
        t, Y = sol.t, sol.y

    if t_eval is not None:
        from scipy.interpolate import interp1d
        f = interp1d(t, Y, kind="linear", axis=1, bounds_error=False,
                     fill_value="extrapolate")
        Y = f(t_eval)
        t = t_eval
    return t, Y


def algebraics(y: np.ndarray, p: dict, mods: dict | None = None) -> dict:
    """Recompute diagnostic algebraic quantities at a given state."""
    d = p if "GammaBPIR" in p else derived_params(p)
    names = STATE_NAMES
    v = {n: y[STATE_INDEX[n]] for n in names}
    GlucNH = v["GlucH"] / d["GlucH0"]; GlucNL = v["GlucL"] / d["GlucL0"]
    GlucNPI = v["GlucPI"] / d["GlucPI0"]
    InsuNH = v["InsuH"] / d["InsuH0"]; InsuNL = v["InsuL"] / d["InsuL0"]
    InsuNPI = v["InsuPI"] / d["InsuPI0"]
    CgonN = v["Cgon"] / d["Cgon0"]
    m = mods or {}
    CLIP = 0.05
    MIPGU_raw = d["beta0PGU"] + d["beta1PGU"] * np.tanh(d["beta2PGU"] * (InsuNPI - d["beta3PGU"]))
    MIPGU = max(CLIP, 1.0 + m.get("insulin_pgu", 1.0) * (MIPGU_raw - 1.0))
    GammaPGU = d["GammaBPGU"] * GlucNPI * MIPGU
    MIHGPinf_raw = d["beta2HGP"] - d["beta3HGP"] * np.tanh(d["beta4HGP"] * (InsuNL - d["beta5HGP"]))
    MIHGPinf = max(CLIP, 1.0 + m.get("insulin_hgp", 1.0) * (MIHGPinf_raw - 1.0))
    MC0HGP = d["beta0HGP"] * np.tanh(d["beta1HGP"] * CgonN)
    MCHGP_raw = MC0HGP - v["Fun2"]
    MCHGP = max(CLIP, 1.0 + m.get("glucagon_hgp", 1.0) * (MCHGP_raw - 1.0))
    MGHGP = d["beta6HGP"] - d["beta7HGP"] * np.tanh(d["beta8HGP"] * (GlucNL - d["beta9HGP"]))
    GammaHGP = d["GammaHGP0"] * v["MIHGP"] * MCHGP * MGHGP
    MIHGUinf_raw = d["beta0HGU"] * np.tanh(d["beta1HGU"] * InsuNL)
    MIHGUinf = max(CLIP, 1.0 + m.get("insulin_hgu", 1.0) * (MIHGUinf_raw - 1.0))
    MGHGU = d["beta2HGU"] + d["beta3HGU"] * np.tanh(d["beta4HGU"] * (GlucNL - d["beta5HGU"]))
    GammaHGU = d["GammaHGU0"] * v["MIHGU"] * MGHGU
    Pprp = v["GlucH"] ** d["beta1PIR"] / (d["beta2PIR"] ** d["beta1PIR"] + d["beta3PIR"] * v["GlucH"] ** d["beta4PIR"])
    Ptgt = Pprp ** d["beta5PIR"]
    Secr = ((d["EMME1"] * Ptgt + d["EMME2"] * (Pprp - v["Pinh"])) if Pprp > v["Pinh"]
            else d["EMME1"] * Ptgt) * v["Rinsu"] * m.get("insulin_secretion", 1.0)
    GammaPIR = (Secr / d["Secr0"]) * d["GammaBPIR"]
    MGPCR = d["beta0PCR"] - d["beta1PCR"] * np.tanh(d["beta2PCR"] * (GlucNH - d["beta3PCR"]))
    MIPCR = d["beta4PCR"] - d["beta5PCR"] * np.tanh(d["beta6PCR"] * (InsuNH - d["beta7PCR"]))
    GammaPCR = d["GammaBPCR"] * MGPCR * MIPCR * m.get("glucagon_secretion", 1.0)
    Roga = d["frac"] * (d["kgj"] * v["Jej"] + d["kgl"] * v["Ile"])
    return dict(GlucNH=GlucNH, GlucNL=GlucNL, GlucNPI=GlucNPI, InsuNH=InsuNH,
                InsuNL=InsuNL, InsuNPI=InsuNPI, CgonN=CgonN, MIPGU=MIPGU,
                GammaPGU=GammaPGU, MIHGPinf=MIHGPinf, MC0HGP=MC0HGP, MCHGP=MCHGP,
                MGHGP=MGHGP, GammaHGP=GammaHGP, MIHGUinf=MIHGUinf, MGHGU=MGHGU,
                GammaHGU=GammaHGU, Secr=Secr, GammaPIR=GammaPIR, MGPCR=MGPCR,
                MIPCR=MIPCR, GammaPCR=GammaPCR, Roga=Roga)
