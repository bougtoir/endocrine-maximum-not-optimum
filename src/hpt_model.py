"""Exploratory secondary axis: hypothalamic–pituitary–thyroid (HPT) model.

A deliberately minimal published-form feedback model (3 ODEs) used ONLY to
test whether the 'interior optimum' phenomenon generalises beyond glucose
homeostasis. Parameters are order-of-magnitude values set so the basal
point matches typical serum values (TSH ~1.5 mU/L, T4 ~100 nmol/L,
T3 ~2 nmol/L); documented as exploratory, NOT a fitted clinical model.

Equations:
  dTSH = k_sTSH / (1 + (T3/k_i)^n_i)  - k_dTSH * TSH
  dT4  = k_sT4 * TSH^e4              - k_dT4 * T4 + Input_T4(t)
  dT3  = k_cT3 * T4                  - k_dT3 * T3

Interventions (same u convention as the glucose axis):
  'hpt_feedback'    : scales deviation of feedback inhibition from neutral
  'hpt_thyroid'     : scales T4 secretory responsiveness to TSH
Challenge: step T4 infusion 0 -> +20 nmol/L/min for 60 min, horizon 360.
"""

import numpy as np

P = dict(
    k_sTSH=0.06,  # mU/L/min max TSH secretion (basal TSH ~1.5 mU/L)
    k_i=2.0,      # nmol/L T3 at half inhibition
    n_i=4.0,      # Hill coefficient of feedback
    k_dTSH=0.02,  # /min
    k_sT4=0.3266, # nmol/L/min T4 secretion gain (basal T4 ~100 nmol/L)
    e4=0.5,       # TSH potency exponent
    k_dT4=0.004,  # /min
    k_cT3=0.0006, # nmol T3 per nmol T4 (basal T3 ~2 nmol/L)
    k_dT3=0.03,   # /min
)

T3_SP = 2.0  # target T3 nmol/L


def feedback_mult(T3, s):
    raw = 1.0 / (1.0 + (T3 / P["k_i"]) ** P["n_i"])
    return max(0.05, 1.0 + s * (raw - 1.0))


def rhs(t, y, s_fb=1.0, s_th=1.0, input_t4=0.0):
    TSH, T4, T3 = y
    s_tsh = P["k_sTSH"] * feedback_mult(T3, s_fb)
    s_t4 = P["k_sT4"] * max(TSH, 0) ** P["e4"] * s_th
    return np.array([
        s_tsh - P["k_dTSH"] * TSH,
        s_t4 - P["k_dT4"] * T4 + input_t4,
        P["k_cT3"] * T4 - P["k_dT3"] * T3,
    ])


def steady_state(s_fb=1.0, s_th=1.0):
    """Find basal steady state by Newton iteration on T3 = f(T3)."""
    from scipy.optimize import brentq
    def f(T3):
        TSH = P["k_sTSH"] * feedback_mult(T3, s_fb) / P["k_dTSH"]
        T4 = P["k_sT4"] * max(TSH, 1e-9) ** P["e4"] * s_th / P["k_dT4"]
        return P["k_cT3"] * T4 / P["k_dT3"] - T3
    try:
        T3 = brentq(f, 1e-6, 50)
    except ValueError:
        T3 = 0.0 if f(1e-6) <= 0 else brentq(f, 1e-6, 500)
    TSH = P["k_sTSH"] * feedback_mult(T3, s_fb) / P["k_dTSH"]
    T4 = P["k_sT4"] * TSH ** P["e4"] * s_th / P["k_dT4"]
    return np.array([TSH, T4, T3])


def simulate(s_fb=1.0, s_th=1.0, load_rate=0.0, load_t=(0.0, 60.0),
             t_span=(-60.0, 360.0), rtol=1e-7):
    from scipy.integrate import solve_ivp
    y0 = steady_state(s_fb, s_th)
    def f(t, y):
        inp = load_rate if load_t[0] <= t < load_t[1] else 0.0
        return rhs(t, y, s_fb, s_th, inp)
    sol = solve_ivp(f, t_span, y0, method="LSODA", rtol=rtol, atol=1e-10,
                    max_step=1.0)   # pulsed load requires bounded steps
    return sol.t, sol.y
