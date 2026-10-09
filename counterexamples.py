# Part 3: automatically find inputs where a greedy algorithm is not optimal.  Owner: P1
#
#   python counterexamples.py                     default run
#   python counterexamples.py --seed 7            a different (but still reproducible) search
#   python counterexamples.py --stats-trials 50000   bigger failure-rate experiment
#
# Needs at least one counterexample each for earliest_start and shortest_duration,
# plus group_heuristic if the search finds one. For each one, the report needs:
# the input intervals, the greedy picks, an optimal solution, and both sizes.
#
# Outputs: results/counterexamples.json            everything below, machine-readable
#          results/counterexample_<algorithm>.png  timeline picture (heuristic vs optimal)
#          results/counterexample_timelines.txt    the same timelines as plain text
#
# What the script does:
#   1. Sanity tests: the two failures the assignment requires (Earliest Start and
#      Shortest Duration) must be detected before anything else runs.
#   2. Counterexample search: for n = 2, 3, ..., max_n it draws tries_per_n instances
#      from generate(), cycling through every kind so no single distribution dominates,
#      and returns the first instance where |Greedy(I)| < OPT(I) (OPT from brute force).
#      Searching small n first keeps the counterexample short. Every instance seed is
#      derived from SEED, so the same counterexample is found every run.
#   3. Minimizing: the instance that was found is shrunk (jobs removed, times compacted,
#      jobs relabeled A, B, C... in time order) while it still fails, so it is easy to read.
#      Both the discovered and the minimized versions are saved.
#   4. Failure rates: every algorithm (Earliest Finish too) is run on a fixed batch of
#      random instances and the failures are counted, overall and per generator kind.
#
# Logical caveat (also needed in the report): a counterexample PROVES an algorithm is
# not always optimal. Finding none only means this search missed one; it proves nothing.
# Earliest Finish having 0 failures below is evidence that the code works, not a proof.

import argparse
import json
import platform
import sys

import matplotlib

matplotlib.use("Agg")  # write PNG files without needing a display
import matplotlib.pyplot as plt

from algorithms import GREEDY, brute_force
from generate import KINDS, generate
from jobs import Job, ids, is_valid_schedule
from run import RESULTS_DIR, SEED

REQUIRED = ["earliest_start", "shortest_duration"]  # the assignment demands these two
EXCLUDED = {"earliest_finish"}  # the correct algorithm, so there is nothing to find
JSON_PATH = RESULTS_DIR / "counterexamples.json"
TIMELINE_PATH = RESULTS_DIR / "counterexample_timelines.txt"
MAX_N = 12  # brute force is instant here (2^12 subsets)
TRIES_PER_N = 2000  # 500 was enough for the two required ones, but not for group_heuristic
STATS_TRIALS = 10000  # instances for the failure-rate table
STATS_N_MIN, STATS_N_MAX = 4, 10

# The two sanity tests from the assignment: (name, algorithm, intervals, greedy size, OPT size).
SANITY_TESTS = [
    ("Sanity Test 1: Earliest Start fails", "earliest_start",
     [(0, 10), (1, 2), (2, 3), (3, 4), (4, 5)], 1, 4),
    ("Sanity Test 2: Shortest Duration fails", "shortest_duration",
     [(2, 4), (0, 3), (3, 6)], 1, 2),
]


# --------------------------------------------------------------------------- helpers

def label(i):
    # Job id -> letter used in the assignment: 0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA.
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def check_results(name, jobs, greedy, opt):
    # Never report a bogus counterexample: both answers must be valid, and the
    # greedy answer can never beat the exact solver.
    if not is_valid_schedule(greedy) or not is_valid_schedule(opt):
        raise AssertionError(f"{name} or brute_force returned overlapping jobs for {jobs}")
    if len(greedy) > len(opt):
        raise AssertionError(f"{name} beat brute force on {jobs}: the exact solver is wrong")


def describe(name, jobs, greedy=None, opt=None):
    # The facts the assignment asks for, for one instance.
    greedy = GREEDY[name](jobs) if greedy is None else greedy
    opt = brute_force(jobs) if opt is None else opt
    check_results(name, jobs, greedy, opt)
    return {
        "jobs": [list(j) for j in jobs],  # [id, start, finish]
        "greedy_ids": ids(greedy),
        "greedy_labels": [label(i) for i in ids(greedy)],
        "opt_ids": ids(opt),
        "opt_labels": [label(i) for i in ids(opt)],
        "greedy_size": len(greedy),
        "opt_size": len(opt),
    }


