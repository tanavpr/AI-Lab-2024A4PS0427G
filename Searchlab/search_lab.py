"""
Warehouse Robot Navigation: A* and BFS search
=============================================

Search problem  P = (S, A, T, s0, G, c)
  S  : all free grid cells, as (row, col) tuples
  A  : Up, Down, Left, Right
  T  : (row, col) + action offset (valid only if the target cell is not '#')
  s0 : position of 'S'
  G  : {position of 'G'}
  c  : 1 for every move

"States expanded" is counted as the number of states removed from the frontier
and processed (the goal state, when removed, is counted too). The same
definition is used for BFS and every A* variant so results are comparable.
"""

import argparse
import heapq
import math
from collections import deque

WAREHOUSE = [
    "#################",
    "#S....#.........#",
    "#.###.#.#######.#",
    "#...#.#.......#.#",
    "###.#.#######.#.#",
    "#...#.........#.#",
    "#.###########.#.#",
    "#.............#G#",
    "#################",
]

# Action name -> (row change, column change)
ACTIONS = {"Up": (-1, 0), "Down": (1, 0), "Left": (0, -1), "Right": (0, 1)}


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------
class Grid:
    """The warehouse. Parses an ASCII map and provides the transition model."""

    def __init__(self, layout):
        self.cells = [list(row) for row in layout]
        self.rows = len(self.cells)
        self.cols = len(self.cells[0])
        if any(len(r) != self.cols for r in self.cells):
            raise ValueError("All map rows must have the same length.")
        self.start = self._find("S")
        self.goal = self._find("G")

    def _find(self, symbol):
        found = [(r, c) for r, row in enumerate(self.cells)
                 for c, ch in enumerate(row) if ch == symbol]
        if len(found) != 1:
            raise ValueError(f"Map must contain exactly one '{symbol}'.")
        return found[0]

    def is_valid(self, pos):
        """An action is invalid if it leaves the grid or enters a '#' cell."""
        r, c = pos
        return (0 <= r < self.rows and 0 <= c < self.cols
                and self.cells[r][c] != "#")

    def successors(self, pos):
        """Transition function: list of (action, next_state, step_cost)."""
        out = []
        for name, (dr, dc) in ACTIONS.items():
            nxt = (pos[0] + dr, pos[1] + dc)
            if self.is_valid(nxt):
                out.append((name, nxt, 1))
        return out

    def is_goal(self, pos):
        return pos == self.goal


# --------------------------------------------------------------------------
# Heuristics  h(n): estimated cost from n to the goal
# --------------------------------------------------------------------------
def manhattan(pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

def euclidean(pos, goal):
    return math.hypot(pos[0] - goal[0], pos[1] - goal[1])

def zero(pos, goal):
    return 0

def double_manhattan(pos, goal):
    return 2 * manhattan(pos, goal)

HEURISTICS = {
    "manhattan": manhattan,
    "euclidean": euclidean,
    "zero": zero,
    "double_manhattan": double_manhattan,
}


# --------------------------------------------------------------------------
# Result container
# --------------------------------------------------------------------------
class Result:
    def __init__(self, found, path, expanded):
        self.found = found          # bool
        self.path = path            # list of positions from s0 to goal, or None
        self.expanded = expanded    # number of states expanded

    @property
    def length(self):
        return len(self.path) - 1 if self.path else None


def reconstruct(parent, end):
    """Follow parent pointers back from the goal to the start."""
    path = [end]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


# --------------------------------------------------------------------------
# A* search
# --------------------------------------------------------------------------
def astar(grid, heuristic=manhattan):
    """
    Frontier : binary heap (priority queue) of (f, h, tie, state)
    g        : dict, best known cost from start to each state
    parent   : dict, for path reconstruction
    closed   : set of states already expanded (avoids re-expansion)
    f(n) = g(n) + h(n); the state with the smallest f is expanded next.
    """
    start, goal = grid.start, grid.goal
    g = {start: 0}
    parent = {start: None}
    h0 = heuristic(start, goal)
    tie = 0                                   # FIFO tie-breaker
    frontier = [(g[start] + h0, h0, tie, start)]
    closed = set()
    expanded = 0

    while frontier:
        f, h, _, current = heapq.heappop(frontier)
        if current in closed:                 # stale duplicate entry
            continue
        closed.add(current)
        expanded += 1
        if grid.is_goal(current):
            return Result(True, reconstruct(parent, current), expanded)
        for _, nxt, cost in grid.successors(current):
            new_g = g[current] + cost
            if nxt not in closed and (nxt not in g or new_g < g[nxt]):
                g[nxt] = new_g
                parent[nxt] = current
                hn = heuristic(nxt, goal)
                tie += 1
                heapq.heappush(frontier, (new_g + hn, hn, tie, nxt))
    return Result(False, None, expanded)


# --------------------------------------------------------------------------
# Breadth-first search (blind)
# --------------------------------------------------------------------------
def bfs(grid):
    """Frontier is a FIFO queue; no heuristic. Goal test on removal, as in A*."""
    start = grid.start
    parent = {start: None}
    frontier = deque([start])
    expanded = 0
    while frontier:
        current = frontier.popleft()
        expanded += 1
        if grid.is_goal(current):
            return Result(True, reconstruct(parent, current), expanded)
        for _, nxt, _ in grid.successors(current):
            if nxt not in parent:             # also serves as visited set
                parent[nxt] = current
                frontier.append(nxt)
    return Result(False, None, expanded)


# --------------------------------------------------------------------------
# Presentation
# --------------------------------------------------------------------------
def render(grid, path):
    canvas = [row[:] for row in grid.cells]
    for r, c in (path or [])[1:-1]:
        canvas[r][c] = "*"
    return "\n".join("".join(row) for row in canvas)


def report(grid, result, label):
    print(f"=== {label} ===")
    print(f"Solution found : {result.found}")
    if result.found:
        print(f"Path length    : {result.length}")
        print(f"States expanded: {result.expanded}")
        print(f"Path           : {' -> '.join(map(str, result.path))}")
        print(render(grid, result.path))
    else:
        print(f"States expanded: {result.expanded}")
        print("No path exists from S to G.")


def main():
    p = argparse.ArgumentParser(description="Warehouse search agent")
    p.add_argument("--algo", choices=["astar", "bfs"], default="astar")
    p.add_argument("--heuristic", choices=sorted(HEURISTICS), default="manhattan")
    p.add_argument("--map", help="path to a text file containing an ASCII map")
    args = p.parse_args()

    layout = WAREHOUSE
    if args.map:
        with open(args.map) as fh:
            layout = [line.rstrip("\n") for line in fh if line.strip()]
    grid = Grid(layout)

    if args.algo == "bfs":
        report(grid, bfs(grid), "BFS")
    else:
        report(grid, astar(grid, HEURISTICS[args.heuristic]),
               f"A* ({args.heuristic})")


if __name__ == "__main__":
    main()
