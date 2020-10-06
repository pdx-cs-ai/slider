#!/usr/bin/python3
# Generate and solve a sliding tile puzzle.
# Bart Massey 2020

import argparse
import functools
import heapq
import random

from collections import deque
from copy import copy, deepcopy

# Make a copy of an object with the given class but no fields.
# https://www.oreilly.com/library/view/python-cookbook/0596001673/ch05s12.html
def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    newcopy = Empty()
    newcopy.__class__ = obj.__class__
    return newcopy

# Returns True iff the puzzle is solvable.
# https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/
def ok_parity(n, tiles):
    n2 = len(tiles)
    inversions = 0
    blankpos = None
    for i in range(n2):
        if tiles[i] == 0:
            blankpos = i
            continue
        for j in range(i + 1, n2):
            if tiles[j] == 0:
                continue
            if tiles[j] < tiles[i]:
                inversions += 1
    if (n & 1) == 1:
        return (inversions & 1) == 0
    blankrow = blankpos // n
    return (blankrow & 1) != (inversions & 1)

# A* state for puzzle, so that keying works with hqueue
@functools.total_ordering
class Pstate(object):
    def __init__(self, k, s):
        self.k = k
        self.s = s
    
    def __eq__(self, o):
        return self.k == o.k
    
    def __lt__(self, o):
        return self.k < o.k
    
    def state(self):
        return self.s

    def key(self):
        return self.k

