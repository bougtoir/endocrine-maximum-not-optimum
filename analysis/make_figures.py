"""Generate all manuscript figures into results/figures/ (PNG, 300 dpi,
separate files per journal figure policy — not embedded in manuscript)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sorensen_model as sm
from interventions import INTERVENTIONS, ALL_INTERVENTIONS
from challenges import CHALLENGES
from endpoints import glucose_series, insulin_series, glucagon_series

R = os.path.join(os.path.dirname(__file__), "..", "results")
FIG = os.path.join(R, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 9, "axes.titlesize": 9, "figure.dpi": 300,
                     "savefig.dpi": 300, "axes.spines.top": False,
                     "axes.spines.right": False})

LABEL = {
    "insulin_signal_peripheral": "Insulin signal ↑ (periph.)",
    "insulin_signal_hepatic": "Insulin signal ↑ (hepatic)",
    "insulin_signal_global": "Insulin signal ↑ (global)",
    "insulin_signal_global_inhibition": "Insulin signal ↓",
    "glucagon_signal_hepatic": "Glucagon signal ↑",
    "glucagon_signal_inhibition": "Glucagon signal ↓",
    "insulin_secretion": "Insulin secretion ↑",
    "insulin_secretion_inhibition": "Insulin secretion ↓",
    "glucagon_secretion": "Glucagon secretion ↑",
    "glucagon_secretion_inhibition": "Glucagon secretion ↓",
}
CH_LABEL = {"fasting": "Prolonged fasting", "ivgtt": "IVGTT",
            "ogtt": "OGTT (100 g)", "ivitt": "IVITT", "civii": "IV insulin infusion"}


def fig1_validation():
    """OGTT validation overlay: model vs upstream Data.xlsx."""
    xl = os.path.join(os.path.dirname(__file__), "..", "models", "primary",
                      "upstream", "Data.xlsx")
    dat = pd.read_excel(xl, header=0)
    t, Y = sm.simulate(oral_dose_mmol=555.56, dose_time=0.0, t_span=(-30, 300))
    g = glucose_series(t, Y); ins = insulin_series(t, Y)
    p = sm.derived_params(sm.BASE_PARAMS)
    pir = np.array([sm.algebraics(Y[:, i], p, None)["GammaPIR"]
                    for i in range(len(t))]) / 6.944
    d1 = dat[dat.VARIABLE == 1]; d2 = dat[dat.VARIABLE == 2]
    d3 = dat[dat.VARIABLE == 3]
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    ax[0].plot(t, g, "k-", lw=1.2, label="Model")
    ax[0].plot(d1.TIME, d1.VALUE, "o", ms=3, c="tab:red", label="Data")
    ax[0].set_ylabel("Glucose (mg/dL)")
    ax[1].plot(t, ins, "k-", lw=1.2)
    ax[1].plot(d2.TIME, d2.VALUE, "o", ms=3, c="tab:red")
    ax[1].set_ylabel("Insulin (mU/L)")
    ax[2].plot(t, pir, "k-", lw=1.2)
    ax[2].plot(d3.TIME, d3.VALUE, "o", ms=3, c="tab:red")
    ax[2].set_ylabel("Insulin release (mU/min)")
    for a in ax:
        a.set_xlabel("Time (min)"); a.axvline(0, c="0.7", lw=0.6)
    ax[0].legend(frameon=False)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig1_validation.png"); plt.close(fig)


def fig2_convention():
    """u-convention + factor curves."""
    u = np.linspace(0, 1, 100)
    fig, ax = plt.subplots(1, 2, figsize=(6.4, 2.4))
    ax[0].plot(u, 1 + u * 2, "k-", label="Potentiation f(u)=1+2u")
    ax[0].plot(u, 1 - u, "k--", label="Inhibition f(u)=1-u")
    ax[0].set_xlabel("u (modulation fraction)"); ax[0].set_ylabel("Factor f(u)")
    ax[0].legend(frameon=False)
    ax[0].set_title("A  Intervention convention")
    s = np.array([1.0, 3.0, 0.0])
    M = np.linspace(0.5, 1.5, 100)
    for si, lab, c in [(1.0, "s=1 baseline", "k"), (3.0, "s=3 pot.", "tab:blue"),
                       (0.0, "s=0 ablated", "tab:red")]:
        ax[1].plot(M, 1 + si * (M - 1), c=c, label=lab)
    ax[1].plot(M, M, ":", c="0.6")
    ax[1].set_xlabel("Native action multiplier M")
    ax[1].set_ylabel("Effective M_eff = 1 + s(M−1)")
    ax[1].legend(frameon=False, fontsize=7)
    ax[1].set_title("B  Action-efficacy semantics")
    fig.tight_layout(); fig.savefig(f"{FIG}/fig2_convention.png"); plt.close(fig)


def fig3_loss_curves():
    sc = pd.read_csv(f"{R}/scans/full_endpoints.csv")
    fig, axes = plt.subplots(2, 3, figsize=(7.6, 4.8), sharex=True)
    chs = ["fasting", "ivgtt", "ogtt", "ivitt", "civii"]
    for ax, ch in zip(axes.flat, chs):
        for ivn in ALL_INTERVENTIONS:
            sub = sc[(sc.intervention == ivn) & (sc.challenge == ch)]
            ax.plot(sub.modulation_fraction, sub.composite_loss, lw=0.9,
                    label=LABEL[ivn])
        ax.set_title(CH_LABEL[ch]); ax.set_xlabel("u"); ax.set_ylabel("L(u)")
        ax.axvline(0, c="0.7", lw=0.5)
    axes.flat[-1].axis("off")
    axes.flat[-1].legend(*axes.flat[1].get_legend_handles_labels(),
                         loc="center", frameon=False, fontsize=6.5)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig3_loss_curves.png"); plt.close(fig)


def fig4_trajectories():
    """Glucose trajectories at u=0, u*, u=1 for the headline cases."""
    cases = [
        ("insulin_secretion_inhibition", "ivgtt", 0.83),
        ("insulin_signal_global_inhibition", "ivgtt", 0.71),
        ("glucagon_secretion_inhibition", "ogtt", 0.88),
        ("insulin_secretion", "civii", 0.51),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 4.6))
    for ax, (ivn, ch, ustar) in zip(axes.flat, cases):
        chd = CHALLENGES[ch]
        for u, c, lab in [(0.0, "0.5", "u=0 (baseline)"),
                          (ustar, "tab:blue", f"u*={ustar}"),
                          (1.0, "tab:red", "u=1 (max)")]:
            t, Y = sm.simulate(params=chd["params"],
                               mods=INTERVENTIONS[ivn].mods(u),
                               t_span=chd["t_span"],
                               oral_dose_mmol=chd.get("oral_dose_mmol"),
                               dose_time=chd.get("dose_time", 0.0),
                               t_eval=np.arange(chd["t_span"][0], chd["t_span"][1], 1.0))
            ax.plot(t, glucose_series(t, Y), c=c, lw=1.1, label=lab)
        ax.axhline(70, c="0.6", lw=0.6, ls="--")
        ax.axhline(140, c="0.6", lw=0.6, ls="--")
        ax.set_title(f"{LABEL[ivn]} × {CH_LABEL[ch]}")
        ax.set_xlabel("Time (min)"); ax.set_ylabel("Glucose (mg/dL)")
    axes.flat[0].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig4_trajectories.png"); plt.close(fig)


def fig5_mechanism():
    fn = f"{R}/feedback/insulin_secretion_inhibition__ivgtt.csv"
    df = pd.read_csv(fn)
    fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.4))
    for u, c in [(0.0, "0.5"), (0.8, "tab:blue"), (1.0, "tab:red")]:
        sub = df[(df.u == u) & (df.t >= 0)]
        ax[0].plot(sub.t, sub.insulin_mU_L, c=c, lw=1.0)
        ax[1].plot(sub.t, sub.glucagon_pM, c=c, lw=1.0)
        ax[2].plot(sub.t, sub.GammaHGP, c=c, lw=1.0, label=f"u={u}")
    ax[0].set_ylabel("Insulin (mU/L)"); ax[1].set_ylabel("Glucagon (pM)")
    ax[2].set_ylabel("Γ_HGP (mmol/min)")
    for a in ax: a.set_xlabel("Time (min)")
    ax[2].legend(frameon=False, fontsize=7)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig5_mechanism.png"); plt.close(fig)


def fig6_pareto():
    pf = pd.read_csv(f"{R}/robustness/pareto_fronts.csv")
    sub = pf[pf["axes"] == "hypo_burden_mgdl_min|hyper_burden_mgdl_min"]
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    for (ivn, ch), g in sub.groupby(["intervention", "challenge"]):
        g = g.sort_values("hypo_burden_mgdl_min")
        ax.plot(g["hyper_burden_mgdl_min"], g["hypo_burden_mgdl_min"], "o-",
                ms=3, lw=0.8, label=f"{LABEL[ivn]} × {ch.upper()}")
        for _, r in g.iterrows():
            ax.annotate(f"{r.u:.2f}", (r["hyper_burden_mgdl_min"],
                        r["hypo_burden_mgdl_min"]), fontsize=5)
    ax.set_xlabel("Hyperglycaemic burden (mg/dL·min)")
    ax.set_ylabel("Hypoglycaemic burden (mg/dL·min)")
    ax.legend(frameon=False, fontsize=6)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig6_pareto.png"); plt.close(fig)


def fig7_weights():
    ws = pd.read_csv(f"{R}/robustness/weight_sensitivity.csv")
    key = ws[ws.perturbation != "default"]
    perts = sorted(key.perturbation.unique())
    cases = sorted(set(zip(key.intervention, key.challenge)))
    M = np.full((len(cases), len(perts)), np.nan)
    C = np.empty((len(cases), len(perts)), dtype=object)
    for i, (ivn, ch) in enumerate(cases):
        for j, pt in enumerate(perts):
            r = key[(key.intervention == ivn) & (key.challenge == ch)
                    & (key.perturbation == pt)]
            if len(r):
                M[i, j] = r.u_opt.iloc[0]; C[i, j] = r.response_class.iloc[0]
    fig, ax = plt.subplots(figsize=(6.8, 3.2))
    im = ax.imshow(M, cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(perts))); ax.set_xticklabels(perts, rotation=90, fontsize=6)
    ax.set_yticks(range(len(cases)))
    ax.set_yticklabels([f"{LABEL[i]} × {c}" for i, c in cases], fontsize=7)
    for i in range(len(cases)):
        for j in range(len(perts)):
            ax.text(j, i, C[i, j].replace("Type", "T"), ha="center",
                    va="center", fontsize=5, color="w")
    fig.colorbar(im, label="u*")
    fig.tight_layout(); fig.savefig(f"{FIG}/fig7_weights.png"); plt.close(fig)


def fig8_disease():
    cl = pd.read_csv(f"{R}/disease/disease_classification.csv")
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4), sharex=True)
    for ax, state in zip(axes, ["healthy", "t2dm", "t1dm"]):
        if state == "healthy":
            df_all = pd.read_csv(f"{R}/scans/full_endpoints.csv")
            dd = df_all[df_all.challenge == "ogtt"]
            for ivn in ALL_INTERVENTIONS:
                s = dd[dd.intervention == ivn]
                ax.plot(s.modulation_fraction, s.composite_loss, lw=0.9,
                        label=LABEL[ivn])
            ax.set_title("Healthy baseline")
        else:
            for ivn in ALL_INTERVENTIONS:
                fn = f"{R}/disease/{state}_{ivn}__ogtt.csv"
                if os.path.exists(fn):
                    s = pd.read_csv(fn)
                    ax.plot(s.modulation_fraction, s.composite_loss, lw=0.9,
                            label=LABEL[ivn])
            ax.set_title(state.upper())
        ax.set_xlabel("u"); ax.set_ylabel("L(u)")
    axes[-1].legend(frameon=False, fontsize=5.5, loc="upper right")
    fig.tight_layout(); fig.savefig(f"{FIG}/fig8_disease.png"); plt.close(fig)


if __name__ == "__main__":
    fig1_validation(); print("fig1 ok")
    fig2_convention(); print("fig2 ok")
    fig3_loss_curves(); print("fig3 ok")
    fig4_trajectories(); print("fig4 ok")
    fig5_mechanism(); print("fig5 ok")
    fig6_pareto(); print("fig6 ok")
    fig7_weights(); print("fig7 ok")
    fig8_disease(); print("fig8 ok")
