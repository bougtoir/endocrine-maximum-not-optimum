"""Gate A5: wide comparison of the 50 cases across historical (published file), H, S, O, C."""
import pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
G = ROOT / "results/rebuild/gate_a"
cl = pd.read_csv(G / "GATE_A_CORRECTED_50_CASES.csv")
orig = pd.read_csv(ROOT / "results/scans/full_classification.csv")
w = cl.pivot_table(index=["intervention", "challenge"], columns="config",
                   values=["response_class", "u_opt"], aggfunc="first")
w.columns = [f"{b}_{a}" for a, b in w.columns]
o = orig.set_index(["intervention", "challenge"])[["response_class", "u_opt"]].add_prefix("published_")
w = o.join(w).reset_index()
w["H_reproduces_published"] = (w.published_response_class == w.H_response_class) & ((w.published_u_opt - w.H_u_opt).abs() < 1e-9)
w.to_csv(G / "GATE_A_CASE_COMPARISON_WIDE.csv", index=False)
keep = w[(w[[c for c in w if c.endswith("response_class")]] == "TypeII").any(axis=1) | ~w.H_reproduces_published]
print(keep[["intervention", "challenge", "published_response_class", "published_u_opt", "H_response_class", "S_response_class",
            "S_u_opt", "O_response_class", "C_response_class", "C_u_opt"]].to_string(index=False))
print("H reproduces published:", int(w.H_reproduces_published.sum()), "/", len(w))
