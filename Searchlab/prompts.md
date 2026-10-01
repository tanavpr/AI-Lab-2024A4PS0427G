# Prompts used with the LLM (Appendix)

> Replace or extend these with the exact prompts from your own LLM session if
> you ran one. The lab asks for the important prompts to be included.

## Prompt 1 – Generate A* (based on the Task 1 design)

I am implementing a simple goal-based search agent in Python.
The environment is a grid represented by an ASCII map. The agent starts at S and
must reach G. `#` are obstacles and `.` are free cells. The agent can move up,
down, left or right, and every movement has cost 1.

Implement A* search using Manhattan distance as the heuristic,
h(n) = |x - xG| + |y - yG|.

Design constraints (from my own design):
- a state is a (row, col) tuple;
- the warehouse is a Grid class that parses the ASCII map and provides
  `is_valid`, `successors` (returns action, next state, cost) and `is_goal`;
- the frontier is a priority queue (heapq) of (f, h, tie_breaker, state);
- keep dictionaries `g` (best cost so far) and `parent` (for path reconstruction),
  and a `closed` set so no state is expanded twice;
- report: whether a solution was found, the path, the path length, and the
  number of states expanded (count a state when it is removed from the frontier).

Keep the implementation simple and explain the main components of the code.

## Prompt 2 – BFS version for comparison (Task 5)

Using the same Grid class and the same definition of "states expanded", add a
breadth-first search function that returns the same Result object, so I can
compare it with A* on the same map.

## Prompt 3 – Heuristic variants (Task 6)

Make the heuristic a parameter of the A* function. Add: h = 0, Euclidean
distance, and 2 x Manhattan distance. Do not change anything else.

## Prompt 4 – Why Manhattan? (Task 6, explanation only)

Explain why Manhattan distance is an appropriate heuristic for a robot that can
only move horizontally and vertically on a grid.

## Prompt 5 – Test generation

Write unittest tests for this program: original map, trivial one-step map,
unreachable goal, two-route map (check the shortest is returned), an independent
path validator, and a check that BFS and A* give equal path lengths.
