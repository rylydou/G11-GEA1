# Every algorithm, in one place. run.py, runtime.py, the tests and the other
# scripts all loop over GREEDY, so anything listed here is included everywhere.

from algorithms.brute_force import brute_force
from algorithms.earliest_finish import earliest_finish
from algorithms.earliest_start import earliest_start
from algorithms.group_heuristic import group_heuristic
from algorithms.shortest_duration import shortest_duration

GREEDY = {
    "earliest_finish": earliest_finish,
    "earliest_start": earliest_start,
    "shortest_duration": shortest_duration,
    "group_heuristic": group_heuristic,
}
