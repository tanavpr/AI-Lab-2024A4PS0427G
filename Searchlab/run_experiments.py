"""Reproduces every table in the report. Run:  python run_experiments.py"""
from search_lab import Grid, astar, bfs, HEURISTICS
from maps import ALL

def row(name, res):
    return (f"| {name:<22} | {str(res.found):<5} | "
            f"{res.length if res.found else '-':>4} | {res.expanded:>8} |")

HEADER = ("| Version                | Found | Path | Expanded |\n"
          "|------------------------|-------|------|----------|")

print("TASK 3 - tests (A*, Manhattan)\n" + HEADER)
for name, layout in ALL.items():
    print(row(name, astar(Grid(layout))))

print("\nTASK 5 - BFS vs A* on the original warehouse\n" + HEADER)
g = Grid(ALL["original"])
print(row("BFS", bfs(g)))
print(row("A* (Manhattan)", astar(g)))

print("\nTASK 6 - heuristic investigation (original warehouse)\n" + HEADER)
for name, h in HEURISTICS.items():
    print(row(f"A* h={name}", astar(g, h)))

print("\nTASK 6 (extra) - same heuristics on the open room, where they differ more\n" + HEADER)
g2 = Grid(ALL["open_room"])
print(row("BFS", bfs(g2)))
for name, h in HEURISTICS.items():
    print(row(f"A* h={name}", astar(g2, h)))

print("\nTASK 6 (extra) - over-aggressive heuristic on the 'overshoot' map\n" + HEADER)
g3 = Grid(ALL["overshoot"])
print(row("BFS (optimal)", bfs(g3)))
for name, h in HEURISTICS.items():
    print(row(f"A* h={name}", astar(g3, h)))
