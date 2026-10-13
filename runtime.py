# Part 6: runtime of the greedy algorithms on large inputs.  Owner: P3
#
#   python runtime.py                     the four assignment sizes, 5 repeats
#   python runtime.py --repeats 9         more repeats, same sizes
#   python runtime.py --sizes 100 1000 10000 100000 300000
#   python runtime.py --kind sparse       benchmark on a different generator kind
#
# Greedy algorithms only; brute force can't handle these sizes.
#
# Three experiments:
#   1. Main sweep. Each greedy algorithm on one instance per n, `repeats` times,
#      reported as the median. This is the table in report section 7.
#   2. Sort step. The same measurement for each algorithm's sort ALONE, so the
#      report can say how much of each running time is the sort (the assignment
#      asks specifically where sorting appears).
#   3. Kind breakdown at the largest n. shortest_duration and group_heuristic
#      insert into a list, which is O(n) per insert, so their cost depends on how
#      many jobs get selected -- not just on n. Timing every generator kind at one
#      n shows that. For the two algorithms that insert, these rows also count how
#      many list elements the inserts actually move, which is the quantity the
#      O(n^2) worst case is about, so the report can compare the two directly.
#
# Outputs: results/runtime.csv           long form: one row per measurement
#          results/runtime_summary.csv   report table: medians, sort share, growth
#          results/runtime.png           log-log time vs n, and sort share per n
#
# Reading the growth columns: over a step from n1 to n2, a Theta(n log n)
# algorithm should cost about (n2 log n2) / (n1 log n1) times as much, and a
# Theta(n^2) one about (n2/n1)^2 times as much. For a 10x step those are ~13x and
# 100x, which are far enough apart to tell apart with a handful of measurements.
#
# Do not overclaim (also needed in the report): a few timings cannot prove an
# asymptotic bound. They can only be consistent or inconsistent with one.

import argparse
import platform
import statistics
import time
from bisect import bisect_right
from math import log

import matplotlib

matplotlib.use("Agg")  # write PNG files without needing a display
import matplotlib.pyplot as plt
import pandas as pd

from algorithms import GREEDY
from algorithms.group_heuristic import count_conflicts
from generate import KINDS, generate
from jobs import Job
from run import RESULTS_DIR, SEED, time_algorithms

SIZES = [100, 1_000, 10_000, 100_000]  # the sizes the assignment suggests
REPEATS = 5
KIND = "varied"  # mixed short and long jobs, so nothing is a special case
CSV_PATH = RESULTS_DIR / "runtime.csv"
SUMMARY_PATH = RESULTS_DIR / "runtime_summary.csv"
PNG_PATH = RESULTS_DIR / "runtime.png"

# One fixed color per algorithm, in GREEDY order (categorical slots 1-4, the same
# palette analysis.py uses). Markers double as a second cue, so the lines can
# still be told apart in grayscale or with color-vision deficiency.
COLORS = {"earliest_finish": "#2a78d6", "earliest_start": "#eb6834",
          "shortest_duration": "#1baf7a", "group_heuristic": "#eda100"}
MARKERS = {"earliest_finish": "o", "earliest_start": "s",
           "shortest_duration": "^", "group_heuristic": "D"}
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


# --------------------------------------------------------------------------- the sort step

# Each algorithm's sort, on its own. These keys MUST match the ones in
# algorithms/*.py -- test_runtime.py checks that they still agree.
#
# group_heuristic is the one that is not a bare sort: it cannot order jobs until it
# knows each job's conflict count, and count_conflicts() sorts two scalar lists to
# get them. Its "sort step" is therefore that counting pass plus the sort itself,
# which together are the whole O(n log n) part of the algorithm.

def sort_earliest_finish(jobs):
    return sorted(jobs, key=lambda j: (j.finish, j.id))


def sort_earliest_start(jobs):
    return sorted(jobs, key=lambda j: (j.start, j.id))


def sort_shortest_duration(jobs):
    return sorted(jobs, key=lambda j: (j.finish - j.start, j.id))


def sort_group_heuristic(jobs):
    conflicts = count_conflicts(jobs)
    return sorted(jobs, key=lambda j: (conflicts[j], j.finish, j.id))


SORT_STEPS = {
    "earliest_finish": sort_earliest_finish,
    "earliest_start": sort_earliest_start,
    "shortest_duration": sort_shortest_duration,
    "group_heuristic": sort_group_heuristic,
}

