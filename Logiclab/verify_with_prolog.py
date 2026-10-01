"""
Generate -> Independent verification
Python generates a plan; SWI-Prolog (verify_plan.pl) checks it independently.

    python verify_with_prolog.py            # plan produced by the Python planner
    python verify_with_prolog.py --bad      # the plan suggested in the lab handout's Task 1
"""
import argparse
import re
import shutil
import subprocess

from planner import INITIAL, GOAL, warehouse_actions, bfs_plan


def to_prolog(action_name):
    """'Move(A,B)' -> 'move(a,b)',  'PickUp(Package,A)' -> 'pickup(package,a)'."""
    return re.sub(r"[A-Za-z]+", lambda m: m.group(0).lower(), action_name)


def prolog_verify(action_names):
    if shutil.which("swipl") is None:
        raise SystemExit("SWI-Prolog (swipl) not found. Install it to run this check.")
    plan = "[" + ",".join(to_prolog(a) for a in action_names) + "]"
    goal = f"verify({plan}),halt"
    out = subprocess.run(["swipl", "-q", "-g", goal, "verify_plan.pl"],
                         capture_output=True, text=True)
    return out.stdout + out.stderr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bad", action="store_true",
                    help="verify the (incorrect) example sequence from the handout")
    args = ap.parse_args()

    if args.bad:
        names = ["Move(A,B)", "PickUp(Package,B)", "Move(B,C)", "Drop(Package,C)"]
        print("Proposed plan (from handout example):", names)
    else:
        res = bfs_plan(INITIAL, warehouse_actions(), GOAL)
        names = [a.name for a in res.plan]
        print("Python planner generated:", names)
    print("\n--- Prolog verifier output ---")
    print(prolog_verify(names))


if __name__ == "__main__":
    main()
