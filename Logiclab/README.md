# Logical Planning: "Logic + Search = Planning"

Laboratory report: a warehouse-robot planning agent in Python (STRIPS-style
actions + breadth-first search) with an independent Prolog plan verifier.

> **Note on authorship:** the code, outputs and tables below were produced and
> run for you. The reflection sections (marked *draft*) must be edited to
> describe what **you** actually did, accepted, changed and verified.

## Files

| File | Purpose |
|---|---|
| `planner.py` | State/Action representation, applicability, effects, BFS planner, independent plan checker, warehouse problem, CLI |
| `test_planner.py` | 14 unit tests (Tasks 0, A, B, C and extras) |
| `planner.pl` | Prolog for Tasks 6, 7, 8 |
| `verify_plan.pl` | Full plan verifier in Prolog (preconditions + effects) |
| `verify_with_prolog.py` | Python generates a plan, Prolog checks it (Generate → Independent verification) |
| `prompts.md` | Prompts used with the LLM (appendix) |

## Running

```bash
python planner.py                      # Test A: solvable warehouse problem
python planner.py --no-pickup          # Test B: PickUp removed -> "No plan found"
python planner.py --robot-goal         # Test C helper: goal At(Robot,C)
python -m unittest -v                  # all tests
python verify_with_prolog.py           # Prolog checks the Python plan  (needs swipl)
python verify_with_prolog.py --bad     # Prolog checks the handout's example sequence
swipl planner.pl                       # interactive Prolog (Tasks 6-8); try ?- can_move(a,b).
```

Python 3 standard library only. SWI-Prolog is needed only for the optional extension
(install from swi-prolog.org, or `sudo apt install swi-prolog`, or `brew install swi-prolog`).

---

## Task 0 – The planning problem

**(a) Initial state** `I = {At(Robot,A), At(Package,A)}`
**(b) Goal** `G = {At(Package,C)}`

**(c)/(d) Actions, preconditions and effects**

| Action | Preconditions | Add (positive effects) | Delete (negative effects) |
|---|---|---|---|
| `Move(A,B)` | At(Robot,A) | At(Robot,B) | At(Robot,A) |
| `Move(B,A)` | At(Robot,B) | At(Robot,A) | At(Robot,B) |
| `Move(B,C)` | At(Robot,B) | At(Robot,C) | At(Robot,B) |
| `Move(C,B)` | At(Robot,C) | At(Robot,B) | At(Robot,C) |
| `PickUp(Package,L)` for L ∈ {A,B,C} | At(Robot,L), At(Package,L) | Holding(Package) | At(Package,L) |
| `Drop(Package,L)` for L ∈ {A,B,C} | At(Robot,L), Holding(Package) | At(Package,L) | Holding(Package) |

**Which actions are applicable initially?**

* `PickUp(Package,A)` is **applicable**: both preconditions At(Robot,A) and At(Package,A) are in I.
* `Drop(Package,C)` is **not applicable**: At(Robot,C) is false and Holding(Package) is false.
* Also applicable initially: `Move(A,B)`. Not applicable: every other action (e.g. `PickUp(Package,B)`: the package is at A, not B).

An action is applicable only if S ⊨ Preconditions(a), not merely because it is in the action list.

## Task 1 – Plan by hand

| State | Facts |
|---|---|
| S0 | At(Robot,A), At(Package,A) |
| S1 = after `PickUp(Package,A)` | At(Robot,A), Holding(Package) |
| S2 = after `Move(A,B)` | At(Robot,B), Holding(Package) |
| S3 = after `Move(B,C)` | At(Robot,C), Holding(Package) |
| S4 = after `Drop(Package,C)` | At(Robot,C), At(Package,C) |

S4 ⊨ G, so the plan is valid.

> ⚠️ **The handout's suggested sequence is wrong.** Task 1 mentions
> `Move(A,B), PickUp(Package,B), Move(B,C), Drop(Package,C)`, but the package
> is at **A**, so `PickUp(Package,B)` is not applicable (At(Package,B) is false).
> The robot has to pick the package up *before* leaving A. Both the Python
> validator and the Prolog verifier reject the handout's sequence (see Task 5/7
> below). The handout says "for example, you might need to reason about…", so
> it is presenting ideas, not a solution. This is a good illustration of the
> lab's theme: a plan that *looks reasonable* is not necessarily valid.

## Task 2 – LLM implementation

