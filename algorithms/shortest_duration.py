# C. Shortest Duration: repeatedly take the compatible job with the smallest finish - start.
#
# Ordering: TODO
# Ties:     TODO (break by smaller job id so results are deterministic)
# Runtime:  TODO
#
# Careful: jobs are NOT picked in time order here, so a new job must be checked
# against ALL selected jobs, not just the last one picked.

from jobs import Job


def shortest_duration(jobs: list[Job]) -> list[Job]:
    # Return the selected jobs sorted by start time. Don't modify `jobs`.
    raise NotImplementedError("TODO")
