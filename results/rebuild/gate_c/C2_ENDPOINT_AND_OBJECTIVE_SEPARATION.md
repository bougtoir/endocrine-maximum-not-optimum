# C2 — Separating the weighted-loss optimum from direct glycaemic outcomes

1. **Historical objective.** It is unchanged (Gate B specification) and is reported in every row of `C2_TARGETED_ABLATIONS.csv`, together with all 15 endpoints (`ep_*`).
2. **Direct outcomes.** They are pre-declared in `C2_PRESPEC.md` and reported as separate columns: nadir, peak, minutes and area below 70, minutes and area above 140, end glucose, pre-challenge drift, and return time. They are not combined into a new score, and no re-weighting was done.
3. **Result.** Every interior composite optimum lies between two monotone direct outcomes moving in opposite directions:
   - (a) peak against nadir and time below 70
   - (b) time below 70 against peak and area above 140

   For (c), no direct outcome improves at all.

   The only quantities that are non-monotone in u are threshold-time metrics, and those enter the historical objective as `recovery_time` and `undershoot` relative to the drifted G(0).
4. **Consequence.** Any statement of the form "an intermediate dose is optimal" is a statement about the 70/140 thresholds and the historical weights. It is not a property of the endocrine response curve. A defensible statement in direct units has the form "u above X produces nadir < 70 mg/dL while peak falls by Y". Such statements are dose–response facts of the model, not optima.
