# Prompts used with the LLM (Appendix)

> Replace or extend these with the exact prompts from your own LLM session if
> you ran one. The handout asks you to identify which parts of the program were
> generated or modified with LLM assistance.

## Prompt 1 – Planner (the handout's specification)

I want to implement a simple planning agent in Python.
Represent a state as a set of logical propositions.
Each action should contain: a name; positive preconditions; negative
preconditions; positive effects; negative effects.
An action is applicable if all of its preconditions are satisfied by the current
state. When an action is applied: (1) remove its negative effects from the
state; (2) add its positive effects to the state.
Use breadth-first search to find a sequence of actions that achieves a specified
goal. The program should also: detect when no plan exists; print the resulting
sequence of actions; print the states reached after each action.
Explain the implementation and identify any assumptions you make.

Warehouse problem: locations A, B, C; connections A-B and B-C (both directions);
Move, PickUp(Package, L) and Drop(Package, L) with the preconditions and effects
given in the handout. Initial: At(Robot,A), At(Package,A). Goal: At(Package,C).

## Prompt 2 – Independent plan checker

Add a function that takes an initial state, a plan and a goal, re-simulates the
plan step by step WITHOUT using the search code, and reports for each step
whether the preconditions held, plus whether the goal is satisfied at the end.

## Prompt 3 – Tests (Tasks 3A, 3B, 3C)

Write unittest tests: (A) the warehouse problem returns a valid 4-action plan;
(B) with the PickUp action removed the planner reports no plan; (C) with only
Move actions available, "robot at C" is reachable but "package at C" is not.
Also test that an inapplicable action raises an error.

## Prompt 4 – Task 5 (optional): explanation

For every action in the plan, identify its preconditions and show that those
preconditions are satisfied in the state in which the action is executed.

## Prompt 5 – Prolog verifier (optional extension)

Write a Prolog program that represents the warehouse as facts (connected/2) and
actions as action(Name, PosPre, NegPre, Add, Delete), and verifies a plan by
checking each action's preconditions in turn and applying its effects.
