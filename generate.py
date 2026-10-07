# Random test data. Built together in the group session.
#
# generate(kind, n, seed) must always return the same instance for the same
# arguments. results/results.csv records (kind, n, seed) so any instance can be rebuilt.

import random

from jobs import Job

KINDS = ["sparse", "dense", "varied", "clustered"]


def generate(kind: str, n: int, seed: int) -> list[Job]:
    rng = random.Random(seed)  # use only rng, never the global random module

    # TODO: return n jobs with ids 0..n-1 and integer times (start < finish).
    #   sparse    - short jobs spread over a long timeline (few overlaps)
    #   dense     - long jobs packed into a short timeline (heavy overlap)
    #   varied    - a mix of very short and very long jobs
    #   clustered - start times bunched around a few points
    raise NotImplementedError("TODO")
