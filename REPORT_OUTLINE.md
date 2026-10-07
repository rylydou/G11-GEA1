# Greedy Algorithms Under Pressure: Interval Scheduling

CMP_SC 4050: Group Algorithm Engineering Assignment 1

Team: P1 NAME, P2 NAME, P3 NAME, P4 NAME

*Target length: 4–6 pages total. Each section lists its owner, rough length, and what it must cover. Delete these italic notes before submitting.*

---

## 1. Introduction

*Owner: P4 · ~1 paragraph*

- The problem: n jobs with start and finish times; choose the most jobs that don't overlap. Intervals are half-open [s, f).
- Our approach: implement, test, break, measure, explain.
- How experiments work: every algorithm runs on the same generated instances and is compared against a brute-force exact solver.

## 2. Greedy Algorithms (Part 1, 25 pts)

*Owner: P4, from group-session notes and the comments at the top of each file in `algorithms/` · ~3/4 page*

| Algorithm | Selection rule | Tie-breaking | Running time |
|---|---|---|---|
| A. Earliest Finish | | | |
| B. Earliest Start | | | |
| C. Shortest Duration | | | |
| D. (group heuristic name) | | | |

- Why our group heuristic (D) is genuinely different from A–C.
- Where sorting appears in each running time.
- Tie-breaking is deterministic (by job id), so results are reproducible.

## 3. Exact Solver (Part 2, 15 pts)

*Owner: P4 · ~1/3 page*

- How brute force works.
- Its running time, and why it is only practical for small n (give a concrete example, such as time at n = 20).
- Its role as the answer key for all experiments.

## 4. Counterexamples (Part 3, 20 pts)

*Owner: P1 · ~1 page · data: `results/counterexamples.json`*

- How the automatic search works.
- One counterexample each for Earliest Start and Shortest Duration, plus our heuristic, or an honest "none found after N tries up to n = K".

| Algorithm | Input intervals | Greedy picks | Optimal picks | \|Greedy(I)\| | OPT(I) |
|---|---|---|---|---|---|
| Earliest Start | | | | | |
| Shortest Duration | | | | | |
| Group heuristic | | | | | |

*[Figure: timeline of at least one counterexample, from `results/counterexample_<algorithm>.png`]*

- **Required discussion:** a counterexample *proves* an algorithm is not always optimal. Failing to find one does *not* prove it is optimal.

## 5. Validating Earliest Finish (Part 4, 15 pts)

*Owner: P2 · ~1/2 page · data: `results/eft_validation.csv`*

- The four kinds of generated instances (sparse, dense, varied, clustered), instance sizes, and seeds.
- At least 100 instances tested.

| Instance kind | Tested | Matched OPT | Match rate |
|---|---|---|---|
| Sparse | | | |
| Dense | | | |
| Varied | | | |
| Clustered | | | |
| **All** | | | |

- **Required caveat:** agreement is evidence that our implementation works. It is not a proof that the algorithm is optimal.

## 6. Comparing the Heuristics (Part 5, 10 pts)

*Owner: P2 · ~3/4 page · data: `results/summary.csv`, `results/summary_by_kind.csv`*

| Algorithm | % optimal | Average \|H(I)\| / OPT(I) | Worst ratio (instance) |
|---|---|---|---|
| Earliest Finish | | | |
| Earliest Start | | | |
| Shortest Duration | | | |
| Group heuristic | | | |

*[Figure: `results/comparison.png`]*

- **Required:** explain what kinds of instances mislead each heuristic, and why. Don't just list numbers.

## 7. Runtime (Part 6, 10 pts)

*Owner: P3 · ~3/4 page · data: `results/runtime.csv`*

- Setup: sizes, number of repeats, median, machine, Python version.

| n | Earliest Finish | Earliest Start | Shortest Duration | Group heuristic |
|---|---|---|---|---|
| 100 | | | | |
| 1,000 | | | | |
| 10,000 | | | | |
| 100,000 | | | | |

*[Figure: `results/runtime.png`]*

- Compare against the running times in Section 2. Explain where sorting shows up.
- **Don't overclaim:** say the measurements are "consistent with" the analysis, not that they "prove" it.

## 8. Engineering Reflection (Part 7, 5 pts)

*Owner: P4, with everyone adding notes under each question · ~1/2 page · use our actual results, not generic statements*

1. Which incorrect greedy heuristic seemed most convincing before we tested it?
2. What did the counterexample reveal about why the local rule fails?
3. What did the exact solver contribute to the development process?
4. What is the difference between experimentally validating an algorithm and proving it correct?

## 9. Conclusion

*Owner: P4 · 1 paragraph, key findings only*

---

## Group Contribution Statement

| Member | Primary contribution |
|---|---|
| P1 NAME | |
| P2 NAME | |
| P3 NAME | |
| P4 NAME | |

## AI Use Statement

*Required. List each tool, what it was used for, and how we checked its output.*

| Tool | Used for | How we validated it |
|---|---|---|
| | | |
