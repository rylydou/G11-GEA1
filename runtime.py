# Part 6: runtime of the greedy algorithms on large inputs.  Owner: P3
#
#   python runtime.py
#
# Greedy algorithms only; brute force can't handle these sizes.
# If an O(n^2) algorithm is too slow at 100,000, note it and drop that size for it.
#
# Outputs: results/runtime.csv   median seconds per algorithm and n
#          results/runtime.png   time vs n on log-log axes

import matplotlib.pyplot as plt

from run import RESULTS_DIR, time_algorithms

SIZES = [100, 1_000, 10_000, 100_000]
REPEATS = 5


def main():
    timings = time_algorithms(SIZES, REPEATS)
    RESULTS_DIR.mkdir(exist_ok=True)
    timings.to_csv(RESULTS_DIR / "runtime.csv", index=False)

    # TODO: also time sorting alone (sorted(jobs, key=...)) at each n, to show how
    #   much of each algorithm's runtime is the sort.
    # TODO: log-log plot of median time vs n, with an n log n reference line
    #   -> results/runtime.png
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    main()