class Puzzle(object):

    # Create a puzzle
    def __init__(self, n, sat=True, tiles=None):
        if tiles == None:
            # Build a puzzle uniformly selected from
            # the space of puzzles with given solvability.
            tiles = [i for i in range(n**2)]
            random.shuffle(tiles)
            while sat != ok_parity(n, tiles):
                random.shuffle(tiles)

            # Square up the puzzle and find the blank.
            puzzle = []
            self.blank = None
            for i in range(n):
                row = []
                for j in range(n):
                    tile = tiles[n * i + j]
                    row.append(tile)
                    if tile == 0:
                        self.blank = (i, j)
                puzzle.append(row)
        else:
            # Do some rudimentary checks on supplied puzzle
            # and find the blank.
            puzzle = tiles
            self.blank = None
            assert len(puzzle) == n
            for i in range(len(puzzle)):
                nj = len(puzzle[i])
                assert nj == n
                for j in range(nj):
                    if puzzle[i][j] == 0:
                        self.blank = (i, j)

        # Finish initialization.
        assert self.blank != None
        self.n = n
        self.puzzle = puzzle
        self.visited = set()
        self.g = 0

    # Return a copy of this state.
    def __copy__(self):
        newcopy = empty_copy(self)
        newcopy.puzzle = deepcopy(self.puzzle)
        newcopy.n = self.n
        newcopy.blank = self.blank
        newcopy.g = self.g
        return newcopy

    # Produce a printable representation of the puzzle.
    def __str__(self):
        n = self.n
        result = ""
        for i in range(n):
            for j in range(n):
                tile = self.puzzle[i][j]
                if tile == 0:
                    result += "   "
                else:
                    result += "{:2} ".format(tile)
            result += "\n"
        return result

    # Just compare the puzzle itself.
    def __eq__(self, other):
        self.puzzle == other.puzzle
            
    # Turn the square puzzle into a linear list.
    def puzzle_list(self):
        result = []
        for row in self.puzzle:
            for tile in row:
                result.append(tile)
        return result

    # Hash is just hash of puzzle list.
    def __hash__(self):
        return hash(tuple(self.puzzle_list()))

    # Return a list of legal moves in the current position.
    # Moves are given as start-end tuples.
    def moves(self):
        n = self.n
        b = self.blank
        (i, j) = b
        ms = []
        for d in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            xi = i + d[0]
            xj = j + d[1]
            if xi >= 0 and xi < n and xj >= 0 and xj < n:
                ms.append(((xi, xj), b))
        return ms

    # Make the given move on the current position, updating
    # the blank.
    def move(self, m):
        assert m[1] == self.blank
        (i, j) = m[1]
        assert self.puzzle[i][j] == 0
        (xi, xj) = m[0]

        # XXX There's probably some more pythonic way to
        # swap these cells.
        tmp = self.puzzle[xi][xj]
        self.puzzle[xi][xj] = self.puzzle[i][j]
        self.puzzle[i][j] = tmp
        
        self.blank = (xi, xj)

    # Return the coordinates the given tile would
    # have in a solved puzzle.
    def target(self, t):
        n = self.n
        if t == 0:
            return (n - 1, n - 1)
        i = (t - 1) // n
        j = (t - 1) - n * i
        return (i, j)

    # Return True iff we are at the solved state.
    def solved(self):
        n = self.n
        for t in range(n * n):
            (i, j) = self.target(t)
            if self.puzzle[i][j] != t:
                return False
        return True

    def defect(self):
        n = self.n
        d = 0
        for i in range(n):
            for j in range(n):
                t = self.puzzle[i][j]
                if t == 0:
                    continue
                (ti, tj) = self.target(t)
                d += abs(i - ti) + abs(j - tj)
        return d

    # Do a random walk through the state space, attempting
    # to avoid previously-visited states when possible.
    def solve_random(self, nsteps, tabu=False):
        # Moves of solution.
        soln = []
        # Set of hashes of visited states.
        # XXX This could cause collisions, but statistically
        # no.
        visited = set()
        # Number of revisited states.
        nrevisited = 0

        # Walk specified number of steps.
        for _ in range(nsteps):
            # Stop when at the goal.
            if self.solved():
                print("nrevisited:", nrevisited)
                return soln

            if tabu:
                # Check whether in a visited state.
                if hash(self) in visited:
                    nrevisited += 1
                else:
                    visited.add(hash(self))

            # Get legal moves from here and
            # pick one.
            ms = self.moves()
            # Unvisited moves.
            mnv = []
            if tabu:
                for m in ms:
                    # Do-undo.
                    (f, t) = m
                    self.move((f, t))
                    if hash(self) not in visited:
                        mnv.append(m)
                    self.move((t, f))

            # Try to visit someplace new.
            if mnv != []:
                m = random.choice(mnv)
            else:
                m = random.choice(ms)

            # Remember the move that got us here,
            # and apply it.
            soln.append(m)
            self.move(m)

        # Ran out of moves.
        return None

    # Solve by random walk without tabu list, but with noise
    # moves.
    def solve_walk(self, nsteps, noise):
        # Moves in solution.
        soln = []

        # Walk the state space.
        for nvisited in range(nsteps):
            # Stop if at goal.
            if self.solved():
                print("nvisited:", nvisited + 1)
                return soln

            # Select from legal moves.
            ms = self.moves()
            if random.random() < noise:
                # Noise case. Select a random move.
                m = random.choice(ms)
            else:
                # Greedy case. Select a move with smallest
                # defect.
                mnv = []
                for m in ms:
                    # Do-undo.
                    (f, t) = m
                    self.move((f, t))
                    d = self.defect()
                    mnv.append((d, m))
                    self.move((t, f))

                # Prune off defects for selection.
                md = min(mnv, key=lambda m: m[0])
                ms = [m[1] for m in mnv if m[0] == md[0]]
                m = random.choice(ms)

            # Make and record the move.
            soln.append(m)
            self.move(m)

        # Ran out of steps.
        return None

    # Solve by breadth-first search with an explicit queue
    # and stop list.
    def solve_bfs(self):
        # Don't mess up this state, just make a new start
        # state.
        start = copy(self)
        start.parent = None
        start.move = None
        visited = {hash(start)}

        # Run the BFS.
        q = deque()
        q.appendleft(start)
        while len(q) > 0:
            # Get next state to expand.
            s = q.pop()

            # Try to expand each child.
            ms = s.moves()
            for m in ms:
                # Make the child.
                c = copy(s)
                c.move(m)

                # Found a solution. Reconstruct and return
                # it.
                if c.solved():
                    soln = [m]
                    while True:
                        s = s.parent
                        if not s:
                            break
                        soln.append(s.move)
                    return list(reversed(soln))

                # Don't re-expand a closed state.
                h = hash(c)
                if h in visited:
                    continue
                
                # Expand and enqueue this child.
                c.parent = s
                c.move = m
                visited.add(h)
                q.appendleft(c)

        # No solution exists.
        return None

    # Solve via depth-first iterative deepening.
    def solve_dfid(self):
        # Increase the depth repeatedly.
        for d in range(1, 500):
            # Reset the stop list.
            self.visited = dict()
            # Try solving at this depth.
            soln = self.solve_dfs(depth=d)
            if soln != None:
                assert len(soln) == d
                return soln
        # Should never get here.
        assert False
    
    # Solve via depth-first search with optional depth
    # limit.
    def solve_dfs(self, depth=None, heur=False):
        # Stop if solved.
        if self.solved():
            print("nvisited:", len(self.visited))
            return []

        # Out of depth, so stop early.
        if depth <= 0:
            return None

        # Augment stop list.
        self.visited[hash(self)] = depth

        def move_defect(m):
            (f, t) = m
            self.move((f, t))
            result = self.defect()
            self.move((t, f))
            return result

        # Find next depth.
        if depth == None:
            d = None
        else:
            d = depth - 1

        # Recursive search.
        ms = self.moves()
        if heur:
            ms.sort(key=move_defect)
        for m in ms:
            # Do-undo.
            (f, t) = m
            self.move((f, t))

            # If new state, search it.
            h = hash(self)
            if h not in self.visited:
                # Recursively solve.
                soln = self.solve_dfs(depth=d, heur=heur)
                if soln != None:
                    # Undo.
                    self.move((t, f))
                    return [m] + soln

            # Undo.
            self.move((t, f))

        # No solution found here.
        return None

    # Solve via A* search.
    def solve_astar(self):
        # Set up start state as with BFS.
        start = copy(self)
        start.parent = None
        start.move = None
        # Stop list needs to be dictionary so states
        # can be updated/reopened.
        visited = {hash(start): start}

        # Set up the heapq and start A*.
        q = []
        start.h = start.defect()
        start.f = start.g + start.h
        heapq.heappush(q, Pstate(start.f, start))
        while q:
            # Get best state via f = g + h.
            sk = q[0].key()
            s = heapq.heappop(q).state()

            # If solved, reconstruct and return the
            # solution.
            if s.solved():
                soln = []
                g = s.g
                states = {s}
                while True:
                    if s.move:
                        soln.append(s.move)
                    s = s.parent
                    if not s.parent:
                        break
                    assert s not in states
                    states.add(s)
                    g -= 1
                    assert g == s.g
                return list(reversed(soln))

            # Expand the children.
            ms = s.moves()
            for m in ms:
                c = copy(s)
                c.move(m)
                c.g = s.g + 1
                c.h = c.defect()
                c.f = c.g + c.h

                # Only expand unvisited or re-expand states.
                hh = hash(c)
                if hh not in visited or visited[hh].f > s.f:
                    c.parent = s
                    c.move = m
                    visited[hh] = c
                    heapq.heappush(q, Pstate(c.f, c))

        return None

