import itertools
import sys

characters = 'ABCDEFGHI'
numbers = '123456789'

class Sudoku:
    def __init__(self, board):
        self.variables, self.domains, self.constraints, self.neighbors, self.pruned = list(), dict(), list(), dict(), dict()
        self.prepare(board)

    def prepare(self, board):
        game = board
        self.variables = [a + b for a in characters for b in numbers]
        self.domains = dict((v, list(range(1, 10)) if game[i] == '0' else [int(game[i])]) for i, v in enumerate(self.variables))
        self.pruned = dict((v, [] if game[i] == '0' else [int(game[i])]) for i, v in enumerate(self.variables))
        self.build_constraints()
        self.neighbors = dict((x, [c[1] for c in self.constraints if x == c[0]]) for x in self.variables)

    def build_constraints(self):
        blocks = [[a + b for a in characters for b in number] for number in numbers]\
                 + [[a + b for a in character for b in numbers] for character in characters]\
                 + [[a + b for a in character for b in number] for character in ('ABC', 'DEF', 'GHI') for number in ('123', '456', '789')]
        for block in blocks:
            combinations = [subset for L in range(0, len(block) + 1) for subset in itertools.permutations(block, L) if L == 2]
            for combination in combinations:
                if [combination[0], combination[1]] not in self.constraints:
                    self.constraints.append([combination[0], combination[1]])

    def solved(self):
        for v in self.variables:
            if not self.domains[v]:
                return False
        return True

    def consistent(self, assignment, var, value):
        consistent = True
        for key, val in assignment.iteritems():
            if val == value and key in self.neighbors[var]:
                consistent = False
        return consistent

    def unassign(self, var, assignment):
        if var in assignment:
            for (D, v) in self.pruned[var]:
                self.domains[D].append(v)
            self.pruned[var] = []
            del assignment[var]

    def forward_check(self, var, value, assignment):
        for neighbor in self.neighbors[var]:
            if neighbor not in assignment and value in self.domains[neighbor]:
                self.domains[neighbor].remove(value)
                self.pruned[var].append((neighbor, value))