"""Gate C3 Stage 1: structured grid for the single candidate prediction from C2 case (a):
'the endogenous secretory gain at which the OGTT nadir reaches 70 mg/dL (u70), and the composite
optimum u*, decrease as insulin-action delay lengthens'. Composite-free primary quantity: u70."""
import numpy as np, pandas as pd, itertools
from multiprocessing import Pool
import gate_c_common as G
from gate_c2_mechanism import sim

B = G.sm.BASE_PARAMS
TAU = [0.5, 0.75, 1.0, 1.5, 2.0]
BASAL = {"82.4": None, "90": B["GlucH0"] * 90.0 / 82.40}
DOSE = {"50g": 277.78, "75g": 416.67, "100g": 555.56}
KPP = [0.5, 1.0, 2.0]   # potentiator rate multiplier (Stage 1 OAT at reference basal/dose only)


def u_cross(u, x, level=70.0):
    for i in range(1, len(u)):
        if x[i - 1] >= level > x[i]:
            return float(u[i - 1] + (x[i - 1] - level) * (u[i] - u[i - 1]) / (x[i - 1] - x[i]))
    return np.nan if x[0] >= level else 0.0


def job(a):
    tau, bk, dk, kp = a
    ov = {"tauInsu": B["tauInsu"] * tau, "KappaPotnPtgt": B["KappaPotnPtgt"] * kp}
    if BASAL[bk]:
        ov["GlucH0"] = BASAL[bk]
    nad, pk, L, b70 = [], [], [], []
    for u in G.U_GRID:
        t, Y, Yo, d = sim("ogtt", G.INTERVENTIONS["insulin_secretion"].mods(float(u)), ov, dose=DOSE[dk])
        do = G.direct_outcomes(t, Yo); L.append(G.loss_row(t, Yo)["composite_loss"])
        nad.append(do["nadir_mgdl"]); pk.append(do["peak_mgdl"]); b70.append(do["min_below70"])
    lab, uo, _ = G.classify_response(G.U_GRID, np.array(L))
    return dict(tau_mult=tau, basal_plasma=bk, dose=dk, kpp_mult=kp, response_class=lab, u_opt=uo,
                u70=u_cross(G.U_GRID, nad), nadir_u0=nad[0], nadir_u1=nad[-1], peak_u0=pk[0], peak_u1=pk[-1],
                min_below70_u1=b70[-1], nadir_monotone=bool(np.all(np.diff(nad) <= 1e-6)),
                peak_monotone=bool(np.all(np.diff(pk) <= 1e-6)))


if __name__ == "__main__":
    jobs = [(t, b, d, 1.0) for t, b, d in itertools.product(TAU, BASAL, DOSE)] + \
           [(t, "82.4", "100g", k) for t in TAU for k in KPP if k != 1.0]
    Bd = G.Budget("gate_c3_stage1", 6000); n = len(jobs) * len(G.U_GRID); Bd.check(n)
    with Pool(2) as p:
        df = pd.DataFrame(p.map(job, jobs, chunksize=1))
    df.to_csv(G.OUT / "C3_STAGED_ROBUSTNESS.csv", index=False)
    Bd.close(n)
    pd.set_option("display.width", 200)
    print(df.round(3).to_string(index=False))
