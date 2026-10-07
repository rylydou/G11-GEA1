# A. Earliest Finish Time: repeatedly take the compatible job that finishes first.
# This is the greedy algorithm from class. It should always match brute force.
#
# Ordering: sort jobs by finish time, then scan once. A job is compatible if it
#           starts at or after the finish of the last selected job.
# Ties:     equal finish times are broken by smaller job id.
# Runtime:  O(n log n). Sorting is O(n log n); the scan is O(n) because each job
#           is compared only with the last selected job.

from jobs import Job


def earliest_finish(jobs: list[Job]) -> list[Job]:
    selected = []
    last_finish = float("-inf")
    for job in sorted(jobs, key=lambda j: (j.finish, j.id)):
        if job.start >= last_finish:
            selected.append(job)
            last_finish = job.finish
    # Selected jobs are already in time order: they don't overlap and finish in increasing order.
    return selected
