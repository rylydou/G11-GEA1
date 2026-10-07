# Shared plumbing: run every algorithm on generated test data and summarize the results.
#
#   python run.py                  generate instances, compare every algorithm to brute force,
#                                  save results/results.csv and print the summary
#   python run.py --per-kind 100   more instances per kind (default 50, so 200 total)
#   python run.py --file jobs.csv  run every algorithm on one input file (id,start,finish)
#
# The other scripts reuse these functions:
#   counterexamples.py (P1)  analysis.py (P2)  runtime.py (P3)

import argparse
import json
import statistics
import time
from pathlib import Path

import pandas as pd

from algorithms import GREEDY, brute_force
from generate import KINDS, generate
from jobs import ids, is_valid_schedule, read_jobs

SEED = 4050  # base seed for every experiment
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_CSV = RESULTS_DIR / "results.csv"


def solve(jobs):
    # Run brute force and every greedy algorithm on one instance.
    # Returns (optimal selection, {algorithm name: its selection}).
    opt = brute_force(jobs)
    picks = {}
    for name, algorithm in GREEDY.items():
        selected = algorithm(jobs)
        if not is_valid_schedule(selected):
            raise AssertionError(f"{name} selected overlapping jobs: {selected}")
        picks[name] = selected
    return opt, picks


def run_experiments(per_kind=50, n_min=4, n_max=12, seed=SEED):
    # One row per (instance, algorithm). n cycles through n_min..n_max so every
    # size is covered evenly. Each instance is rebuilt by generate(kind, n, seed).
    rows = []
    instance = 0
    for kind in KINDS:
        for i in range(per_kind):
            n = n_min + i % (n_max - n_min + 1)
            instance_seed = seed + instance
            jobs = generate(kind, n, instance_seed)
            opt, picks = solve(jobs)
            for name, selected in picks.items():
                rows.append({
                    "instance": instance,
                    "kind": kind,
                    "n": n,
                    "seed": instance_seed,
                    "algorithm": name,
                    "size": len(selected),
                    "opt": len(opt),
                    "ratio": len(selected) / len(opt),
                    "optimal": len(selected) == len(opt),
                    "selected_ids": json.dumps(ids(selected)),
                    "opt_ids": json.dumps(ids(opt)),
                    "jobs": json.dumps([list(j) for j in jobs]),
                })
            instance += 1
    return pd.DataFrame(rows)


def summarize(results):
    # Per algorithm: % of instances solved optimally, average |H(I)| / OPT(I),
    # and the worst instance seen.
    summary = results.groupby("algorithm").agg(
        instances=("instance", "count"),
        pct_optimal=("optimal", lambda s: 100 * s.mean()),
        mean_ratio=("ratio", "mean"),
        worst_ratio=("ratio", "min"),
    )
    worst_rows = results.loc[results.groupby("algorithm")["ratio"].idxmin()]
    summary["worst_instance"] = worst_rows.set_index("algorithm")["instance"]
    return summary.round(3)


def time_algorithms(sizes, repeats, kind="varied", seed=SEED):
    # Median wall-clock time of each greedy algorithm at each n. No brute force here.
    rows = []
    for n in sizes:
        jobs = generate(kind, n, seed)
        for name, algorithm in GREEDY.items():
            times = []
            for _ in range(repeats):
                start = time.perf_counter()
                algorithm(jobs)
                times.append(time.perf_counter() - start)
            median = statistics.median(times)
            print(f"  {name:<18} n={n:<8} median {median:.5f}s")  # shows progress if one is slow
            rows.append({
                "algorithm": name,
                "n": n,
                "repeats": repeats,
                "median_seconds": median,
                "min_seconds": min(times),
                "max_seconds": max(times),
            })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description="Run every algorithm on generated test data.")
    parser.add_argument("--file", help="run on one CSV file (id,start,finish) instead")
    parser.add_argument("--per-kind", type=int, default=50, help="instances per generator kind")
    parser.add_argument("--n-min", type=int, default=4, help="smallest instance size")
    parser.add_argument("--n-max", type=int, default=12, help="largest instance size (brute force limits this)")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    if args.file:
        jobs = read_jobs(args.file)
        opt, picks = solve(jobs)
        print(f"{'brute_force':<18} size={len(opt):<3} ids={ids(opt)}")
        for name, selected in picks.items():
            print(f"{name:<18} size={len(selected):<3} ids={ids(selected)}")
        return

    results = run_experiments(args.per_kind, args.n_min, args.n_max, args.seed)
    RESULTS_DIR.mkdir(exist_ok=True)
    results.to_csv(RESULTS_CSV, index=False)

    eft = results[results["algorithm"] == "earliest_finish"]
    print(f"Saved {results['instance'].nunique()} instances to {RESULTS_CSV}\n")
    print(f"Earliest Finish matched brute force on {eft['optimal'].sum()} / {len(eft)} instances\n")
    print(summarize(results).to_string())


if __name__ == "__main__":
    main()
