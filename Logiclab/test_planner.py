"""Tests for the logical planner.  Run:  python -m unittest -v"""
import unittest
from planner import (INITIAL, GOAL, make_action, warehouse_actions, bfs_plan,
                     applicable, apply_action, validate_plan, move, pickup, drop)


def names(plan):
    return [a.name for a in plan]


class Task0Applicability(unittest.TestCase):
    def test_pickup_A_applicable_initially(self):
        self.assertTrue(applicable(INITIAL, pickup("A")))

    def test_drop_C_not_applicable_initially(self):
        self.assertFalse(applicable(INITIAL, drop("C")))

    def test_pickup_B_not_applicable_initially(self):
        # package is at A, robot at A: PickUp(Package,B) is not applicable
        self.assertFalse(applicable(INITIAL, pickup("B")))

    def test_apply_inapplicable_action_raises(self):
        with self.assertRaises(ValueError):
            apply_action(INITIAL, drop("C"))


class TaskATests(unittest.TestCase):
    def test_A_solvable(self):
        res = bfs_plan(INITIAL, warehouse_actions(), GOAL)
        self.assertTrue(res.found)
        self.assertEqual(names(res.plan),
                         ["PickUp(Package,A)", "Move(A,B)", "Move(B,C)", "Drop(Package,C)"])
        ok, _ = validate_plan(INITIAL, res.plan, GOAL)
        self.assertTrue(ok)
        self.assertTrue(GOAL <= res.states[-1])

    def test_A_plan_is_shortest(self):
        res = bfs_plan(INITIAL, warehouse_actions(), GOAL)
        self.assertEqual(len(res.plan), 4)      # no 3-action plan exists


class TaskBTests(unittest.TestCase):
    def test_B_no_pickup_means_no_plan(self):
        acts = [a for a in warehouse_actions() if not a.name.startswith("PickUp")]
        res = bfs_plan(INITIAL, acts, GOAL)
        self.assertFalse(res.found)
        self.assertIsNone(res.plan)

    def test_B_no_drop_means_no_plan(self):
        acts = [a for a in warehouse_actions() if not a.name.startswith("Drop")]
        self.assertFalse(bfs_plan(INITIAL, acts, GOAL).found)


class TaskCTests(unittest.TestCase):
    def test_C_robot_reaching_C_is_not_package_reaching_C(self):
        only_moves = [a for a in warehouse_actions() if a.name.startswith("Move")]
        # Robot CAN reach C ...
        self.assertTrue(bfs_plan(INITIAL, only_moves, {"At(Robot,C)"}).found)
        # ... but the package is still at A, so the package goal is unreachable.
        self.assertFalse(bfs_plan(INITIAL, only_moves, GOAL).found)

    def test_C_extra_irrelevant_move_does_not_change_plan_length(self):
        extra = warehouse_actions() + [move("A", "B")]   # duplicate irrelevant move
        self.assertEqual(len(bfs_plan(INITIAL, extra, GOAL).plan), 4)


class ValidatorTests(unittest.TestCase):
    def test_handout_example_sequence_is_invalid(self):
        bad = [move("A", "B"), pickup("B"), move("B", "C"), drop("C")]
        ok, log = validate_plan(INITIAL, bad, GOAL)
        self.assertFalse(ok)
        self.assertIn("NOT applicable", log[-1])

    def test_skipping_pickup_is_invalid(self):
        bad = [move("A", "B"), move("B", "C"), drop("C")]
        self.assertFalse(validate_plan(INITIAL, bad, GOAL)[0])

    def test_wrong_goal_not_satisfied(self):
        plan = [move("A", "B"), move("B", "C")]
        ok, log = validate_plan(INITIAL, plan, GOAL)
        self.assertFalse(ok)
        self.assertIn("goal NOT satisfied", log[-1])


class NegativePreconditionTests(unittest.TestCase):
    def test_negative_precondition_blocks_action(self):
        act = make_action("Lock", pos_pre=["At(Robot,A)"], neg_pre=["Locked"],
                          pos_eff=["Locked"])
        self.assertTrue(applicable(frozenset({"At(Robot,A)"}), act))
        self.assertFalse(applicable(frozenset({"At(Robot,A)", "Locked"}), act))


if __name__ == "__main__":
    unittest.main()
