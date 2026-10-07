# C. Shortest Duration: repeatedly take the compatible job with the smallest finish - start.
#
# Ordering: sort jobs by duration, then try each one in that order.
# Ties:     equal durations are broken by smaller job id.
# Runtime:  O(n log n) to sort. Jobs are NOT picked in time order, so each
#           candidate must be checked against every selected job. We keep the
#           selected jobs sorted by start time and binary-search for where the
#           candidate would go; since selected jobs never overlap, only its two
#           neighbors need checking (O(log n) per job). Inserting into a Python
#           list shifts elements, which is O(n) in the worst case, so the strict
#           bound is O(n^2), but that shift is a fast memory copy in practice.

from bisect import bisect_right

from jobs import Job


def shortest_duration(jobs: list[Job]) -> list[Job]:
    selected = []  # selected jobs, kept sorted by start time
    starts = []    # their start times, for binary search
    for job in sorted(jobs, key=lambda j: (j.finish - j.start, j.id)):
        i = bisect_right(starts, job.start)
        fits_after_previous = i == 0 or selected[i - 1].finish <= job.start
        fits_before_next = i == len(selected) or job.finish <= selected[i].start
        if fits_after_previous and fits_before_next:
            selected.insert(i, job)
            starts.insert(i, job.start)
    return selected
