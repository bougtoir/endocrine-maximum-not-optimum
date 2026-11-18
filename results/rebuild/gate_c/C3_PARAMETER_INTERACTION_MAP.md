# C3 — Parameter interaction map (Stage 1, case (a) only)

**Source.** `C3_STAGED_ROBUSTNESS.csv`, 40 conditions × 21 u, 840 evaluations.

**Prediction tested.** Specified from C2 and composite-free: u70, the secretory gain at which the OGTT nadir first reaches 70 mg/dL, decreases as insulin-action delay lengthens. The secondary quantity is the composite u*.

**Results.**
- **Basal × delay.** At basal 90 mg/dL the nadir never falls below 70 mg/dL at any u, dose or delay, so u70 is undefined. The composite class is Type I (u* = 1) in all 15 conditions. The prediction has no content off the reference basal state.
- **Dose × delay at basal 82.4.**
  - At 100 g, u70 falls monotonically with delay: 0.686 → 0.595 → 0.519 → 0.395 → 0.303, and u* tracks it.
  - At 75 g the ordering is not monotone (0.721, 0.781, 0.699, 0.546, 0.436).
  - At 50 g it is not monotone either (0.719, 0.774, 0.907, 0.837, 0.683).
- **Potentiator × delay (100 g).** At each potentiator rate, u70 still decreases with delay. A faster potentiator shifts u70 upward.
- **Direct outcomes.** Nadir and peak are monotone in u in all 40 conditions.

**Interpretation.** The delay → lower critical gain relation is the qualitative signature of delayed negative feedback. It appears only with a large glucose load and a low starting glucose. It is not robust across model-credible starting states. It is also not specific to this model, so it cannot be presented as a new endocrine prediction.

**Stage 2 not triggered.** Stage 2 (correlated ensemble) and Stage 3 (GSA/surrogate) were not run. No mechanism survived as a robust, model-specific prediction, so the expected information gain is low (see `C3_COMPUTE_BUDGET.md`).
