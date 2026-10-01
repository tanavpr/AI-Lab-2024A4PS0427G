"""
Goal-Based Agent for the Warehouse Navigation Problem
=====================================================

The agent:
  * perceives its environment (a 2-D grid map),
  * keeps an internal state (its current position),
  * holds an explicit goal (reach 'G'),
  * chooses a sequence of actions (Up/Down/Left/Right) that achieves the goal.

Search algorithm: Breadth-First Search (BFS)
--------------------------------------------
Every move costs exactly 1, so BFS is *complete* (finds a path if one exists)
and *optimal* (finds a shortest path). The grid is small, so its memory cost
is irrelevant here. An A* alternative is included for comparison.

Usage:
    python warehouse_agent.py              # BFS (default)
    python warehouse_agent.py --algo astar # A* with Manhattan heuristic
"""

import argparse
import heapq
from collections import deque

WAREHOUSE_MAP = [
    "#####################",
    "#S....#............G#",
    "#.##....##########..#",
    "#....##.............#",
    "#.######.###.#.###..#",
    "#........#..........#",
    "#####################",
]

# Action name -> (row change, column change)
ACTIONS = {
    "Up": (-1, 0),
    "Down": (1, 0),
    "Left": (0, -1),
    "Right": (0, 1),
}


class Warehouse:
    """The environment: a 2-D grid of characters."""

    def __init__(self, layout):
        self.grid = [list(row) for row in layout]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        if any(len(r) != self.cols for r in self.grid):
            raise ValueError("All map rows must have the same length.")
        self.start = self._find("S")
        self.goal = self._find("G")

    def _find(self, symbol):
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell == symbol:
                    return (r, c)
        raise ValueError(f"Map does not contain '{symbol}'.")

    def is_free(self, pos):
        r, c = pos
        return 0 <= r < self.rows and 0 <= c < self.cols and self.grid[r][c] != "#"

    def successors(self, pos):
        """Return [(action, next_position)] for every legal move from pos."""
        result = []
        for name, (dr, dc) in ACTIONS.items():
            nxt = (pos[0] + dr, pos[1] + dc)
            if self.is_free(nxt):
                result.append((name, nxt))
        return result


class GoalBasedAgent:
    """Decision-making component: plans a path from its state to the goal."""

    def __init__(self, environment, algorithm="bfs"):
        self.env = environment
        self.state = environment.start      # current state
        self.goal = environment.goal        # explicit goal
        self.algorithm = algorithm
        self.nodes_expanded = 0

    def goal_test(self, state):
        return state == self.goal

    def plan(self):
        """Return a list of (action, position) steps, or None if no path."""
        if self.algorithm == "astar":
            return self._astar()
        return self._bfs()

    # ---- Breadth-First Search -------------------------------------------
    def _bfs(self):
        frontier = deque([self.state])
        came_from = {self.state: None}   # state -> (previous state, action)
        while frontier:
            current = frontier.popleft()
            self.nodes_expanded += 1
            if self.goal_test(current):
                return self._reconstruct(came_from, current)
            for action, nxt in self.env.successors(current):
                if nxt not in came_from:     # visited set prevents loops
                    came_from[nxt] = (current, action)
                    frontier.append(nxt)
        return None

    # ---- A* Search ------------------------------------------------------
    def _heuristic(self, pos):
        return abs(pos[0] - self.goal[0]) + abs(pos[1] - self.goal[1])

    def _astar(self):
        counter = 0  # tie-breaker so the heap never compares tuples of positions
        frontier = [(self._heuristic(self.state), counter, self.state)]
        came_from = {self.state: None}
        cost = {self.state: 0}
        while frontier:
            _, _, current = heapq.heappop(frontier)
            self.nodes_expanded += 1
            if self.goal_test(current):
                return self._reconstruct(came_from, current)
            for action, nxt in self.env.successors(current):
                new_cost = cost[current] + 1
                if nxt not in cost or new_cost < cost[nxt]:
                    cost[nxt] = new_cost
                    came_from[nxt] = (current, action)
                    counter += 1
                    heapq.heappush(
                        frontier, (new_cost + self._heuristic(nxt), counter, nxt)
                    )
        return None

    @staticmethod
    def _reconstruct(came_from, end):
        steps = []
        node = end
        while came_from[node] is not None:
            prev, action = came_from[node]
            steps.append((action, node))
            node = prev
        steps.reverse()
        return steps

    def act(self, steps):
        """Execute the plan, updating the agent's internal state."""
        for _, pos in steps:
            self.state = pos


def render(env, steps):
    """Return the map as text with the path drawn using '*'."""
    canvas = [row[:] for row in env.grid]
    for _, (r, c) in steps[:-1]:          # leave 'G' visible
        canvas[r][c] = "*"
    return "\n".join("".join(row) for row in canvas)


def main():
    parser = argparse.ArgumentParser(description="Warehouse goal-based agent")
    parser.add_argument("--algo", choices=["bfs", "astar"], default="bfs")
    args = parser.parse_args()

    env = Warehouse(WAREHOUSE_MAP)
    agent = GoalBasedAgent(env, algorithm=args.algo)

    print(f"Algorithm : {args.algo.upper()}")
    print(f"Start (row, col): {env.start}   Goal (row, col): {env.goal}\n")

    steps = agent.plan()
    if steps is None:
        print("No path exists from S to G.")
        return

    agent.act(steps)
    print("Map with path (* = path):")
    print(render(env, steps))
    print()
    print(f"Path length     : {len(steps)} moves")
    print(f"Nodes expanded  : {agent.nodes_expanded}")
    print("Action sequence : " + ", ".join(a for a, _ in steps))
    print("Coordinates     : " + " -> ".join(
        [str(env.start)] + [str(p) for _, p in steps]))
    print(f"Final agent state is the goal: {agent.goal_test(agent.state)}")


if __name__ == "__main__":
    main()
