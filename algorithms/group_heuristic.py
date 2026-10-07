# D. Our group's heuristic: Fewest Conflicts.
# Repeatedly take the compatible job that overlaps the fewest other jobs. The
# idea is that a job with few conflicts blocks the fewest alternatives.
#
# Ordering: count each job's conflicts once, in the original input (we do not
#           recount after each pick). Sort by conflict count, then try each job
#           in that order, keeping it if it fits.
# Ties:     equal conflict counts are broken by earlier finish time, then smaller id.
# Runtime:  O(n log n) to count conflicts and sort. Counting uses two sorted
#           lists and binary search (see below) instead of comparing every pair,
#           which would be O(n^2). Picking jobs works like shortest_duration.py:
#           O(log n) to check each job, with an O(n) worst-case list insert.

from bisect import bisect_left, bisect_right

from jobs import Job


def count_conflicts(jobs: list[Job]) -> dict[Job, int]:
    # Job k overlaps job j when k.start < j.finish and j.start < k.finish.
    #   jobs starting before j finishes:    bisect_left(starts, j.finish)
    #   ...minus jobs that ended by j.start: bisect_right(finishes, j.start)
    #   ...minus j itself:                   1
    starts = sorted(j.start for j in jobs)
    finishes = sorted(j.finish for j in jobs)
    return {
        j: bisect_left(starts, j.finish) - bisect_right(finishes, j.start) - 1
        for j in jobs
    }


def group_heuristic(jobs: list[Job]) -> list[Job]:
    conflicts = count_conflicts(jobs)
    selected = []  # selected jobs, kept sorted by start time
    starts = []    # their start times, for binary search
    for job in sorted(jobs, key=lambda j: (conflicts[j], j.finish, j.id)):
        i = bisect_right(starts, job.start)
        fits_after_previous = i == 0 or selected[i - 1].finish <= job.start
        fits_before_next = i == len(selected) or job.finish <= selected[i].start
        if fits_after_previous and fits_before_next:
            selected.insert(i, job)
            starts.insert(i, job.start)
    return selected
