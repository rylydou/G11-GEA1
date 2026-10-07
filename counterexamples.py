# Part 3: automatically find inputs where a greedy algorithm is not optimal.  Owner: P1
#
#   python counterexamples.py
#
# Needs at least one counterexample each for earliest_start and shortest_duration,
# plus group_heuristic if the search finds one. For each one, the report needs:
# the input intervals, the greedy picks, an optimal solution, and both sizes.
#
# Outputs: results/counterexamples.json
#          results/counterexample_<algorithm>.png (at least one timeline)

import json

import matplotlib.pyplot as plt

from algorithms import GREEDY, brute_force
from generate import KINDS, generate
from jobs import ids
from run import RESULTS_DIR, SEED


def find_counterexample(name, max_n=12, tries_per_n=500, seed=SEED):
    # Try small sizes first (n = 2, 3, ...) so the counterexample is easy to read.
    # Return a dict with: algorithm, kind, n, seed, jobs, greedy_ids, opt_ids,
    # greedy_size, opt_size. Return None if nothing was found.
    # Tip: results/results.csv (from run.py) already has suboptimal rows you can reuse.
    raise NotImplementedError("TODO")


def plot_timeline(example, path):
    # Draw each job as a horizontal bar. Highlight the greedy picks and the
    # optimal picks in different colors, or draw them as two panels.
    raise NotImplementedError("TODO")


def main():
    # TODO: run find_counterexample for every algorithm except earliest_finish,
    # save all of them to results/counterexamples.json, plot at least one
    # timeline, and print a one-line summary for each (e.g. "|Greedy| = 1, OPT = 4").
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    main()
