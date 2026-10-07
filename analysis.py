# Parts 4 and 5: validate Earliest Finish and compare all four algorithms.  Owner: P2
#
#   python run.py         (first, creates results/results.csv)
#   python analysis.py
#
# run.py already prints the headline numbers. This script produces the tables
# and charts for the report.
#
# Outputs: results/eft_validation.csv    Part 4: tested / matched per kind
#          results/summary.csv           Part 5: % optimal, mean ratio, worst instance
#          results/summary_by_kind.csv   Part 5: same, broken down by kind
#          results/comparison.png        Part 5: chart

import json

import matplotlib.pyplot as plt
import pandas as pd

from generate import KINDS
from run import RESULTS_CSV, RESULTS_DIR, summarize

# One fixed color per kind (categorical slots 1-4, validated for adjacent bars).
KIND_COLORS = {"sparse": "#2a78d6", "dense": "#eb6834", "varied": "#1baf7a", "clustered": "#eda100"}
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def eft_validation(results):
    # Part 4: per kind, how many instances Earliest Finish was tested on and how
    # many it matched brute force on, plus an overall row.
    eft = results[results["algorithm"] == "earliest_finish"]
    table = eft.groupby("kind").agg(tested=("optimal", "size"), matched=("optimal", "sum"))
    table = table.reindex(KINDS)
    table.loc["all"] = table.sum()
    table["match_rate"] = (100 * table["matched"] / table["tested"]).round(1)

    mismatches = eft[~eft["optimal"]]
    if len(mismatches):
        print(f"!!! BUG: Earliest Finish missed OPT on {len(mismatches)} instances: "
              f"{mismatches['instance'].tolist()}")
    return table


def summary_by_kind(results):
    # Part 5: summarize() run separately on each kind of instance.
    parts = [summarize(results[results["kind"] == kind]).assign(kind=kind) for kind in KINDS]
    return pd.concat(parts).reset_index().set_index(["kind", "algorithm"])


def comparison_chart(by_kind, path):
    # Part 5: grouped bars, mean |H(I)| / OPT(I) per algorithm, one bar per kind.
    algorithms = list(by_kind.index.get_level_values("algorithm").unique())
    width = 0.8 / len(KINDS)
    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=200)

    for k, kind in enumerate(KINDS):
        ratios = [by_kind.loc[(kind, a), "mean_ratio"] for a in algorithms]
        xs = [i + (k - (len(KINDS) - 1) / 2) * width for i in range(len(algorithms))]
        # A white edge leaves a small gap between neighboring bars.
        ax.bar(xs, ratios, width, label=kind, color=KIND_COLORS[kind],
               edgecolor="white", linewidth=1.5, zorder=2)

    ax.axhline(1.0, color=MUTED, linewidth=1, linestyle="--", zorder=1)
    ax.text(len(algorithms) - 0.5, 1.0, "optimal", color=MUTED, fontsize=8, ha="right", va="bottom")

    ax.set_xticks(range(len(algorithms)))
    ax.set_xticklabels([a.replace("_", " ").title() for a in algorithms], color=TEXT)
    ax.set_ylabel("Mean |H(I)| / OPT(I)", color=TEXT)
    ax.set_ylim(0, 1.08)
    ax.set_title("How close each greedy algorithm gets to optimal, by instance kind",
                 color=TEXT, loc="left")
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.tick_params(colors=MUTED, length=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.legend(title="Instance kind", frameon=False, ncol=len(KINDS),
              loc="upper center", bbox_to_anchor=(0.5, -0.1))

    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def print_worst_instances(results):
    # Part 5: each algorithm's worst instance, to help explain what misleads it.
    worst = results.loc[results.groupby("algorithm")["ratio"].idxmin()]
    for row in worst.itertuples():
        print(f"\n{row.algorithm}: instance {row.instance} ({row.kind}, n={row.n}, seed={row.seed}) "
              f"picked {row.size} of {row.opt}, ratio {row.ratio:.3f}")
        print(f"  jobs [id, start, finish]: {json.loads(row.jobs)}")
        print(f"  picked ids:  {json.loads(row.selected_ids)}")
        print(f"  optimal ids: {json.loads(row.opt_ids)}")


def main():
    results = pd.read_csv(RESULTS_CSV)

    summary = summarize(results)
    summary.to_csv(RESULTS_DIR / "summary.csv")

    validation = eft_validation(results)
    validation.to_csv(RESULTS_DIR / "eft_validation.csv")

    by_kind = summary_by_kind(results)
    by_kind.to_csv(RESULTS_DIR / "summary_by_kind.csv")

    comparison_chart(by_kind, RESULTS_DIR / "comparison.png")

    print("Part 4: Earliest Finish validation\n")
    print(validation.to_string())
    print("\nPart 5: overall comparison\n")
    print(summary.to_string())
    print("\nPart 5: by kind\n")
    print(by_kind.to_string())
    print("\nPart 5: worst instance per algorithm")
    print_worst_instances(results)
    print(f"\nSaved tables and chart to {RESULTS_DIR}")


if __name__ == "__main__":
    main()
