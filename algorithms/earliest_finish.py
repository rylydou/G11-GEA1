# A. Earliest Finish Time: repeatedly take the compatible job that finishes first.
# This is the greedy algorithm from class. It should always match brute force.
#
# Ordering: TODO
# Ties:     TODO (break by smaller job id so results are deterministic)
# Runtime:  TODO

from jobs import Job


def earliest_finish(jobs: list[Job]) -> list[Job]:
    # Return the selected jobs sorted by start time. Don't modify `jobs`.
    raise NotImplementedError("TODO")
