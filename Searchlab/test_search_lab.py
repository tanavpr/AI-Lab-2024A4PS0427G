"""Tests for the A*/BFS warehouse search.  Run:  python -m unittest -v"""
import unittest
from search_lab import (Grid, astar, bfs, ACTIONS, manhattan, euclidean,
                        zero, double_manhattan)
from maps import ALL


def is_valid_path(grid, path):
    """Independent checker: starts at S, ends at G, unit steps, no walls."""
    if path[0] != grid.start or path[-1] != grid.goal:
        return False
    for a, b in zip(path, path[1:]):
        if (b[0] - a[0], b[1] - a[1]) not in ACTIONS.values():
            return False
        if not grid.is_valid(b):
            return False
    return len(set(path)) == len(path)          # no repeated states


class Task3Tests(unittest.TestCase):
    def test1_original_warehouse(self):
        g = Grid(ALL["original"])
        res = astar(g)
        self.assertTrue(res.found)
        self.assertTrue(is_valid_path(g, res.path))
        self.assertEqual(res.length, 40)

    def test2_trivial_one_step(self):
        g = Grid(ALL["trivial"])
        res = astar(g)
        self.assertTrue(res.found)
        self.assertEqual(res.length, 1)
        self.assertEqual(res.path, [(1, 1), (1, 2)])

    def test3_no_solution_terminates(self):
        g = Grid(ALL["no_solution"])
        for res in (astar(g), bfs(g)):
            self.assertFalse(res.found)
            self.assertIsNone(res.path)

    def test4_alternative_paths_returns_shortest(self):
        g = Grid(ALL["alternative"])
        res = astar(g)
        self.assertEqual(res.length, 4)          # the 8-move detour is rejected
        self.assertEqual(res.length, bfs(g).length)


class AgreementTests(unittest.TestCase):
    def test_admissible_heuristics_match_bfs_on_every_map(self):
        for name, layout in ALL.items():
            g = Grid(layout)
            b = bfs(g)
            for h in (manhattan, euclidean, zero):
                a = astar(g, h)
                self.assertEqual(a.found, b.found, name)
                if b.found:
                    self.assertEqual(a.length, b.length, f"{name}/{h.__name__}")

    def test_astar_expands_no_more_than_bfs_in_open_room(self):
        g = Grid(ALL["open_room"])
        self.assertLess(astar(g).expanded, bfs(g).expanded)

    def test_zero_heuristic_expands_same_as_bfs_in_open_room(self):
        g = Grid(ALL["open_room"])
        self.assertEqual(astar(g, zero).expanded, bfs(g).expanded)

    def test_overaggressive_heuristic_can_be_suboptimal(self):
        g = Grid(ALL["overshoot"])
        self.assertGreater(astar(g, double_manhattan).length, bfs(g).length)


class InputTests(unittest.TestCase):
    def test_missing_start(self):
        with self.assertRaises(ValueError):
            Grid(["####", "#.G#", "####"])

    def test_ragged_map(self):
        with self.assertRaises(ValueError):
            Grid(["####", "#SG#", "###"])


if __name__ == "__main__":
    unittest.main()
