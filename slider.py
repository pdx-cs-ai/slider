#!/usr/bin/python3

# Generate and solve a sliding tile puzzle.

import random
import argparse

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

class Puzzle(object):

    # Create a random puzzle
    def __init__(self, n, sat=True):
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

        # Finish initialization.
        assert self.blank != None
        self.n = n
        self.puzzle = puzzle

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
    def solve_random(self, nsteps):
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
            for m in ms:
                # Do-undo.
                (f, t) = m
                self.move((f, t))
                if hash(self) not in visited:
                    mnv.append(m)
                self.move((t, f))

            # Try to visit someplace new.
            if mnv:
                m = random.choice(mnv)
            else:
                m = random.choice(ms)

            # Remember the move that got us here,
            # and apply it.
            soln.append(m)
            self.move(m)

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

# Process arguments.
parser = argparse.ArgumentParser(description='Solve Sliding Tile Puzzle.')
parser.add_argument('-n', type=int,
                    default=3, help='length of side')
parser.add_argument('--verbose', '-v',
                    action="store_true", help='show full solution')
parser.add_argument('--unsat', '-u',
                    action="store_true", help='use unsat puzzle')
solvers = {
    "random",
    "walk",
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

# Build a random puzzle and run the solver.
p = Puzzle(n, sat=sat)
print(p)
if solver == "random":
    soln = p.solve_random((1000 * n)**2)
elif solver == "walk":
    soln = p.solve_walk((1000 * n)**2, noise)
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
