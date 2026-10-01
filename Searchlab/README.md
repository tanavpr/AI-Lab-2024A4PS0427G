# A* Search for Warehouse Robot Navigation

Laboratory report: *Search and A\** – using an LLM as an engineering assistant.

> **Note on honesty / authorship:** the code, tables and numbers below were
> produced and run for you. The reflection sections (Task 7 and Final
> Reflection) are *drafts*: edit them so they describe what **you** actually
> did, designed and changed, as the lab requires.

## Files

| File | Purpose |
|---|---|
| `search_lab.py` | Grid environment, A\*, BFS, heuristics, command-line interface |
| `maps.py` | Test maps (trivial, no-solution, alternative paths, open room, overshoot) |
| `test_search_lab.py` | 10 unit tests (Task 3 plus extra) |
| `run_experiments.py` | Reproduces every results table in this report |
| `prompts.md` | Prompts used with the LLM (appendix) |

## Reproducing the results

```bash
python search_lab.py                                  # A* with Manhattan on the warehouse
python search_lab.py --algo bfs                       # BFS
python search_lab.py --heuristic euclidean            # other heuristics: zero, double_manhattan
python search_lab.py --map mymap.txt                  # your own ASCII map
python -m unittest -v                                 # run all tests
python run_experiments.py                             # print all result tables
```

Python 3 standard library only.

---

## Task 0 – Formulating the search problem

| Component | Specification |
|---|---|
| State (S) | Robot position `(row, col)` on a free cell |
| Actions (A) | Up, Down, Left, Right |
| Transition (T) | `T((r,c), a) = (r+dr, c+dc)` with Up=(-1,0), Down=(+1,0), Left=(0,-1), Right=(0,+1); defined only if the new cell is valid |
| Initial state (s0) | Position of `S`: (1, 1) |
| Goal (G) | `{(7, 15)}`, the position of `G` |
| Cost (c) | 1 per move, so path cost = number of moves |

**(a) What is needed to specify a state?** Only the robot's position `(row, col)`. The map is fixed, so it is part of the problem, not the state.

**(b) What makes an action invalid?** Moving outside the grid or into a `#` cell.

**(c) Deterministic?** Yes. Each action in a given state has exactly one outcome, and the environment is static and fully observable.

**(d) What is a solution?** A sequence of valid actions (equivalently a sequence of positions) from `S` to `G`. An *optimal* solution has minimum total cost.

## Task 1 – Design of the agent (written before prompting)

1. **State in Python:** a `(row, col)` tuple (hashable, so it can be a dict key / set member).
2. **Warehouse:** a `Grid` class holding a list of lists of characters, plus `start` and `goal` found by scanning for `S` and `G`.
3. **Valid actions:** `Grid.successors(pos)` tries the four offsets and keeps those where `is_valid` (inside grid, not `#`) is true; each is returned with its cost (1).
4. **Goal recognition:** `Grid.is_goal(pos)` compares with the goal position. The test is applied when a state is *removed* from the frontier (required for A\* optimality).
5. **Frontier contents:** a heap of tuples `(f, h, tie_breaker, state)`; `f = g + h`. The tie-breaker counter prevents Python comparing states and makes ties first-in-first-out.
6. **Path reconstruction:** a `parent` dictionary maps each state to the state it was reached from; follow it from the goal back to the start and reverse.

**Reported on termination:** solution found (bool), path, path length, number of states expanded.

## Task 2 – LLM generation

See `prompts.md`. Prompt 1 encodes the design above (state representation, frontier, closed set, reporting) so the LLM translates *my design* into code rather than choosing the design itself. The result is `search_lab.py`.

## Task 3 – Testing

All values from `python run_experiments.py` (A\*, Manhattan):

| Test | Map | Found | Path length | Expanded | Expected | Pass |
|---|---|---|---|---|---|---|
| 1 Original warehouse | supplied | True | 40 | 64 | path exists | ✅ |
| 2 Trivial | `#SG##` | True | 1 | 2 | 1 step | ✅ |
| 3 No solution | supplied | False | – | 9 | report failure, terminate | ✅ |
| 4 Alternative paths | 4-move top row vs 8-move detour | True | 4 | 5 | 4 (shortest) | ✅ |

