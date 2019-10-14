# Sliding Tile Puzzle Solvers
Bart Massey

This Python codebase gives some example techniques for
solving
[Sliding Tile Puzzle](https://en.wikipedia.org/wiki/Sliding_puzzle)
problems.

Say `python3 slider.py --help` for program arguments.

Solvers:

* random: Do a random walk through the state space, with a
  tabu list to try to avoid previous states

* walk: Local search with a heuristic greedy walk with noise
  moves, no tabu list

* bfs: Complete breadth-first-search with stop list.

* dfid: Depth-first iterative deepening with stop list.
