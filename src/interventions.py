"""Intervention framework — uniform modulation convention.

CONVENTION (non-negotiable, see docs/DESIGN.md):
    u = 0  -> no exogenous modulation (baseline, multiplier = 1)
    u = 1  -> defined maximum modulation
For every intervention a monotone factor f(u) sets the *action efficacy* s:
    potentiation (agonist-like):  f(u) = 1 + u*(GMAX - 1),   GMAX > 1
    inhibition   (antagonist-like): f(u) = 1 - u*(1 - GMIN), GMIN in [0,1)
For signalling interventions the model applies s to the deviation of the
hormone-action multiplier from neutral: M_eff = 1 + s*(M - 1) (s=1 baseline,
s>1 amplified action, s=0 complete ablation). Secretion interventions scale
the secretion rate directly. u therefore always increases the *strength* of
modulation, never reverses direction. `native_parameter_value` = f(u).
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Intervention:
    name: str
    label: str
    mod_key: str            # multiplier key understood by sorensen_model.rhs
    mode: str               # 'potentiation' | 'inhibition'
    gmax: float             # f(u=1): >1 for potentiation, in [0,1) for inhibition
    description: str = ""

    def factor(self, u: float) -> float:
        if not 0.0 <= u <= 1.0:
            raise ValueError("u must lie in [0,1]")
        if self.mode == "potentiation":
            return 1.0 + u * (self.gmax - 1.0)
        if self.mode == "inhibition":
            return 1.0 - u * (1.0 - self.gmax)
        raise ValueError(self.mode)

    def mods(self, u: float) -> dict:
        return {k: self.factor(u) for k in self.mod_key.split("+")}


GMAX = 3.0   # defined maximum for potentiation = 3x baseline signal efficacy
GMIN = 0.0   # defined maximum for inhibition = complete loss of signal

INTERVENTIONS = {
    # --- Experiment A: insulin signalling efficacy ---
    "insulin_signal_peripheral": Intervention(
        "insulin_signal_peripheral", "Insulin signalling (peripheral uptake)",
        "insulin_pgu", "potentiation", GMAX,
        "Scales the insulin signal driving peripheral glucose uptake (MIPGU)."),
    "insulin_signal_hepatic": Intervention(
        "insulin_signal_hepatic", "Insulin signalling (hepatic: HGP + HGU)",
        "insulin_hgp+insulin_hgu", "potentiation", GMAX,
        "Scales insulin action on hepatic glucose production and uptake."),
    "insulin_signal_global": Intervention(
        "insulin_signal_global", "Insulin signalling (global)",
        "insulin_pgu+insulin_hgp+insulin_hgu", "potentiation", GMAX,
        "Scales insulin action at all sites simultaneously."),
    "insulin_signal_global_inhibition": Intervention(
        "insulin_signal_global_inhibition", "Insulin signalling inhibition",
        "insulin_pgu+insulin_hgp+insulin_hgu", "inhibition", GMIN,
        "Scales insulin action downward; u=1 is complete insulin resistance."),
    # --- Experiment B: glucagon signalling efficacy ---
    "glucagon_signal_hepatic": Intervention(
        "glucagon_signal_hepatic", "Glucagon signalling (hepatic HGP)",
        "glucagon_hgp", "potentiation", GMAX,
        "Scales the glucagon signal driving hepatic glucose production."),
    "glucagon_signal_inhibition": Intervention(
        "glucagon_signal_inhibition", "Glucagon signalling inhibition",
        "glucagon_hgp", "inhibition", GMIN,
        "u=1 abolishes glucagon stimulation of HGP."),
    # --- Experiment C: insulin secretion capacity ---
    "insulin_secretion": Intervention(
        "insulin_secretion", "Beta-cell insulin secretion capacity",
        "insulin_secretion", "potentiation", GMAX,
        "Scales pancreatic insulin release rate."),
    "insulin_secretion_inhibition": Intervention(
        "insulin_secretion_inhibition", "Beta-cell secretion impairment",
        "insulin_secretion", "inhibition", GMIN,
        "u=1 abolishes endogenous insulin secretion (T1DM limit)."),
    # --- Experiment D: glucagon secretion capacity ---
    "glucagon_secretion": Intervention(
        "glucagon_secretion", "Alpha-cell glucagon secretion capacity",
        "glucagon_secretion", "potentiation", GMAX,
        "Scales pancreatic glucagon release rate."),
    "glucagon_secretion_inhibition": Intervention(
        "glucagon_secretion_inhibition", "Glucagon secretion suppression",
        "glucagon_secretion", "inhibition", GMIN,
        "u=1 abolishes endogenous glucagon secretion."),
}

PRIMARY_INTERVENTIONS = [
    "insulin_signal_global", "glucagon_signal_hepatic",
    "insulin_secretion", "glucagon_secretion",
]
INHIBITION_INTERVENTIONS = [
    "insulin_signal_global_inhibition", "glucagon_signal_inhibition",
    "insulin_secretion_inhibition", "glucagon_secretion_inhibition",
]
ALL_INTERVENTIONS = PRIMARY_INTERVENTIONS + INHIBITION_INTERVENTIONS + [
    "insulin_signal_peripheral", "insulin_signal_hepatic",
]
