"""Gate A1: compare upstream MATLAB default parameter sets (Sorensen IV
variant, BioSorSimo oral variant) with the manuscript implementation
(src/sorensen_model.BASE_PARAMS). Reads the frozen upstream zips directly."""
import re, sys, zipfile, pathlib
import pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
import sorensen_model as sm

UP = ROOT / "models/primary/upstream"
SRC = {
    "sorensen_iv": (UP / "Sorensen/ModelMatlab/Sorensen.zip", "SorensenInitializeParvals.m"),
    "biosorsimo_oral": (UP / "BioSorSimo/ModelMatlab/BioSorSimo.zip", "BioSorSimoInitializeParvals.m"),
}
PAT = re.compile(r"^\s*([A-Za-z]\w*)\s*=\s*([-+0-9.eE]+)\s*;\s*%\s*\(bigtheta\s*(\d+)\)")


def parse(zpath, member):
    with zipfile.ZipFile(zpath) as z:
        name = next(n for n in z.namelist() if n.endswith(member))
        txt = z.read(name).decode("latin-1")
    return {m.group(1): float(m.group(2)) for m in map(PAT.match, txt.splitlines()) if m}


def main():
    sets = {k: parse(*v) for k, v in SRC.items()}
    names = sorted(set(sets["sorensen_iv"]) | set(sets["biosorsimo_oral"]) | set(sm.BASE_PARAMS))
    rows = []
    for n in names:
        a = sets["sorensen_iv"].get(n); b = sets["biosorsimo_oral"].get(n); c = sm.BASE_PARAMS.get(n)
        rows.append(dict(parameter=n, upstream_sorensen_iv=a, upstream_biosorsimo_oral=b,
                         manuscript_impl=c,
                         iv_vs_oral_differ=(a is not None and b is not None and abs(a - b) > 1e-12 * max(1, abs(a))),
                         manuscript_matches_iv=(a is not None and c is not None and abs(a - c) <= 1e-9 * max(1, abs(a))),
                         manuscript_matches_oral=(b is not None and c is not None and abs(b - c) <= 1e-9 * max(1, abs(b)))))
    df = pd.DataFrame(rows)
    out = ROOT / "results/rebuild/gate_a/GATE_A_PARAMETER_PROVENANCE.csv"
    df.to_csv(out, index=False)
    d = df[df.iv_vs_oral_differ | (~df.manuscript_matches_iv & df.upstream_sorensen_iv.notna() & df.manuscript_impl.notna())]
    print(d.to_string(index=False))
    print("n upstream IV:", len(sets["sorensen_iv"]), "n oral:", len(sets["biosorsimo_oral"]), "n impl:", len(sm.BASE_PARAMS))


if __name__ == "__main__":
    main()
