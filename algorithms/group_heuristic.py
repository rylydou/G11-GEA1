# D. Our group's heuristic. Decide the rule in the group session.
#
# Suggestion: Fewest Conflicts, i.e. repeatedly take the compatible job that
# overlaps the fewest other remaining jobs. Avoid "latest start time": it
# mirrors Earliest Finish, so it is always optimal and has no counterexample.
#
# Ordering: TODO
# Ties:     TODO (break by smaller job id so results are deterministic)
# Runtime:  TODO

from jobs import Job


def group_heuristic(jobs: list[Job]) -> list[Job]:
    # Return the selected jobs sorted by start time. Don't modify `jobs`.
    raise NotImplementedError("TODO")