# --------------------------------------------------------------------------- sanity tests

def run_sanity_tests():
    # Stop immediately if the framework does not detect the two known failures.
    results = []
    for test, name, intervals, want_greedy, want_opt in SANITY_TESTS:
        jobs = [Job(i, s, f) for i, (s, f) in enumerate(intervals)]
        got_greedy = len(GREEDY[name](jobs))
        got_opt = len(brute_force(jobs))
        passed = (got_greedy, got_opt) == (want_greedy, want_opt)
        results.append({"test": test, "algorithm": name, "intervals": intervals,
                        "expected_greedy": want_greedy, "expected_opt": want_opt,
                        "got_greedy": got_greedy, "got_opt": got_opt, "passed": passed})
        if not passed:
            raise AssertionError(f"{test} FAILED: greedy={got_greedy} (want {want_greedy}), "
                                 f"OPT={got_opt} (want {want_opt}). Fix the framework first.")
    return results


# --------------------------------------------------------------------------- the search

def find_counterexample(name, max_n=MAX_N, tries_per_n=TRIES_PER_N, seed=SEED):
    # Try small sizes first (n = 2, 3, ...) so the counterexample is easy to read.
    # Return a dict with: algorithm, kind, n, seed, jobs, greedy_ids, opt_ids,
    # greedy_size, opt_size (plus the letter labels). Return None if nothing was found.
    algorithm = GREEDY[name]
    for n in range(2, max_n + 1):
        for t in range(tries_per_n):
            kind = KINDS[t % len(KINDS)]  # round-robin over the generator kinds
            instance_seed = seed + n * tries_per_n + t  # unique per (n, t), fixed by SEED
            jobs = generate(kind, n, instance_seed)
            greedy = algorithm(jobs)
            opt = brute_force(jobs)
            check_results(name, jobs, greedy, opt)
            if len(greedy) < len(opt):
                return {"algorithm": name, "kind": kind, "n": n, "seed": instance_seed,
                        **describe(name, jobs, greedy, opt)}
    return None


# --------------------------------------------------------------------------- minimizing

def fails(name, jobs):
    return len(jobs) > 0 and len(GREEDY[name](jobs)) < len(brute_force(jobs))


def minimize(name, jobs):
    # Make a failing instance as small and readable as possible. Every change is kept
    # only if the instance STILL fails, so the result is always a real counterexample.

    # 1) Delete jobs one at a time while the instance still fails.
    current = list(jobs)
    changed = True
    while changed:
        changed = False
        for job in list(current):
            candidate = [j for j in current if j != job]
            if fails(name, candidate):
                current = candidate
                changed = True

    def keep_if_fails(candidate):
        return candidate if fails(name, candidate) else current

    # 2) Ids 0..m-1 in the existing id order (every algorithm breaks ties by id, so
    #    the relative order of ids keeps the behavior the same).
    current = keep_if_fails([Job(new, j.start, j.finish)
                             for new, j in enumerate(sorted(current, key=lambda j: j.id))])

    # 3) Shift to start at time 0, then squeeze out empty time between the endpoints.
    shift = min(j.start for j in current)
    current = keep_if_fails([Job(j.id, j.start - shift, j.finish - shift) for j in current])
    rank = {p: r for r, p in enumerate(sorted({p for j in current for p in (j.start, j.finish)}))}
    current = keep_if_fails([Job(j.id, rank[j.start], rank[j.finish]) for j in current])

    # 4) Relabel A, B, C... in time order so the report reads left to right.
    by_time = sorted(current, key=lambda j: (j.start, j.finish, j.id))
    current = keep_if_fails([Job(new, j.start, j.finish) for new, j in enumerate(by_time)])
    return current


# --------------------------------------------------------------------------- failure rates

