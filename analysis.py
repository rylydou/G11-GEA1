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

import matplotlib.pyplot as plt
import pandas as pd

from run import RESULTS_CSV, RESULTS_DIR, summarize


def main():
    results = pd.read_csv(RESULTS_CSV)

    summarize(results).to_csv(RESULTS_DIR / "summary.csv")

    # TODO Part 4: for earliest_finish, count tested vs matched per kind plus an
    #   overall row -> results/eft_validation.csv. Print any mismatch loudly (it's a bug).
    # TODO Part 5: summarize() for each kind -> results/summary_by_kind.csv
    # TODO Part 5: bar chart of mean ratio per algorithm (one bar per kind) -> results/comparison.png
    # TODO Part 5: print each algorithm's worst instance (its jobs and picks) to help
    #   explain what kinds of inputs mislead it.
    raise NotImplementedError("TODO")


if __name__ == "__main__":
    main()
