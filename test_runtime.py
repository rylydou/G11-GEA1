# Run with: pytest
# Checks for Part 6 (runtime.py). The benchmark itself is not tested for speed --
# timings are not reproducible enough to assert on. What is tested is the thing
# that can silently go wrong: runtime.py restates each algorithm's sort key, so it
# can drift away from algorithms/*.py and quietly measure the wrong sort.

import math

import pandas as pd
import pytest

from algorithms import GREEDY
from generate import KINDS, generate
from jobs import Job
from runtime import SORT_STEPS, growth, report_table, summarize_runtime, time_callable


@pytest.mark.parametrize("name", GREEDY)
def test_every_algorithm_has_a_sort_step(name):
    assert name in SORT_STEPS


@pytest.mark.parametrize("name", SORT_STEPS)
@pytest.mark.parametrize("kind", KINDS)
def test_sort_step_only_reorders(name, kind):
    jobs = generate(kind, 40, seed=11)
    original = list(jobs)
    ordered = SORT_STEPS[name](jobs)
    assert jobs == original, "sort step modified its input"
    assert sorted(ordered) == sorted(jobs), "sort step is not a permutation of the input"


@pytest.mark.parametrize("name", SORT_STEPS)
@pytest.mark.parametrize("kind", KINDS)
def test_sort_step_agrees_with_the_algorithm(name, kind):
    # All four algorithms work the same way: walk the jobs in sort order, keep each
    # one that fits. The first job in that order always fits, because nothing is
    # selected yet -- so it must appear in the algorithm's output. If runtime.py's
    # key no longer matches the algorithm's, this picks a different first job and
    # usually one that the algorithm did not select.
    for seed in range(25):
        jobs = generate(kind, 12, seed)
        first = SORT_STEPS[name](jobs)[0]
        assert first in GREEDY[name](jobs), f"{name}: sort key disagrees on {jobs}"


def test_sort_step_agrees_on_the_sanity_cases():
    # The assignment's two known failures, where the heuristics pick one long job.
    sanity_1 = [Job(0, 0, 10), Job(1, 1, 2), Job(2, 2, 3), Job(3, 3, 4), Job(4, 4, 5)]
    sanity_2 = [Job(0, 2, 4), Job(1, 0, 3), Job(2, 3, 6)]
    assert SORT_STEPS["earliest_start"](sanity_1)[0].id == 0  # A starts first
    assert SORT_STEPS["shortest_duration"](sanity_2)[0].id == 0  # A is shortest
    assert SORT_STEPS["earliest_finish"](sanity_1)[0].id == 1  # B finishes first


def test_time_callable_reports_a_median_and_spread():
    jobs = generate("varied", 50, seed=3)
    measured = time_callable(GREEDY["earliest_finish"], jobs, repeats=3)
    assert measured["repeats"] == 3
    assert measured["min_seconds"] <= measured["median_seconds"] <= measured["max_seconds"]
    assert measured["min_seconds"] > 0


def test_growth_predictions():
    # A 10x step: n log n predicts ~13x, n^2 predicts exactly 100x.
    predicted = growth(10_000, 100_000)
    assert predicted["n2_growth"] == pytest.approx(100)
    assert predicted["nlogn_growth"] == pytest.approx(12.5, rel=0.01)
    # Doubling n: n log n is a little over 2x, n^2 is 4x.
    doubled = growth(1_000, 2_000)
    assert 2 < doubled["nlogn_growth"] < 2.3
    assert doubled["n2_growth"] == pytest.approx(4)


def fake_long(median_by_n, sort_by_n, algorithm="earliest_finish"):
    rows = []
    for n, seconds in median_by_n.items():
        rows.append({"experiment": "main", "algorithm": algorithm, "kind": "varied", "n": n,
                     "step": "full", "repeats": 5, "median_seconds": seconds,
                     "min_seconds": seconds, "max_seconds": seconds, "selected": n // 2})
        rows.append({"experiment": "sort", "algorithm": algorithm, "kind": "varied", "n": n,
                     "step": "sort", "repeats": 5, "median_seconds": sort_by_n[n],
                     "min_seconds": sort_by_n[n], "max_seconds": sort_by_n[n]})
    return pd.DataFrame(rows)


def test_summarize_runtime_derives_share_and_growth():
    long = fake_long({100: 1.0, 1_000: 10.0}, {100: 0.5, 1_000: 8.0})
    summary = summarize_runtime(long)

    assert list(summary["n"]) == [100, 1_000]
    assert math.isnan(summary.loc[0, "observed_growth"]), "first n has no previous step"
    assert summary.loc[0, "sort_pct_of_total"] == pytest.approx(50)
    assert summary.loc[1, "sort_pct_of_total"] == pytest.approx(80)
    assert summary.loc[1, "observed_growth"] == pytest.approx(10)
    assert summary.loc[1, "n2_growth"] == pytest.approx(100)
    assert summary.loc[1, "nlogn_growth"] == pytest.approx(15, rel=0.01)


def test_summarize_runtime_keeps_every_algorithm_and_size():
    long = pd.concat([fake_long({100: 1.0, 1_000: 2.0}, {100: 0.5, 1_000: 1.0}, name)
                      for name in GREEDY], ignore_index=True)
    summary = summarize_runtime(long)
    assert len(summary) == 2 * len(GREEDY)
    assert list(summary["algorithm"].unique()) == list(GREEDY), "lost GREEDY order"

    table = report_table(summary)
    assert list(table.columns) == list(GREEDY)
    assert list(table.index) == [100, 1_000]