# The two algorithms that do not pick jobs in time order, so they keep the selected
# list sorted with list.insert (see algorithms/shortest_duration.py).
INSERT_BASED = ["shortest_duration", "group_heuristic"]


# --------------------------------------------------------------------------- the insert step

def insert_profile(jobs, order):
    # Why the two insert-based algorithms get slow: list.insert(i, x) has to shift
    # every element after position i, so one insert costs O(len(selected) - i).
    # This repeats their selection loop, not to time it but to count the elements
    # those shifts move -- the measurement that says whether the O(n^2) worst case
    # is actually being hit. It mirrors the loop in algorithms/shortest_duration.py
    # and algorithms/group_heuristic.py; if those change, this has to change too.
    selected, starts, shifted, appends = [], [], 0, 0
    for job in order:
        i = bisect_right(starts, job.start)
        fits_after_previous = i == 0 or selected[i - 1].finish <= job.start
        fits_before_next = i == len(selected) or job.finish <= selected[i].start
        if fits_after_previous and fits_before_next:
            shifted += len(selected) - i  # 0 means it landed at the end: nothing moves
            appends += i == len(selected)
            selected.insert(i, job)
            starts.insert(i, job.start)
    return {"selected": len(selected), "elements_shifted": shifted,
            "mean_shift": shifted / len(selected) if selected else 0,
            "append_pct": 100 * appends / len(selected) if selected else 0}


# --------------------------------------------------------------------------- measuring

def time_callable(fn, jobs, repeats):
    # Median wall-clock seconds over `repeats` runs on the same instance, plus the
    # spread. Same instance every repeat, so repeats measure timing noise only.
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        fn(jobs)
        times.append(time.perf_counter() - start)
    return {"repeats": repeats, "median_seconds": statistics.median(times),
            "min_seconds": min(times), "max_seconds": max(times)}


def time_sorts(sizes, repeats, kind=KIND, seed=SEED):
    # Experiment 2: each algorithm's sort step alone, at every n.
    rows = []
    for n in sizes:
        jobs = generate(kind, n, seed)
        for name, sort_step in SORT_STEPS.items():
            measured = time_callable(sort_step, jobs, repeats)
            print(f"  {name:<18} n={n:<8} median {measured['median_seconds']:.5f}s  (sort only)")
            rows.append({"experiment": "sort", "algorithm": name, "kind": kind, "n": n,
                         "step": "sort", **measured})
    return pd.DataFrame(rows)


def time_kinds(n, repeats, seed=SEED):
    # Experiment 3: every generator kind at one n, with |selected| recorded, because
    # the insert cost in shortest_duration / group_heuristic scales with |selected|.
    rows = []
    for kind in KINDS:
        jobs = generate(kind, n, seed)
        for name, algorithm in GREEDY.items():
            measured = time_callable(algorithm, jobs, repeats)
            row = {"experiment": "kind", "algorithm": name, "kind": kind, "n": n,
                   "step": "full", "selected": len(algorithm(jobs)), **measured}
            if name in INSERT_BASED:
                row |= insert_profile(jobs, SORT_STEPS[name](jobs))
            rows.append(row)
            print(f"  {kind:<10} {name:<18} median {measured['median_seconds']:.5f}s  "
                  f"selected {row['selected']:,}" + (
                      f"  shifted {row['elements_shifted']:,} elements "
                      f"({row['append_pct']:.0f}% of inserts were appends)"
                      if name in INSERT_BASED else ""))
    return pd.DataFrame(rows)


def selected_counts(sizes, kind=KIND, seed=SEED):
    # |selected| for the main sweep. generate() is deterministic, so these are the
    # same instances time_algorithms() just measured.
    counts = {}
    for n in sizes:
        jobs = generate(kind, n, seed)
        for name, algorithm in GREEDY.items():
            counts[(name, n)] = len(algorithm(jobs))
    return counts


# --------------------------------------------------------------------------- the report table

def growth(n1, n2):
    # Expected cost multiplier from n1 to n2 under each candidate bound.
    return {"nlogn_growth": (n2 * log(n2)) / (n1 * log(n1)), "n2_growth": (n2 / n1) ** 2}


