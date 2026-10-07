# Random test data in four kinds, so experiments don't all use one distribution.
#
# generate(kind, n, seed) always returns the same instance for the same
# arguments. results/results.csv records (kind, n, seed) so any instance can be rebuilt.
#
# The timeline length grows with n, so each kind keeps roughly the same overlap
# density from n = 4 (brute-force experiments) up to n = 100,000 (runtime).

import random

from jobs import Job

KINDS = ["sparse", "dense", "varied", "clustered"]


def generate(kind: str, n: int, seed: int) -> list[Job]:
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}, expected one of {KINDS}")
    rng = random.Random(seed)  # use only rng, never the global random module

    if kind == "clustered":
        centers = [rng.randint(0, 10 * n) for _ in range(max(2, n // 4))]

    jobs = []
    for i in range(n):
        if kind == "sparse":
            # Short jobs spread over a long timeline: few overlaps.
            start = rng.randint(0, 20 * n)
            length = rng.randint(1, 5)
        elif kind == "dense":
            # Longer jobs packed into a short timeline: heavy overlap.
            start = rng.randint(0, 2 * n)
            length = rng.randint(2, 8)
        elif kind == "varied":
            # Mostly short jobs plus some very long ones that cover many short ones.
            start = rng.randint(0, 10 * n)
            length = rng.randint(1, 5) if rng.random() < 0.7 else rng.randint(20, 60)
        else:  # clustered
            # Start times bunched around a few points on the timeline.
            start = rng.choice(centers) + rng.randint(0, 5)
            length = rng.randint(1, 6)
        jobs.append(Job(i, start, start + length))
    return jobs