Test 1 path (40 moves):

```
#################
#S****#*********#
#.###*#*#######*#
#...#*#*******#*#
###.#*#######*#*#
#...#*********#*#
#.###########.#*#
#.............#G#
#################
```

Test 3 expands 9 states because those are all the cells reachable from `S`; once the frontier is empty the search stops, so there is no infinite loop. This is guaranteed by the `closed` set.

I also wrote an **independent path validator** (starts at S, ends at G, only unit steps, no walls, no repeated states) so path correctness is not judged by eye. In total 10 tests pass: `python -m unittest -v`.

## Task 4 – Where each concept appears in `search_lab.py`

| Concept | Where |
|---|---|
| State | `(row, col)` tuples, e.g. `current` in `astar()` (line ~147) |
| Action | `ACTIONS` dictionary at the top of the file |
| Transition | `Grid.successors()` (line 67), adds the action offset to the position |
| Goal test | `Grid.is_goal()` (line 76); called in `astar()` just after the state is popped (line ~152) |
| g(n) | `g` dictionary (line 138); updated with `new_g = g[current] + cost` (line 155) |
| h(n) | `manhattan()` (line 83), called as `heuristic(nxt, goal)` (line 159) |
| f(n) | `new_g + hn`, the first element of the heap tuple pushed at line 161 |
| Frontier | `frontier` list used as a `heapq` min-heap (lines 142, 147, 161) |
| Visited states | `closed` set (line 150) |
| Path reconstruction | `reconstruct()` (line 117) using the `parent` dict |

**(a) Frontier data structure:** a binary min-heap (priority queue) via `heapq`.
**(b) Choosing the next state:** `heappop` returns the entry with the smallest `f`; ties are broken by smaller `h`, then first-in-first-out.
**(c) Heuristic calculated:** in `manhattan()`, called when a state is first generated (and for the start state).
**(d) Explicit f = g + h?** Yes: `new_g + hn` is computed when pushing a state. `f` is not stored per state in a dictionary; it lives in the heap entry.
**(e) Preventing repeated exploration:** the `closed` set: a state popped a second time (a stale duplicate heap entry) is skipped. Also a state is only re-pushed if a strictly cheaper `g` is found.

## Task 5 – BFS vs A\* (original warehouse, unchanged)

| Measure | BFS | A\* (Manhattan) |
|---|---|---|
| Solution found | True | True |
| Path length | 40 | 40 |
| States expanded | 64 | 64 |

**(a)** Yes, both found a solution. **(b)** Yes, both found a 40-move optimal path. **(c)** *Neither*: both expanded 64 states, which is every free cell in the warehouse.

**(d) Why might A\* expand fewer states, and why didn't it here?** In general A\* is guided towards the goal, so it can ignore regions where `g + h` is large. Here it cannot, because the map is almost a single winding corridor. The straight-line (Manhattan) distance from S to G is only 20, but the real path is 40 because walls force the robot to travel *away* from the goal before it gets closer. So `f = g + h` stays below 40 for every cell, and A\* must expand all of them before reaching the goal. The heuristic is admissible but not informative on this map.

To show A\* really does help when the geometry cooperates, I ran an open room (extra experiment): BFS expands 15 states, A\* (Manhattan) expands 7, for the same 6-move path.

## Task 6 – Heuristic investigation

**Why Manhattan?** With only 4-directional unit-cost moves, the cheapest conceivable route needs at least `|Δrow| + |Δcol|` moves, so Manhattan never overestimates (admissible). It is also consistent, and it is exact when there are no walls.

**Original warehouse:**

| Heuristic | Found | Path length | Expanded |
|---|---|---|---|
| Manhattan | True | 40 | 64 |
| h = 0 | True | 40 | 64 |
| Euclidean | True | 40 | 64 |
| 2 × Manhattan | True | 40 | 64 |

All identical, because (as explained in Task 5) every cell has to be expanded in this corridor-like map, so no heuristic can reduce the work. This is itself a result: *a heuristic can only save work when it can rule states out.*

**Open room (6-move path):**

| Heuristic | Found | Path length | Expanded |
|---|---|---|---|
| BFS | True | 6 | 15 |
| h = 0 | True | 6 | 15 |
| Manhattan | True | 6 | 7 |
| Euclidean | True | 6 | 10 |
| 2 × Manhattan | True | 6 | 7 |

