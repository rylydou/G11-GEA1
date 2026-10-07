# Exact solver: the "answer key" every experiment compares against.
# Try subsets of jobs from largest to smallest; the first subset with no overlaps
# is a maximum one.
#
# Ties:     jobs are sorted by (start, id) first, and subsets are tried in a fixed
#           order, so the same input always returns the same optimal solution.
# Runtime:  O(2^n * n) in the worst case. There are 2^n subsets, and checking one
#           takes O(n) (sorting by start up front means every subset is already
#           in time order, so we only compare neighbors). Each extra job doubles
#           the work: n = 20 means about a million subsets, which is why this is
#           only practical for small n.

from itertools import combinations

from jobs import Job

MAX_N = 20  # beyond this, brute force takes too long


def brute_force(jobs: list[Job]) -> list[Job]:
    if len(jobs) > MAX_N:
        raise ValueError(f"brute_force only handles n <= {MAX_N}, got {len(jobs)}")

    ordered = sorted(jobs, key=lambda j: (j.start, j.id))
    for size in range(len(ordered), 0, -1):
        for subset in combinations(ordered, size):  # keeps start-time order
            if all(a.finish <= b.start for a, b in zip(subset, subset[1:])):
                return list(subset)
    return []