def read_puzzle(filename):
    puzzle = []
    with open(filename, "r") as f:
        for row in f:
            tiles = [int(i) for i in row.split()]
            puzzle.append(tiles)
    return puzzle

# Process arguments.
parser = argparse.ArgumentParser(description='Solve Sliding Tile Puzzle.')
parser.add_argument('-n', type=int,
                    default=3, help='length of side')
parser.add_argument('--file', '-f', type=str,
                    default=None, help='file to read puzzle from')
parser.add_argument('--verbose', '-v',
                    action="store_true", help='show full solution')
parser.add_argument('--unsat', '-u',
                    action="store_true", help='use unsat puzzle')
solvers = {
    "random",
    "tabu",
    "walk",
    "bfs",
    "dfs",
    "dfid",
    "astar"
}
# https://stackoverflow.com/a/27529806
parser.add_argument('--solver', '-s',
                    type=str, choices=solvers,
                    default="random", help='solver algorithm')
parser.add_argument('--noise', type=float,
                    default=0.5, help='noise for walk')
args = parser.parse_args()
n = args.n
solver = args.solver
full = args.verbose
sat = not args.unsat
noise = args.noise
if args.file == None:
    # Build a random puzzle.
    p = Puzzle(n, sat=sat)
else:
    puzzle = read_puzzle(args.file)
    n = len(puzzle)
    p = Puzzle(n, tiles=puzzle)

# Run the solver.
print(p)
if solver == "random":
    soln = p.solve_random((1000 * n)**2)
elif solver == "tabu":
    soln = p.solve_random((1000 * n)**2, tabu=True)
elif solver == "walk":
    soln = p.solve_walk((1000 * n)**2, noise)
elif solver == "bfs":
    soln = p.solve_bfs()
elif solver == "dfid":
    soln = p.solve_dfid()
elif solver == "dfs":
    soln = p.solve_dfs(heur=True)
elif solver == "astar":
    soln = p.solve_astar()
else:
    assert False

# Show the solution if any.
if soln:
    if full:
        for m in soln:
            print(m)
    else:
        print(len(soln))
else:
    print("no solution found")
