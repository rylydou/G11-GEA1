# B. Earliest Start Time: repeatedly take the compatible job that starts first.
#
# Ordering: TODO
# Ties:     TODO (break by smaller job id so results are deterministic)
# Runtime:  TODO

from jobs import Job


def earliest_start(jobs: list[Job]) -> list[Job]:
    # Return the selected jobs sorted by start time. Don't modify `jobs`.
    raise NotImplementedError("TODO")
