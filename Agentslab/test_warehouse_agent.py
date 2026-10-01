"""Unit tests for the warehouse goal-based agent. Run: python -m unittest -v"""
import unittest
from warehouse_agent import Warehouse, GoalBasedAgent, WAREHOUSE_MAP, ACTIONS

BLOCKED_MAP = [
    "#######",
    "#S.#.G#",
    "#######",
]


def validate(env, steps):
    """Check a plan: every step is a legal one-square move, avoids '#', ends at G."""
    pos = env.start
    for action, nxt in steps:
        dr, dc = ACTIONS[action]
        assert (pos[0] + dr, pos[1] + dc) == nxt, "move does not match action"
        assert env.is_free(nxt), "path crosses an obstacle"
        pos = nxt
    return pos == env.goal


class TestAgent(unittest.TestCase):
    def test_bfs_finds_valid_path(self):
        env = Warehouse(WAREHOUSE_MAP)
        steps = GoalBasedAgent(env, "bfs").plan()
        self.assertIsNotNone(steps)
        self.assertTrue(validate(env, steps))

    def test_astar_finds_valid_path(self):
        env = Warehouse(WAREHOUSE_MAP)
        steps = GoalBasedAgent(env, "astar").plan()
        self.assertTrue(validate(env, steps))

    def test_both_algorithms_give_same_optimal_length(self):
        env = Warehouse(WAREHOUSE_MAP)
        self.assertEqual(len(GoalBasedAgent(env, "bfs").plan()),
                         len(GoalBasedAgent(env, "astar").plan()))

    def test_no_path_returns_none(self):
        env = Warehouse(BLOCKED_MAP)
        self.assertIsNone(GoalBasedAgent(env, "bfs").plan())
        self.assertIsNone(GoalBasedAgent(env, "astar").plan())

    def test_missing_start_raises(self):
        with self.assertRaises(ValueError):
            Warehouse(["####", "#.G#", "####"])


if __name__ == "__main__":
    unittest.main()
