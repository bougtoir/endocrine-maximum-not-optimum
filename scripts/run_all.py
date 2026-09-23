#!/usr/bin/env python3
"""Reproducible end-to-end pipeline for 'maximum is not optimum'.

Usage: python scripts/run_all.py
Runs: unit tests -> scans -> controls -> robustness -> pareto -> feedback
      -> disease -> figures -> tables/values.
"""

import subprocess, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "analysis")

STEPS = [
    ("unit tests", [sys.executable, os.path.join(ROOT, "tests", "test_pipeline.py")]),
    ("grid scans + refinement", [sys.executable, os.path.join(A, "run_scans.py")]),
    ("synthetic controls", [sys.executable, os.path.join(A, "run_controls.py")]),
    ("robustness & sensitivity", [sys.executable, os.path.join(A, "run_robustness.py")]),
    ("pareto fronts", [sys.executable, os.path.join(A, "run_pareto.py")]),
    ("feedback mechanism", [sys.executable, os.path.join(A, "run_feedback.py")]),
    ("disease states", [sys.executable, os.path.join(A, "run_disease.py")]),
    ("HPT exploratory axis", [sys.executable, os.path.join(A, "run_hpt.py")]),
    ("figures", [sys.executable, os.path.join(A, "make_figures.py")]),
    ("tables + manuscript values", [sys.executable, os.path.join(A, "make_tables_values.py")]),
    ("manuscript package", [sys.executable, os.path.join(A, "make_manuscript.py")]),
]


def main():
    for name, cmd in STEPS:
        print(f"\n{'='*70}\n### {name}\n{'='*70}")
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            print(f"FAILED: {name} (exit {r.returncode})")
            sys.exit(r.returncode)
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