See `prompts.md` (Prompt 1 is the handout's specification). Mapping of the
specification onto `planner.py`:

| Idea | Where in the program |
|---|---|
| State as a set of propositions | `frozenset` of strings such as `"At(Robot,A)"` |
| Action with 4 fact sets + name | `Action` dataclass (line 25) |
| Preconditions → *when is an action applicable?* | `applicable()` (line 44): `pos_pre ⊆ state` and `neg_pre ∩ state = ∅` |
| Effects → *how does the state change?* | `apply_action()` (line 49): `(state − neg_eff) ∪ pos_eff` |
| Goal → *when does planning terminate?* | `satisfies_goal()` (line 56), tested in `bfs_plan` (line 82) |
| BFS → *how are alternatives explored?* | `bfs_plan()` (line 74): FIFO `deque` frontier, `parent` dict as visited set and for plan reconstruction |
| "No plan found" | frontier becomes empty → `PlanResult(None, …)` (line 98) |

**Assumptions made:** all facts are ground (no variables); the world is
deterministic and fully known; each action's effects are exactly its add/delete
lists (STRIPS assumption: nothing else changes); the closed-world assumption (a
fact not in the state is false); the goal is a set of positive facts.

## Task 3 – Tests

| Test | Initial state | Goal | Plan found? | Plan | Valid? |
|---|---|---|---|---|---|
| **A** Solvable | {At(Robot,A), At(Package,A)} | At(Package,C) | Yes (8 states expanded) | PickUp(Package,A), Move(A,B), Move(B,C), Drop(Package,C) | ✅ every step checked by `validate_plan` |
| **B** Impossible (PickUp removed) | same | At(Package,C) | **No plan found** (3 states expanded) | – | ✅ correct to fail: no action can make Holding(Package) |
| **C** Irrelevant actions (only Move actions) | same | At(Package,C) | **No plan found** | – | ✅ robot can reach C but the package never leaves A |
| **C′** same actions, goal changed | same | At(Robot,C) | Yes | Move(A,B), Move(B,C) | ✅ shows the planner distinguishes the two goals |

Output of Test A:

```
a1 = PickUp(Package,A)   S1: ['At(Robot,A)', 'Holding(Package)']
a2 = Move(A,B)           S2: ['At(Robot,B)', 'Holding(Package)']
a3 = Move(B,C)           S3: ['At(Robot,C)', 'Holding(Package)']
a4 = Drop(Package,C)     S4: ['At(Package,C)', 'At(Robot,C)']
```

BFS finds a plan with the fewest actions (4); the tests confirm no 3-action plan
exists. All 14 tests pass (`python -m unittest -v`). The planner is also checked by
a separate function, `validate_plan`, that re-simulates the plan without using the
search code, and by Prolog (below).

## Task 4 – Logic and Search

Completed flow:

```
Current state
   ↓
Check action preconditions        (is S ⊨ Preconditions(a)?)
   ↓
Apply the action's effects        (remove negative effects, add positive effects)
   ↓
Generate successor state S' = Apply(S, a)
   ↓
Search over alternatives          (BFS: put S' in the FIFO frontier unless already seen)
   ↓
Goal?                             (G ⊆ S' → return the plan; otherwise continue)
```

**In my own words:** logic determines what is *possible*: for each state, it
says which actions may be executed (preconditions) and what the world looks like
afterwards (effects). Search determines what to *try*: among all the applicable
actions in all the states reached, BFS decides the order in which sequences are
explored and stops at the first goal state. Logic alone gives only one-step
possibilities; search alone would try impossible actions. Together they produce a
plan: *Logic + Search = Planning*.

## Task 5 (optional) – Can the LLM verify its own plan?

An LLM-written explanation ("PickUp needs At(Robot,A) and At(Package,A), both true
in S0…") is a natural-language *claim* that could contain a mistake or be
persuasively wrong. The independently executed transitions (`validate_plan`
in Python, and `verify_plan.pl` in Prolog) are *computed* from the action
definitions and cannot be talked into an error. Example: the handout's
sequence `Move(A,B), PickUp(Package,B), …` *reads* plausibly, but the executed
check says:

```
move(a,b)  applicable -> [at(package,a),at(robot,b)]
pickup(package,b)  NOT applicable in [at(package,a),at(robot,b)]
PLAN INVALID
```

**Trust (b), the independent state transitions.** A generated explanation is not
the same as an independent verification. The explanation is still useful for
understanding, but it must be checked against the executed transitions.

## "Think About It" answers (Task 0–4)

* *Applicable merely because it is listed?* No. It must satisfy S ⊨ Preconditions(a).
* *Where do preconditions, effects, goal and BFS appear in the code?* See the Task 2 table.
* *Logic determines what is possible; search determines what to try.* See Task 4.

## Optional extension – Prolog (Tasks 6–8)

Run from `planner.pl`:

| Query | Result |
|---|---|
| `?- can_move(a,b).` | true |
| `?- can_move(a,c).` | false |
| `?- valid_move(a,b).` | true |
| `?- valid_move(b,c).` | true |
| `?- valid_move(a,c).` | false |
| `?- valid_move_sequence([a,b,c]).` | true |
| `?- valid_move_sequence([a,c]).` | false |
| `?- reduce_speed.` | true |

**Task 6**
(a) `can_move(a,b)` is true because the fact `connected(a,b)` exists and the rule `can_move(X,Y) :- connected(X,Y)` lets Prolog derive it with X=a, Y=b.
(b) `can_move(a,c)` is not established because there is no fact `connected(a,c)` and no other rule that could derive it. (Note: Prolog's `false` means "cannot be proven from this knowledge base" (negation as failure / closed-world assumption), not "known to be false in the real world".)
(c) The rule corresponds to the implication `∀x,y. Connected(x,y) → CanMove(x,y)`: Prolog's `:-` reads "if", with the head as the conclusion and the body as the condition.

**Task 7:** `valid_move(a,b)` and `valid_move(b,c)` succeed; `valid_move(a,c)` fails.
**Challenge:** if Python proposed `Move(a,c)`, the query `?- valid_move(a,c).` fails, so the warehouse knowledge **does not support** the action. Python generated the candidate action; Prolog independently checks it against the logical description: *Generate → Independent verification.*
I also extended this to whole plans: `verify_plan.pl` checks preconditions and applies effects for every action. `python verify_with_prolog.py` shows it accepting the Python plan, and `--bad` shows it rejecting the handout's `PickUp(Package,B)` step.

**Task 8:** `reduce_speed` succeeds because:

```
wet_road (fact)  ⇒  slippery :- wet_road (rule)  ⇒  reduce_speed :- slippery (rule)  ⇒  reduce_speed (conclusion)
```

i.e. WetRoad, WetRoad → Slippery, Slippery → ReduceSpeed ⊢ ReduceSpeed (modus ponens applied twice).

**Reflection (Prolog)**
1. A *fact* is an unconditional statement (`connected(a,b).`); a *rule* says a conclusion holds if its conditions hold (`can_move(X,Y) :- connected(X,Y).`).
2. A query asks whether the statement can be derived from the facts and rules (whether it follows from the knowledge base). Success ≈ "provable"; failure ≈ "not provable from what the program contains".
3. A separate program with its own description of the world can catch invalid actions the generator proposed (e.g. a move between unconnected places), independently of how the plan was produced.
4. LLM-assisted code can be plausible but wrong. An independent verifier doesn't share the generator's assumptions or bugs, so agreement is stronger evidence, and disagreement flags an error that the generator's own explanation would hide.

---

## Reflection Questions (draft: adapt to your own experience)

1. **Why specify preconditions and effects before asking the LLM?** They define what "correct" means. Without them the LLM would choose its own semantics, and you could not tell whether the generated planner was right.
2. **Error if preconditions weren't checked?** The robot could `Drop(Package,C)` while still at A (so the package would "teleport" to C), or `PickUp` a package from another room. The planner would report a 1-step plan that is physically impossible.
3. **Why isn't a plan that looks reasonable necessarily valid?** Plausibility is judged informally; validity requires every action's preconditions to hold in the state where it is executed. The handout's `Move(A,B), PickUp(Package,B)…` example looks natural but fails because the package is still at A.
4. **What did the LLM contribute?** The translation of my specification into working code (Action class, BFS, state printing), the extra validator and the tests.
5. **What did I have to verify independently?** Applicability of every action, effects of each step, that the goal holds at the end, "no plan" behaviour, that robot-at-C ≠ package-at-C, and whether the plan is shortest. I did this with tests, the independent `validate_plan`, and Prolog.
6. **Where is logical reasoning used?** In `applicable()` (S ⊨ Preconditions(a)), in `apply_action()` (effects update the world model), in the goal test (G ⊆ S), and in the Prolog rules and queries.
7. **How is planning related to the previous module's search?** Planning *is* search in the state space: states are sets of facts, successor states come from applicable actions, the goal test checks the goal facts, and each action costs 1, exactly the BFS formulation used for the warehouse grid. The difference is that states and actions are described logically instead of by grid coordinates, so the same BFS works for any problem described this way.

**Which parts were LLM-generated or modified (draft)**

| Part | Source |
|---|---|
| Problem specification, hand-built plan, tests' expected outcomes | You (designed) |
| `planner.py` core (Action, applicable, apply, BFS) | LLM-generated from your specification |
| `validate_plan`, extra tests, Prolog verifier, bridge script | LLM-suggested additions |
| Changes you made | *(fill in)* |
