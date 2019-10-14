#!/usr/bin/python3

import random
import argparse

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

    def __init__(self, n, sat=True):
        tiles = [i for i in range(n**2)]
        random.shuffle(tiles)
        while sat and not ok_parity(n, tiles):
            random.shuffle(tiles)
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
        assert self.blank != None
        self.n = n
        self.puzzle = puzzle

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

    def move(self, m):
        assert m[1] == self.blank
        (i, j) = m[1]
        assert self.puzzle[i][j] == 0
        (xi, xj) = m[0]
        tmp = self.puzzle[xi][xj]
        self.puzzle[xi][xj] = self.puzzle[i][j]
        self.puzzle[i][j] = tmp
        self.blank = (xi, xj)

    def target(self, t):
        n = self.n
        if t == 0:
            return (n - 1, n - 1)
        i = (t - 1) // n
        j = (t - 1) - n * i
        return (i, j)

    def solved(self):
        n = self.n
        for t in range(n * n):
            (i, j) = self.target(t)
            if self.puzzle[i][j] != t:
                return False
        return True

    def solve_random(self, nsteps):
        soln = []
        visited = set()
        nvisited = 0
        for _ in range(nsteps):
            if self.solved():
                print("nvisited:", nvisited)
                return soln

            if self in visited:
                nvisited += 1
            else:
                visited.add(self)

            ms = self.moves()
            mnv = []

            for m in ms:
                (f, t) = m
                self.move((f, t))
                if self not in visited:
                    mnv.append(m)
                self.move((t, f))

            if mnv:
                m = random.choice(mnv)
            else:
                m = random.choice(ms)

            soln.append(m)
            self.move(m)

        return None
            

    def __eq__(self, other):
        self.puzzle == other.puzzle
            
    def puzzle_list(self):
        result = []
        for row in self.puzzle:
            for tile in row:
                result.append(tile)
        return result

    def __hash__(self):
        return hash(tuple(self.puzzle_list()))

# Process arguments.
parser = argparse.ArgumentParser(description='Solve Sliding Tile Puzzle.')
parser.add_argument('-n', type=int,
                    default=3, help='length of side')
parser.add_argument('--solution', '-s',
                    action="store_true", help='show full solution')
solvers = {
    "random"
}
# https://stackoverflow.com/a/27529806
parser.add_argument('--solver', '-c',
                    type=str, choices=solvers,
                    default="random", help='solver algorithm')
args = parser.parse_args()
n = args.n
solver = args.solver
full = args.solution

p = Puzzle(n)
print(p)
if solver == "random":
    soln = p.solve_random((1000 * n)**2)
else:
    assert False

if soln:
    if full:
        for m in soln:
            print(m)
    else:
        print(len(soln))
else:
    print("no solution found")
