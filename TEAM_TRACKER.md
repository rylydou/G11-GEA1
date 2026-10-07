# GEA1 Team Tracker

**Due: Thursday 10/9/2026, 11:59 pm** · Repo: (link) · Report doc: (link)

## The assignment in brief

We are given jobs with start and finish times and must pick the most jobs that don't overlap. A job ending at time 5 does not conflict with one starting at 5. We will:

1. **Build** four greedy algorithms (Earliest Finish, Earliest Start, Shortest Duration, plus one of our own) and a slow brute-force solver that always finds the best answer.
2. **Test** that Earliest Finish matches brute force on at least 100 random instances.
3. **Break** the other algorithms by automatically searching for inputs where they fail.
4. **Measure** how often each algorithm is optimal, and how fast each runs as inputs grow.
5. **Explain** it all in a 4–6 page report.

**Key ideas the report must get right:**

- A counterexample proves an algorithm is wrong. Passing tests does not prove it is right.
- Timing measurements are "consistent with" a Big-O bound. They don't prove it.
- Every number in the report must come from our code, never typed in by hand.

## Who does what

| Person | Name | Owns |
|---|---|---|
| P1 | | Part 3: counterexample search + timeline figure (`counterexamples.py`) |
| P2 | | Parts 4–5: validation + comparison tables and charts (`analysis.py`) |
| P3 | | Part 6: runtime benchmark (`runtime.py`) |
| P4 | | Report, reflection, README, final check that everything reproduces |
| Everyone | | Group session: algorithms, brute force, test data generator |

## Group session (today, 2–3 hours)

- [ ] Agree on our own heuristic (D) and fill in names above (15 min)
- [ ] Write the four greedy algorithms in `algorithms/`, with ordering / ties / runtime comments (30 min)
- [ ] Write `algorithms/brute_force.py` (20 min)
- [ ] Both required sanity tests pass: `pytest -k sanity` (15 min)
- [ ] Write `generate.py` for all four kinds of test data (30 min)
- [ ] All tests pass: `pytest` (20 min)
- [ ] `python run.py` works, and we look at the summary together (20 min)
- [ ] P4 takes notes on decisions and why we made them (these go into report sections 2–3)

## To-do by person (after the session)

**P1: Counterexamples**

- [ ] Automatic search finds a counterexample for Earliest Start
- [ ] … and for Shortest Duration
- [ ] … and for our heuristic, or document "none found after N tries up to n = K"
- [ ] Save them to `results/counterexamples.json`
- [ ] Timeline figure for at least one counterexample
- [ ] Write report Section 4, including the "counterexample vs. proof" discussion
- [ ] Review P3's code

**P2: Validation + comparison**

- [ ] Earliest Finish validation table per kind (at least 100 instances)
- [ ] Comparison table: % optimal, average ratio, worst instance per algorithm
- [ ] Breakdown by kind, plus a comparison chart
- [ ] Write report Sections 5–6, including what misleads each heuristic
- [ ] Review P1's code

**P3: Runtime**

- [ ] Timings at n = 100, 1,000, 10,000, 100,000 (median of repeated runs)
- [ ] Time sorting alone, to show where the sort cost appears
- [ ] Log-log runtime plot
- [ ] Write report Section 7
- [ ] Review P2's code

**P4: Report + final check**

- [ ] Write report Sections 1–3 from session notes
- [ ] Collect everyone's reflection notes and write Section 8, then the conclusion
- [ ] Contribution statement + AI use statement (ask everyone what AI they used)
- [ ] Review the shared code (`run.py`, `generate.py`, `algorithms/`)
- [ ] Final check: fresh clone, follow the README, confirm every result reproduces
- [ ] Export the report to PDF and submit

## Everyone (before submitting)

- [ ] Add your notes under each reflection question in the report doc
- [ ] Tell P4 which AI tools you used and how
- [ ] Confirm your line in the contribution statement

## Timeline

| When | Milestone |
|---|---|
| Wed 10/7 | Group session done: all tests pass, `python run.py` works |
| Thu 10/8 | Individual parts done, results in `results/`, report sections drafted, code reviewed |
| Fri 10/9 | Report finished, fresh-clone check passed, submitted by 11:59 pm |

## Requirements checklist (from the assignment)

| Requirement | Points | Where | Done |
|---|---|---|---|
| Four greedy algorithms, each returning the selected jobs, with ordering / ties / runtime documented | 25 | `algorithms/` + report §2 | ☐ |
| Exact brute-force solver, with runtime and small-n explanation | 15 | `algorithms/brute_force.py` + report §3 | ☐ |
| Counterexample search; full details for each; at least one timeline; "proof vs. no counterexample" discussion | 20 | `counterexamples.py` + report §4 | ☐ |
| Earliest Finish validated on at least 100 instances of several kinds; matched / tested reported | 15 | `run.py`, `analysis.py` + report §5 | ☐ |
| Comparison: % optimal, average ratio, worst instance, table or graph, discussion | 10 | `analysis.py` + report §6 | ☐ |
| Runtime at increasing n, median of repeats, sorting explained, no overclaiming | 10 | `runtime.py` + report §7 | ☐ |
| Reflection: all four questions, with real analysis | 5 | report §8 | ☐ |
| Two required sanity tests pass | — | `test_algorithms.py` | ☐ |
| README: language/version, how to run, input format, how to reproduce | — | `README.md` | ☐ |
| Machine-readable results (CSV/JSON) | — | `results/` | ☐ |
| Group contribution statement | — | report | ☐ |
| AI use statement | — | report | ☐ |
