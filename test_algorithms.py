# Run with: pytest
# The first two tests are the sanity tests required by the assignment.

import pytest

from algorithms import GREEDY, brute_force, earliest_finish, earliest_start, shortest_duration
from generate import KINDS, generate
from jobs import Job, ids, is_valid_schedule

# Assignment sanity cases. Letters map to ids: A=0, B=1, C=2, D=3, E=4.
SANITY_1 = [Job(0, 0, 10), Job(1, 1, 2), Job(2, 2, 3), Job(3, 3, 4), Job(4, 4, 5)]
SANITY_2 = [Job(0, 2, 4), Job(1, 0, 3), Job(2, 3, 6)]


def test_sanity_1_earliest_start_fails():
    assert ids(earliest_start(SANITY_1)) == [0]  # picks A
    assert len(brute_force(SANITY_1)) == 4  # B, C, D, E


def test_sanity_2_shortest_duration_fails():
    assert ids(shortest_duration(SANITY_2)) == [0]  # picks A
    assert len(brute_force(SANITY_2)) == 2  # B, C


def test_earliest_finish_on_sanity_cases():
    assert ids(earliest_finish(SANITY_1)) == [1, 2, 3, 4]
    assert ids(earliest_finish(SANITY_2)) == [1, 2]


def test_half_open_intervals():
    assert is_valid_schedule([Job(0, 0, 5), Job(1, 5, 9)])  # touching is fine
    assert not is_valid_schedule([Job(0, 0, 5), Job(1, 4, 9)])


def test_brute_force_small_cases():
    assert brute_force([]) == []
    assert len(brute_force([Job(0, 0, 10), Job(1, 1, 9), Job(2, 2, 8)])) == 1
    assert len(brute_force([Job(0, 0, 1), Job(1, 1, 2), Job(2, 2, 3)])) == 3


@pytest.mark.parametrize("kind", KINDS)
def test_generator_is_reproducible(kind):
    jobs = generate(kind, 15, seed=7)
    assert jobs == generate(kind, 15, seed=7)
    assert [j.id for j in jobs] == list(range(15))
    assert all(j.start < j.finish for j in jobs)


@pytest.mark.parametrize("name", GREEDY)
@pytest.mark.parametrize("kind", KINDS)
def test_greedy_output_is_valid(name, kind):
    for seed in range(20):
        jobs = generate(kind, 10, seed)
        original = list(jobs)
        selected = GREEDY[name](jobs)
        assert jobs == original, "modified its input"
        assert is_valid_schedule(selected)
        assert set(selected) <= set(jobs)
        assert len(selected) <= len(brute_force(jobs))
        assert GREEDY[name](jobs) == selected, "not deterministic"


@pytest.mark.parametrize("kind", KINDS)
def test_earliest_finish_matches_brute_force(kind):
    for seed in range(20):
        jobs = generate(kind, 10, seed)
        assert len(earliest_finish(jobs)) == len(brute_force(jobs))