def failure_rates(trials=STATS_TRIALS, n_min=STATS_N_MIN, n_max=STATS_N_MAX, seed=SEED):
    # Run EVERY algorithm (Earliest Finish too) on the same batch of random instances
    # and count how often each is suboptimal. Seeds start at seed + 1,000,000 so they
    # never reuse the instances from the counterexample search.
    stats = {name: {"instances_tested": 0, "counterexamples_found": 0,
                    "by_kind": {k: {"tested": 0, "failed": 0} for k in KINDS}}
             for name in GREEDY}
    sizes = n_max - n_min + 1
    for t in range(trials):
        kind = KINDS[t % len(KINDS)]
        n = n_min + (t // len(KINDS)) % sizes  # n cycles through n_min..n_max evenly
        jobs = generate(kind, n, seed + 1_000_000 + t)
        opt = brute_force(jobs)
        for name, algorithm in GREEDY.items():
            greedy = algorithm(jobs)
            check_results(name, jobs, greedy, opt)
            s = stats[name]
            s["instances_tested"] += 1
            s["by_kind"][kind]["tested"] += 1
            if len(greedy) < len(opt):
                s["counterexamples_found"] += 1
                s["by_kind"][kind]["failed"] += 1
    for s in stats.values():
        s["failure_rate"] = s["counterexamples_found"] / s["instances_tested"]
    return stats


# --------------------------------------------------------------------------- visualization

def plot_timeline(example, path):
    # Draw each job as a horizontal bar. Top panel: the heuristic's picks (red).
    # Bottom panel: an optimal solution (green). Jobs that were not picked are gray.
    jobs = sorted(example["jobs"], key=lambda j: (j[1], j[0]))  # rows ordered by (start, id)
    t_min = min(j[1] for j in jobs)
    t_max = max(j[2] for j in jobs)
    panels = [
        (f"{example['algorithm']} picks: {example['greedy_size']} jobs", example["greedy_ids"], "tab:red"),
        (f"Optimal solution: {example['opt_size']} jobs", example["opt_ids"], "tab:green"),
    ]

    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(8, 1.0 + 0.45 * len(jobs) * 2))
    for ax, (title, chosen, color) in zip(axes, panels):
        for row, (job_id, start, finish) in enumerate(jobs):
            picked = job_id in chosen
            ax.barh(row, finish - start, left=start, height=0.6,
                    color=color if picked else "lightgray",
                    edgecolor="black" if picked else "gray", linewidth=0.8)
            ax.text(start + (finish - start) / 2, row, label(job_id),
                    ha="center", va="center", fontsize=8)
        ax.set_yticks(range(len(jobs)))
        ax.set_yticklabels([f"job {label(j[0])}" for j in jobs], fontsize=8)
        ax.invert_yaxis()  # first job at the top
        ax.set_title(title, fontsize=10)
        ax.grid(axis="x", linestyle=":", alpha=0.6)
    axes[-1].set_xlim(t_min - 0.5, t_max + 0.5)
    axes[-1].set_xticks(range(t_min, t_max + 1, max(1, (t_max - t_min) // 25)))
    axes[-1].set_xlabel("time (intervals are half-open [start, finish))")
    fig.suptitle(
        f"Counterexample for {example['algorithm']}: "
        f"|Greedy| = {example['greedy_size']}, OPT = {example['opt_size']}",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def text_timeline(example, width=60):
    # The same picture as plain text. Columns H / O mark the jobs chosen by the
    # heuristic / by the optimal solution.
    jobs = [Job(*j) for j in example["jobs"]]
    lo = min(j.start for j in jobs)
    hi = max(j.finish for j in jobs)
    scale = min(1.0, width / (hi - lo))
    col = lambda t: round((t - lo) * scale)
    greedy, best = set(example["greedy_ids"]), set(example["opt_ids"])
    lines = [f"{example['algorithm']}: |Greedy| = {example['greedy_size']}, OPT = {example['opt_size']}",
             f"  heuristic picks: {', '.join(example['greedy_labels'])}",
             f"  an optimal set:  {', '.join(example['opt_labels'])}",
             "",
             "  job   [start,finish)   H O  time -->"]
    prefix = 0
    for j in sorted(jobs, key=lambda j: (j.start, j.finish, j.id)):
        a, b = col(j.start), max(col(j.finish), col(j.start) + 1)
        bar = " " * a + "[" + "=" * (b - a - 1) + ")" if b - a > 1 else " " * a + "|"
        head = (f"  {label(j.id):<4}  [{j.start:>3},{j.finish:>3})    "
                f"{'x' if j.id in greedy else '.'} {'x' if j.id in best else '.'}  ")
        prefix = len(head)
        lines.append(head + bar)
    # Axis: a tick every 5 time units, plus the last time point if it does not collide.
    ticks = list(range(lo, hi + 1, 5))
    if hi - ticks[-1] >= 3:
        ticks.append(hi)
    axis = [" "] * (col(hi) + len(str(hi)) + 1)
    for t in ticks:
        for k, ch in enumerate(str(t)):
            axis[col(t) + k] = ch
    lines.append(" " * prefix + "".join(axis).rstrip())
    return "\n".join(lines)


# --------------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description="Search for greedy counterexamples (Part 3).")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--max-n", type=int, default=MAX_N, help="largest instance size (brute force limits this)")
    parser.add_argument("--tries-per-n", type=int, default=TRIES_PER_N)
    parser.add_argument("--stats-trials", type=int, default=STATS_TRIALS,
                        help="instances for the failure-rate table (0 to skip)")
    args = parser.parse_args()
    RESULTS_DIR.mkdir(exist_ok=True)

    print("Running sanity tests...")
    sanity = run_sanity_tests()
    for r in sanity:
        print(f"  PASS  {r['test']}  (greedy = {r['got_greedy']}, OPT = {r['got_opt']})")

    print(f"\nSearching for counterexamples (n = 2..{args.max_n}, {args.tries_per_n} tries per n, "
          f"seed = {args.seed})...")
    found, not_found, texts = [], [], []
    for name in GREEDY:
        if name in EXCLUDED:
            continue
        example = find_counterexample(name, max_n=args.max_n, tries_per_n=args.tries_per_n, seed=args.seed)
        if example is None:
            not_found.append(name)
            print(f"{name}: no counterexample found (n <= {args.max_n}, {args.tries_per_n} tries per n). "
                  "This does NOT prove it is optimal.")
            continue
        small = minimize(name, [Job(*j) for j in example["jobs"]])
        minimized = {"algorithm": name, "n": len(small), **describe(name, small)}
        assert minimized["greedy_size"] < minimized["opt_size"], "minimized instance must still fail"
        example["minimized"] = minimized
        found.append(example)

        png = RESULTS_DIR / f"counterexample_{name}.png"
        plot_timeline(minimized, png)  # the minimized one is the easiest to read
        texts.append(text_timeline(minimized))
        print(f"{name}: |Greedy| = {minimized['greedy_size']}, OPT = {minimized['opt_size']} "
              f"(minimized to n = {minimized['n']}; found with kind={example['kind']}, "
              f"n={example['n']}, seed={example['seed']}) -> {png.name}")
        print(f"    heuristic picks {minimized['greedy_labels']}, an optimal set is {minimized['opt_labels']}")

    stats = {}
    if args.stats_trials > 0:
        print(f"\nFailure rates on {args.stats_trials} random instances "
              f"(n = {STATS_N_MIN}..{STATS_N_MAX}, all {len(KINDS)} kinds)...")
        stats = failure_rates(args.stats_trials, seed=args.seed)
        for name, s in stats.items():
            print(f"  {name:<18} {s['counterexamples_found']:>5} / {s['instances_tested']} suboptimal")

    output = {
        "search": {"seed": args.seed, "max_n": args.max_n, "tries_per_n": args.tries_per_n,
                   "kinds": KINDS, "stats_trials": args.stats_trials, "python": platform.python_version()},
        "sanity_tests": sanity,
        "failure_rates": stats,
        "counterexamples": found,
        "no_counterexample_found": not_found,
        "note": ("A counterexample proves an algorithm is not always optimal. Finding none "
                 "(or 0 failures in the table) is evidence only, not a proof of optimality."),
    }
    JSON_PATH.write_text(json.dumps(output, indent=2) + "\n")
    TIMELINE_PATH.write_text("\n\n".join(texts) + "\n")

    print("\n" + "\n\n".join(texts))
    print(f"\nSaved {len(found)} counterexample(s) to {JSON_PATH}")

    missing = [name for name in REQUIRED if name in not_found]
    if missing:
        print(f"ERROR: the assignment requires counterexamples for {missing}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