def summarize_runtime(long):
    # One row per (algorithm, n): total time, sort time, the sort's share of the
    # total, and the observed growth from the previous n next to what n log n and
    # n^2 predict for that step.
    full = long[(long["experiment"] == "main") & (long["step"] == "full")]
    sort = long[long["step"] == "sort"]
    table = full.merge(
        sort[["algorithm", "n", "median_seconds"]].rename(columns={"median_seconds": "sort_seconds"}),
        on=["algorithm", "n"], how="left",
    )
    # The sort and the full algorithm are timed in separate passes, so this ratio can
    # come out a little over 100% for earliest_finish / earliest_start, where the sort
    # really is almost the whole algorithm. Read anything near 100 as "all of it".
    table["sort_pct_of_total"] = 100 * table["sort_seconds"] / table["median_seconds"]

    rows = []
    for name in GREEDY:  # GREEDY order, not alphabetical
        part = table[table["algorithm"] == name].sort_values("n")
        previous = None
        for row in part.to_dict("records"):
            if previous is None:
                row |= {"observed_growth": float("nan"), "nlogn_growth": float("nan"),
                        "n2_growth": float("nan")}
            else:
                row |= {"observed_growth": row["median_seconds"] / previous["median_seconds"],
                        **growth(previous["n"], row["n"])}
            rows.append(row)
            previous = row
    columns = ["algorithm", "n", "selected", "repeats", "median_seconds", "min_seconds",
               "max_seconds", "sort_seconds", "sort_pct_of_total", "observed_growth",
               "nlogn_growth", "n2_growth"]
    summary = pd.DataFrame(rows)[columns].round(6)
    # `long` holds rows from every experiment, and the sort rows have no |selected|,
    # so the column arrives here as floats. These are counts.
    summary["selected"] = summary["selected"].astype(int)
    return summary


def report_table(summary):
    # Section 7's table: one row per n, one column per algorithm, median seconds.
    return summary.pivot(index="n", columns="algorithm", values="median_seconds")[list(GREEDY)]


# --------------------------------------------------------------------------- the figure

def runtime_chart(summary, path, kind=KIND):
    # Left: median time vs n on log-log axes, with an n log n reference line. A
    # straight line here means a power law, and the slope is the exponent; the
    # reference line is what Theta(n log n) looks like on these axes.
    # Right: how much of each running time is the sort, as n grows.
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(10, 4.4), dpi=200)
    sizes = sorted(summary["n"].unique())

    for name in GREEDY:
        part = summary[summary["algorithm"] == name].sort_values("n")
        ax.plot(part["n"], part["median_seconds"], label=name.replace("_", " ").title(),
                color=COLORS[name], marker=MARKERS[name], markersize=5.5, linewidth=2,
                markeredgecolor="white", markeredgewidth=0.8, zorder=3)

    # Anchored to the fastest algorithm at the smallest n, so it sits next to the data.
    anchor = summary[(summary["algorithm"] == "earliest_finish") & (summary["n"] == sizes[0])]
    scale = anchor["median_seconds"].iloc[0] / (sizes[0] * log(sizes[0]))
    ax.plot(sizes, [scale * n * log(n) for n in sizes], color=MUTED, linewidth=1,
            linestyle="--", zorder=1)
    # Below the line in open space: the guide runs almost underneath earliest_finish,
    # so a label sitting on it would be unreadable.
    label_at = sizes[len(sizes) // 2]
    ax.text(label_at, scale * label_at * log(label_at) * 0.4, "n log n", color=MUTED,
            fontsize=8, ha="center", va="top")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("n (jobs)", color=TEXT)
    ax.set_ylabel(f"Median of {summary['repeats'].iloc[0]} runs (seconds)", color=TEXT)
    ax.set_title("Running time vs instance size", color=TEXT, loc="left")

    width = 0.8 / len(GREEDY)
    for k, name in enumerate(GREEDY):
        part = summary[summary["algorithm"] == name].sort_values("n")
        xs = [i + (k - (len(GREEDY) - 1) / 2) * width for i in range(len(sizes))]
        # A white edge leaves a small gap between neighboring bars.
        bx.bar(xs, part["sort_pct_of_total"], width, color=COLORS[name],
               edgecolor="white", linewidth=1.5, zorder=2)

    bx.axhline(100, color=MUTED, linewidth=1, linestyle="--", zorder=1)
    bx.text(len(sizes) - 0.5, 100, "all of the running time", color=MUTED, fontsize=8,
            ha="right", va="bottom")
    bx.set_xticks(range(len(sizes)))
    bx.set_xticklabels([f"{n:,}" for n in sizes], color=TEXT)
    bx.set_ylim(0, 118)
    bx.set_xlabel("n (jobs)", color=TEXT)
    bx.set_ylabel("Sort step, % of running time", color=TEXT)
    bx.set_title("How much of the time is the sort", color=TEXT, loc="left")

    for axis in (ax, bx):
        axis.grid(axis="y", color=GRID, zorder=0)
        axis.tick_params(colors=MUTED, length=0)
        for side in ("top", "right", "left"):
            axis.spines[side].set_visible(False)
        axis.spines["bottom"].set_color(GRID)

    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=len(GREEDY), loc="lower center",
               bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f"Greedy running time on {kind} instances", color=TEXT, x=0.02, ha="left")
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    fig.savefig(path)
    plt.close(fig)


