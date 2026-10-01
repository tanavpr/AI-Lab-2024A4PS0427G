"""
Logical planning agent for the warehouse problem
================================================

Logic + Search = Planning

* A STATE is a frozenset of ground propositions, e.g. "At(Robot,A)".
* An ACTION has positive/negative preconditions and positive/negative effects.
* LOGIC   : an action is applicable in state S if S |= Preconditions(a)
            (every positive precondition is in S, no negative precondition is).
* EFFECTS : apply(S, a) = (S - neg_effects) | pos_effects
* SEARCH  : breadth-first search over sequences of applicable actions until
            a state satisfying the goal (goal facts are all in the state).
"""

import argparse
from collections import deque
from dataclasses import dataclass


# --------------------------------------------------------------------------
# Representation
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Action:
    name: str
    pos_pre: frozenset = frozenset()   # facts that must be true
    neg_pre: frozenset = frozenset()   # facts that must be false
    pos_eff: frozenset = frozenset()   # facts made true  (add list)
    neg_eff: frozenset = frozenset()   # facts made false (delete list)

    def __str__(self):
        return self.name


def make_action(name, pos_pre=(), neg_pre=(), pos_eff=(), neg_eff=()):
    return Action(name, frozenset(pos_pre), frozenset(neg_pre),
                  frozenset(pos_eff), frozenset(neg_eff))


# --------------------------------------------------------------------------
# Logic: applicability and effects
# --------------------------------------------------------------------------
def applicable(state, action):
    """S |= Preconditions(a)."""
    return action.pos_pre <= state and not (action.neg_pre & state)


def apply_action(state, action):
    """S' = (S - negative effects) + positive effects. Refuses inapplicable actions."""
    if not applicable(state, action):
        raise ValueError(f"{action} is not applicable in {sorted(state)}")
    return (state - action.neg_eff) | action.pos_eff


def satisfies_goal(state, goal):
    return frozenset(goal) <= state


# --------------------------------------------------------------------------
# Search: breadth-first over states
# --------------------------------------------------------------------------
class PlanResult:
    def __init__(self, plan, states, expanded):
        self.plan = plan            # list[Action] or None
        self.states = states        # list of states S0..Sn or None
        self.expanded = expanded

    @property
    def found(self):
        return self.plan is not None


def bfs_plan(initial, actions, goal):
    initial = frozenset(initial)
    parent = {initial: None}                 # state -> (previous state, action)
    frontier = deque([initial])
    expanded = 0
    while frontier:
        state = frontier.popleft()
        expanded += 1
        if satisfies_goal(state, goal):      # goal test: terminates planning
            plan, states, s = [], [state], state
            while parent[s] is not None:
                prev, act = parent[s]
                plan.append(act)
                states.append(prev)
                s = prev
            plan.reverse()
            states.reverse()
            return PlanResult(plan, states, expanded)
        for act in actions:
            if applicable(state, act):       # logic decides what is possible
                nxt = apply_action(state, act)
                if nxt not in parent:        # search decides what to try
                    parent[nxt] = (state, act)
                    frontier.append(nxt)
    return PlanResult(None, None, expanded)  # "No plan found"


# --------------------------------------------------------------------------
# Independent plan checker (does not use bfs_plan or its bookkeeping)
# --------------------------------------------------------------------------
def validate_plan(initial, plan, goal):
    """Re-simulate a plan step by step. Returns (ok, list_of_messages)."""
    state = set(initial)
    log = []
    for i, act in enumerate(plan, start=1):
        missing = [p for p in act.pos_pre if p not in state]
        violated = [p for p in act.neg_pre if p in state]
        if missing or violated:
            log.append(f"step {i}: {act} NOT applicable "
                       f"(missing: {sorted(missing)}, forbidden present: {sorted(violated)})")
            return False, log
        state -= set(act.neg_eff)
        state |= set(act.pos_eff)
        log.append(f"step {i}: {act} OK -> {sorted(state)}")
    ok = set(goal) <= state
    log.append("goal satisfied" if ok else f"goal NOT satisfied (final: {sorted(state)})")
    return ok, log


# --------------------------------------------------------------------------
# The warehouse problem
# --------------------------------------------------------------------------
LOCATIONS = ["A", "B", "C"]
CONNECTIONS = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B")]

def move(a, b):
    return make_action(f"Move({a},{b})",
                       pos_pre=[f"At(Robot,{a})"],
                       pos_eff=[f"At(Robot,{b})"],
                       neg_eff=[f"At(Robot,{a})"])

def pickup(loc):
    return make_action(f"PickUp(Package,{loc})",
                       pos_pre=[f"At(Robot,{loc})", f"At(Package,{loc})"],
                       pos_eff=["Holding(Package)"],
                       neg_eff=[f"At(Package,{loc})"])

def drop(loc):
    return make_action(f"Drop(Package,{loc})",
                       pos_pre=[f"At(Robot,{loc})", "Holding(Package)"],
                       pos_eff=[f"At(Package,{loc})"],
                       neg_eff=["Holding(Package)"])

def warehouse_actions():
    acts = [move(a, b) for a, b in CONNECTIONS]
    acts += [pickup(l) for l in LOCATIONS]
    acts += [drop(l) for l in LOCATIONS]
    return acts

INITIAL = frozenset({"At(Robot,A)", "At(Package,A)"})
GOAL = frozenset({"At(Package,C)"})


def show(initial, actions, goal, label):
    res = bfs_plan(initial, actions, goal)
    print(f"=== {label} ===")
    print(f"Initial : {sorted(initial)}")
    print(f"Goal    : {sorted(goal)}")
    if not res.found:
        print(f"No plan found  (states expanded: {res.expanded})")
        return res
    print(f"Plan found ({len(res.plan)} actions, states expanded: {res.expanded}):")
    print(f"  S0: {sorted(res.states[0])}")
    for i, (a, s) in enumerate(zip(res.plan, res.states[1:]), start=1):
        print(f"  a{i} = {a}")
        print(f"  S{i}: {sorted(s)}")
    ok, _ = validate_plan(initial, res.plan, goal)
    print(f"Independent validation: {'VALID' if ok else 'INVALID'}")
    return res


def main():
    p = argparse.ArgumentParser(description="Logical planning agent (BFS)")
    p.add_argument("--no-pickup", action="store_true", help="Test B: remove PickUp")
    p.add_argument("--robot-goal", action="store_true",
                   help="Test C: goal is At(Robot,C) instead of At(Package,C)")
    args = p.parse_args()

    actions = warehouse_actions()
    goal = GOAL
    if args.no_pickup:
        actions = [a for a in actions if not a.name.startswith("PickUp")]
    if args.robot_goal:
        goal = frozenset({"At(Robot,C)"})
    show(INITIAL, actions, goal, "Warehouse planner")


if __name__ == "__main__":
    main()
