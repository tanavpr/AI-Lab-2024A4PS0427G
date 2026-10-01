"""Test maps used in Task 3 (and the original warehouse)."""
from search_lab import WAREHOUSE

TRIVIAL = ["#####",
           "#SG##",
           "#####"]

NO_SOLUTION = ["#######",
               "#S....#",
               "###.###",
               "#...#G#",
               "#######"]

# Two routes: top row (4 moves) and a detour round the bottom (8 moves).
ALTERNATIVE = ["#######",
               "#S...G#",
               "#.###.#",
               "#.....#",
               "#######"]

# Open room: many equally short paths (Manhattan distance is exact here).
OPEN_ROOM = ["#######",
             "#S....#",
             "#.....#",
             "#....G#",
             "#######"]

# Over-aggressive heuristic demo: 2 x Manhattan overestimates (inadmissible)
# and returns a longer-than-optimal path here.
OVERSHOOT = ["#########",
             "#S.#.#..#",
             "#....##.#",
             "#.#.....#",
             "#....#..#",
             "##..#..G#",
             "#########"]

ALL = {"original": WAREHOUSE, "trivial": TRIVIAL, "no_solution": NO_SOLUTION,
       "alternative": ALTERNATIVE, "open_room": OPEN_ROOM,
       "overshoot": OVERSHOOT}