# --------------------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description="Benchmark the greedy algorithms (Part 6).")
    parser.add_argument("--sizes", type=int, nargs="+", default=SIZES, help="instance sizes")
    parser.add_argument("--repeats", type=int, default=REPEATS, help="runs per measurement")
    parser.add_argument("--kind", choices=KINDS, default=KIND, help="generator kind for the sweep")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--skip-kinds", action="store_true",
                        help="skip the per-kind experiment at the largest n")
    args = parser.parse_args()
    sizes = sorted(args.sizes)
    RESULTS_DIR.mkdir(exist_ok=True)

    print(f"Python {platform.python_version()} on {platform.platform()}")
    print(f"{platform.processor() or 'unknown cpu'}\n")
    print(f"Timing every greedy algorithm, {args.repeats} runs each, "
          f"kind={args.kind}, seed={args.seed}")
    print(f"n = {', '.join(f'{n:,}' for n in sizes)}\n")

    full = time_algorithms(sizes, args.repeats, kind=args.kind, seed=args.seed)
    full["experiment"], full["kind"], full["step"] = "main", args.kind, "full"
    counts = selected_counts(sizes, args.kind, args.seed)
    full["selected"] = [counts[(r.algorithm, r.n)] for r in full.itertuples()]

    print("\nTiming each algorithm's sort step alone...")
    sorts = time_sorts(sizes, args.repeats, args.kind, args.seed)

    kinds = pd.DataFrame()
    if not args.skip_kinds:
        print(f"\nTiming every generator kind at n = {sizes[-1]:,}...")
        kinds = time_kinds(sizes[-1], args.repeats, args.seed)

    long = pd.concat([full, sorts, kinds], ignore_index=True)
    long.to_csv(CSV_PATH, index=False)

    summary = summarize_runtime(long)
    summary.to_csv(SUMMARY_PATH, index=False)
    runtime_chart(summary, PNG_PATH, args.kind)

    print("\nPart 6: median seconds per algorithm (the section 7 table)\n")
    print(report_table(summary).to_string(float_format=lambda v: f"{v:.6f}"))
    print("\nPart 6: sort share and growth per step\n")
    # Per column, because seconds and growth factors are orders of magnitude apart.
    seconds = lambda v: f"{v:.6f}"
    factor = lambda v: "-" if pd.isna(v) else f"{v:.1f}x"
    print(summary.drop(columns=["repeats", "min_seconds", "max_seconds"]).to_string(
        index=False, na_rep="-", formatters={
            "median_seconds": seconds, "sort_seconds": seconds,
            "sort_pct_of_total": lambda v: f"{v:.1f}%", "observed_growth": factor,
            "nlogn_growth": factor, "n2_growth": factor,
        }))

    if not kinds.empty:
        print(f"\nPart 6: every kind at n = {sizes[-1]:,}\n")
        pivot = kinds.pivot(index="kind", columns="algorithm", values="median_seconds")
        print(pivot[list(GREEDY)].reindex(KINDS).to_string(float_format=lambda v: f"{v:.4f}"))
        print("\n  the insert-based two, in detail (why the kinds differ)\n")
        detail = kinds[kinds["algorithm"].isin(INSERT_BASED)].set_index(["algorithm", "kind"])
        print(detail[["median_seconds", "selected", "elements_shifted", "mean_shift",
                      "append_pct"]].to_string(formatters={
                          "median_seconds": seconds, "selected": lambda v: f"{int(v):,}",
                          "elements_shifted": lambda v: f"{int(v):,}",
                          "mean_shift": lambda v: f"{v:,.0f}",
                          "append_pct": lambda v: f"{v:.1f}%"}))

    print(f"\nSaved {len(long)} measurements to {CSV_PATH}")
    print(f"Saved the report table to {SUMMARY_PATH} and the figure to {PNG_PATH}")
    print("\nNote for the report: these timings are consistent with the analysis in "
          "section 2.\nThey do not prove any asymptotic bound.")


if __name__ == "__main__":
    main()
