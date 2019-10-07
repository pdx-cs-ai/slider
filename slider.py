#!/usr/bin/python3

import random

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
        i = t // n
        j = t - n * i
        return (i, j)

    def solved(self):
        n = self.n
        if self.blank != (n - 1, n - 1):
            return False
        for t in range(n * n - 1):
            (i, j) = self.target(t)
            if self.puzzle[i][j] != t + 1:
                return False
        return True

    def solve_random(self, nsteps):
        soln = []
        for _ in range(nsteps):
            ms = self.moves()
            m = random.choice(ms)
            soln.append(m)
            self.move(m)
            if self.solved():
                return soln
        return None
            
p = Puzzle(3)
print(p)
soln = p.solve_random(10000000)
if soln:
    print(len(soln))
else:
    print("no solution")
