# GEA1: Interval Scheduling

CMP_SC 4050, Group Algorithm Engineering Assignment 1. Four greedy algorithms for
interval scheduling, compared against a brute-force exact solver on generated test data.

Language: **Python 3.10+**. Libraries: matplotlib, pandas, pytest.

## Files

| File | What | Owner |
|---|---|---|
| `jobs.py` | `Job` type, overlap check, CSV reader | shared |
| `generate.py` | random test data (sparse / dense / varied / clustered) | shared |
| `algorithms/` | one file per algorithm, plus `brute_force.py` (the exact solver) | shared |
| `run.py` | runs every algorithm on generated data, saves results, prints summary | shared |
| `test_algorithms.py` | required sanity tests + correctness checks | shared |
| `counterexamples.py` | Part 3: counterexample search + timeline | P1 |
| `analysis.py` | Parts 4–5: validation + comparison tables/charts | P2 |
| `runtime.py` | Part 6: runtime benchmark | P3 |
| `results/` | every generated CSV, JSON and PNG | — |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
pytest                       # sanity tests + correctness checks
python run.py                # generate 200 instances, compare to brute force -> results/results.csv
python counterexamples.py    # Part 3
python analysis.py           # Parts 4-5
python runtime.py            # Part 6
```

Running those commands in that order reproduces every result. All randomness is seeded
(`SEED = 4050` in `run.py`), so the output is the same every time.

## Input format

To run every algorithm on your own instance, use a CSV file with a header row.
Times are integers, and intervals are half-open `[start, finish)`:

```
id,start,finish
0,0,10
1,1,2
```

```bash
python run.py --file example_jobs.csv
```
