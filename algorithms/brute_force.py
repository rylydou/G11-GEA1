# Exact solver: the "answer key" every experiment compares against.
# Try every subset of jobs and keep the largest one with no overlaps.
#
# Runtime: TODO (expected O(2^n * n)). The report must explain why this only
# works for small n.

from jobs import Job

MAX_N = 20  # beyond this, brute force takes too long


def brute_force(jobs: list[Job]) -> list[Job]:
    # Return one optimal selection, sorted by start time. Don't modify `jobs`.
    if len(jobs) > MAX_N:
        raise ValueError(f"brute_force only handles n <= {MAX_N}, got {len(jobs)}")
    raise NotImplementedError("TODO")
