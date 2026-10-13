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

*Owner: P3 · data: `results/runtime.csv`, `results/runtime_summary.csv`, `results/runtime.png` · regenerate with `python runtime.py`*

**Setup.** We timed only the four greedy algorithms; the exact solver is hopeless at
these sizes (Section 3). Each algorithm ran 5 times on the same instance at each of
n = 100, 1,000, 10,000, and 100,000, and we report the median of those 5 runs. The
instances come from `generate("varied", n, seed=4050)`, so every measurement can be
rebuilt from the seed. Measurements were taken with `time.perf_counter()` on an Apple
Silicon (arm64) machine running macOS 26.6.2 and Python 3.13.7. Timings on a laptop
are noisy — we saw roughly ±10–30% run-to-run variation at the smallest sizes — which
is why we report a median rather than a single run or a mean.

**Median running time (seconds).**

| n | Earliest Finish | Earliest Start | Shortest Duration | Group heuristic |
|---|---|---|---|---|
| 100 | 0.000011 | 0.000010 | 0.000023 | 0.000045 |
| 1,000 | 0.000153 | 0.000148 | 0.000378 | 0.000693 |
| 10,000 | 0.002358 | 0.002302 | 0.009566 | 0.013438 |
| 100,000 | 0.035200 | 0.033970 | 0.585857 | 0.526978 |

*[Figure: `results/runtime.png` — left: median time vs n on log-log axes with an
n log n reference line; right: the share of each running time spent in the sort.]*

**Growth from one size to the next.** Each step multiplies n by 10. Over such a step
a Θ(n log n) algorithm should get about 15×, 13.3×, and 12.5× slower (the ratio
(n₂ log n₂)/(n₁ log n₁) shrinks slightly as n grows), while a Θ(n²) algorithm should
get 100× slower. Those predictions are far enough apart to tell apart:

| Algorithm | 100 → 1,000 | 1,000 → 10,000 | 10,000 → 100,000 |
|---|---|---|---|
| Earliest Finish | 14.2× | 15.4× | 14.9× |
| Earliest Start | 15.0× | 15.6× | 14.8× |
| Shortest Duration | 16.3× | 25.3× | 61.2× |
| Group heuristic | 15.5× | 19.4× | 39.2× |
| *Θ(n log n) predicts* | *15.0×* | *13.3×* | *12.5×* |
| *Θ(n²) predicts* | *100×* | *100×* | *100×* |

Earliest Finish and Earliest Start stay flat at roughly 15× per decade, close to the
n log n prediction and nowhere near 100×. On the log-log plot they are straight lines
parallel to the n log n reference. Shortest Duration and the group heuristic start in
the same range and then bend upward — 61.2× and 39.2× on the last step — which is the
shape their Section 2 analysis predicts: an O(n log n) sort plus a selection loop whose
list insert is O(n) in the worst case.

**Where the sort appears.** All four algorithms sort once, up front, and that sort is
the Θ(n log n) term in every one of them. Timing the sort by itself (`SORT_STEPS` in
`runtime.py`) shows how much of each running time it accounts for:

| Algorithm | n = 100 | n = 1,000 | n = 10,000 | n = 100,000 |
|---|---|---|---|---|
| Earliest Finish | 69% | 81% | 86% | 84% |
| Earliest Start | 73% | 84% | 83% | 85% |
| Shortest Duration | 35% | 32% | 17% | 3% |
| Group heuristic | 72% | 68% | 55% | 21% |

For Earliest Finish and Earliest Start the sort is essentially the whole algorithm: what
follows is one O(n) left-to-right scan that compares each job against only the last
selected job. Their share climbs from about 70% at n = 100 and then settles in the
mid-80s — the climb is not sorting becoming relatively more expensive, it is the fixed
interpreter overhead that dominates a 10-microsecond measurement washing out once the
instance is large. (The sort and the total are timed in separate passes, so each share
carries a few points of measurement noise; the right reading of the mid-80s is "nearly
all of it", not an exact 84.)

For the other two the share *falls*, because the part that is not the sort grows faster
than the sort does. By n = 100,000 Shortest Duration spends only 3% of its time sorting;
the other 97% is the selection loop, and the next paragraph shows it is the inserts.

**Why the other two bend upward.** Shortest Duration and the group heuristic do not pick
jobs in time order, so they keep the selected set in a list sorted by start time and
`list.insert` into it; one insert shifts every element after the insertion point. At
n = 100,000, `runtime.py` counts the elements those shifts move:

| Algorithm | Instance kind | Median time | \|Selected\| | Elements shifted | Inserts that were appends |
|---|---|---|---|---|---|
| Shortest Duration | sparse | 1.164 s | 88,994 | 1,983,181,506 | 0.0% |
| Shortest Duration | varied | 0.591 s | 61,352 | 943,273,230 | 0.0% |
| Shortest Duration | clustered | 0.321 s | 41,732 | 435,840,760 | 0.0% |
| Shortest Duration | dense | 0.214 s | 33,582 | 283,309,679 | 0.0% |
| Group heuristic | sparse | 0.368 s | 89,061 | 434,164,711 | 87.6% |
| Group heuristic | varied | 0.533 s | 61,433 | 700,562,375 | 23.2% |
| Group heuristic | clustered | 0.354 s | 42,152 | 356,824,455 | 18.3% |
| Group heuristic | dense | 0.276 s | 34,366 | 242,590,571 | 5.0% |

n is identical (100,000) on every row here, so n alone cannot explain a 5.4× spread in
running time. The shift count can: across the four kinds the elements shifted span 7×,
and time divided by elements shifted stays between 0.59 and 0.76 ns for Shortest
Duration. A roughly constant cost per element moved, holding across instances that
differ this much, is what we would expect if the shifting really is the dominant cost.
The small residual goes the right way too — dense has the highest apparent cost per
element (0.76 ns) because its fixed Θ(n log n) sort is a larger fraction of a smaller
total.

This also explains a result that surprised us: on sparse instances the group heuristic
beats Shortest Duration (0.368 s vs 1.164 s) even though it does strictly more work,
counting every job's conflicts first. The group heuristic orders jobs by
(conflicts, finish, id); on sparse instances most jobs have the same low conflict count,
so the finish-time tiebreak hands the selection loop a batch that is already in time
order and 87.6% of its inserts land at the end of the list, where nothing has to move.
Shortest Duration's duration order has nothing to do with position on the timeline, so
almost none of its inserts are appends and the average one shifts about 22,000 elements.
That is a property of our data structure, not of the greedy rule: keeping the selected
set in a structure with cheap ordered insertion would remove the effect from both.

**What these measurements do not show.** Four sizes, five repeats, one machine, one
generator kind for the main sweep. The results are *consistent with* the running times in
Section 2 and they do not prove any of them. Four points cannot separate Θ(n log n) from,
say, Θ(n log² n) or Θ(n^1.05), and the fact that Shortest Duration grew 61.2× rather than
100× on the last step does not mean its worst case is better than O(n²) — it means these
instances did not provoke the worst case. A bound is established by the argument in
Section 2; the timings only tell us we have not contradicted it.

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
