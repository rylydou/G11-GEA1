# The Job type and small helpers shared by every file.
#
# Intervals are half-open [start, finish): a job that finishes at time t does
# NOT overlap a job that starts at time t.

import csv
from typing import NamedTuple


class Job(NamedTuple):
    id: int
    start: int
    finish: int


def overlaps(a: Job, b: Job) -> bool:
    return a.start < b.finish and b.start < a.finish


def is_valid_schedule(jobs: list[Job]) -> bool:
    # True if no two jobs in the list overlap.
    ordered = sorted(jobs, key=lambda j: j.start)
    return all(a.finish <= b.start for a, b in zip(ordered, ordered[1:]))


def ids(jobs: list[Job]) -> list[int]:
    # Sorted job ids, the standard way to print or save a selection.
    return sorted(j.id for j in jobs)


def read_jobs(path: str) -> list[Job]:
    # CSV file with a header row: id,start,finish
    with open(path, newline="") as f:
        return [Job(int(r["id"]), int(r["start"]), int(r["finish"])) for r in csv.DictReader(f)]
