"""Gate B: endpoint overlap / double counting among objective-entering endpoints (Spearman rho over all
config-C case x u points, pooled and per challenge)."""
import sys, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from homeostatic_loss import DEFAULT_WEIGHTS

K = [k for k, w in DEFAULT_WEIGHTS.items() if w > 0]
ep = pd.read_csv(ROOT / "results/rebuild/gate_a/corrected_scan_endpoints.csv")
ep = ep[ep.config == "C"]
rows = []
for ch, d in [("pooled", ep)] + list(ep.groupby("challenge")):
    r = d[K].corr(method="spearman")
    for i, a in enumerate(K):
        for b in K[i + 1:]:
            rows.append(dict(scope=ch, endpoint_a=a, endpoint_b=b, spearman_rho=r.loc[a, b]))
df = pd.DataFrame(rows)
df.to_csv(ROOT / "results/rebuild/gate_b/GATE_B_ENDPOINT_OVERLAP.csv", index=False)
print(df[(df.spearman_rho.abs() >= 0.8)].round(2).to_string(index=False))
