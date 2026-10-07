# B. Earliest Start Time: repeatedly take the compatible job that starts first.
#
# Ordering: sort jobs by start time, then scan once. Because jobs are picked in
#           start order, a job is compatible with every selected job exactly when
#           it starts at or after the finish of the last selected job.
# Ties:     equal start times are broken by smaller job id.
# Runtime:  O(n log n). Sorting is O(n log n); the scan is O(n).

from jobs import Job


def earliest_start(jobs: list[Job]) -> list[Job]:
    selected = []
    last_finish = float("-inf")
    for job in sorted(jobs, key=lambda j: (j.start, j.id)):
        if job.start >= last_finish:
            selected.append(job)
            last_finish = job.finish
    return selected