* **h = 0** gives f = g, so A\* degenerates into uniform-cost search, which here behaves like BFS: still optimal, but no guidance (15 expansions).
* **Euclidean** is admissible but *weaker* than Manhattan (it always underestimates on a grid), so it gives less guidance (10 expansions vs 7).
* **2 × Manhattan** is *inadmissible* (it can exceed the true cost) and makes the search more greedy. In the open room it still found the optimum; on the `overshoot` map it did not:

| Heuristic (`overshoot` map) | Found | Path length | Expanded |
|---|---|---|---|
| BFS (optimal) | True | 10 | 25 |
| Manhattan | True | 10 | 18 |
| Euclidean | True | 10 | 18 |
| h = 0 | True | 10 | 25 |
| 2 × Manhattan | True | **12** | 15 |

**Conclusion:** a heuristic that is too *pessimistic about distance* (h too large, inadmissible) makes A\* faster but can return a **non-shortest path**. A heuristic that is too *weak* (h = 0) stays optimal but loses the benefit of being "informed". Admissibility (h ≤ h\*) is what guarantees optimality; how *close* h is to h\* decides how much work is saved.

## Task 7 – Evaluating the LLM-generated agent (draft: adapt to your own experience)

1. **Correct immediately:** the grid parsing, the transition function, the heap-based frontier, path reconstruction and the BFS/A\* agreement on the supplied map.
2. **Bugs / design problems:** no functional bugs appeared. Design issues that needed a decision: (i) *when to apply the goal test* (on pop, not on generation, for A\* optimality); (ii) *what counts as "expanded"* (defined once and used for both algorithms so the comparison is fair); (iii) *tie-breaking*, which changes expansion counts but not path length; (iv) duplicate heap entries, handled with a closed set.
3. **How discovered:** by reading the code against the Task 4 checklist and by the experiments. The biggest surprise (A\* = BFS on the warehouse) only appeared when running Task 5.
4. **Unfamiliar terms:** e.g. `heapq`, tie-breaker counters, "stale entries", consistent vs admissible heuristics.
5. **Modified?** The heuristic was turned into a parameter for Task 6, a BFS function was added using the same `Result` type, and extra maps were added. *(Edit to match your own changes.)*
6. **Most useful tests:** the no-solution test (checks termination), the alternative-paths test (checks optimality), and the independent path validator (checks correctness without trusting the program's own output).
7. **Could the program be trusted without testing?** No. It looks plausible, but only tests establish properties such as optimality and termination.
8. **What I understood about A\* that I didn't before:** A\* is only as good as its heuristic. On this warehouse it was no better than BFS, and an inadmissible heuristic can silently return a worse path.

## Final Reflection (draft)

**1. Why formulate the problem first?** The formulation (states, actions, transitions, goal, cost) is the specification of what "correct" means. Without it you cannot tell the LLM what to build, cannot design tests, and cannot decide whether a plausible-looking output is actually right. The algorithm is just one way of solving a well-defined problem.

**2. In what sense is A\* informed?** It uses problem-specific knowledge, the heuristic h(n), to estimate how far each state is from the goal and expands the state with the lowest g + h. Blind methods such as BFS only use the structure of the graph (e.g. depth) and treat every direction as equally promising.

**3. Why does the heuristic matter?** It determines both correctness and efficiency. If it is admissible, A\* is optimal; if it overestimates, A\* may return a worse path (shown by the 2× Manhattan result). The closer h is to the true cost, the fewer states are expanded; h = 0 gives no guidance, and on the warehouse map the straight-line distance (20) was far below the true cost (40), so no state could be pruned.

**4. What did the LLM contribute?** Fast translation of my design into working, documented code, plus a BFS variant, extra tests and explanations. It did not decide what the problem was, define the tests' expected outcomes, or confirm that the results meant what they appeared to.

**5. What could go wrong without testing?** The program could loop forever on unsolvable maps, return paths through walls or non-shortest paths, miscount expansions, or fail on edge cases (goal next to start, missing S). Output that looks right can hide such errors: *working output ≠ validated algorithm*.
