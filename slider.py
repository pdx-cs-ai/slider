#!/usr/bin/python3

import random

noise = 0.0

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
        t -= 1
        i = t // n
        j = t - n * i
        return (i, j)

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

    def solve_random(self, nsteps):
        soln = []
        nvisited = 0
        for _ in range(nsteps):
            if self.solved():
                print("nvisited:", nvisited)
                return soln

            nvisited += 1

            ms = self.moves()
            mnv = []

            if random.random() < noise:
                m = random.choice(ms)
            else:
                for m in ms:
                    (f, t) = m
                    self.move((f, t))
                    d = self.defect()
                    mnv.append((d, m))
                    self.move((t, f))

                md = min(mnv, key=lambda m: m[0])
                ms = [m[1] for m in mnv if m[0] == md[0]]
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

p = Puzzle(4)
print(p)
soln = p.solve_random(10000000)
if soln:
    print(len(soln))
else:
    print("no solution found")
