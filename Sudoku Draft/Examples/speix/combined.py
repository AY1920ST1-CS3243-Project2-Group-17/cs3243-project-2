import itertools
import sys
import copy

characters = 'ABCDEFGHI'
numbers = '123456789'

import argparse
from sudoku import Sudoku
import os
from collections import deque

# Source: https://github.com/speix/sudoku-solver

class Variable(object):
    def __init__(self, name, value=None, domain=None, 
                 pruned=None, neighbours=None):
        self.name = name
        self.value = value
        self.domain = set() if domain is None else domain
        self.pruned = [] if pruned is None else pruned
        self.neighbours = set() if neighbours is None else neighbours

    def add_neighbour(self, other):
        self.neighbours.add(other)

    def order_domain_values(self):
        if len(self.domain) == 1:
            return list(self.domain)
        return sorted(self.domain, key=lambda val: self.conflicts(val))

    def conflicts(self, val):
        count = 0
        for n in self.neighbours:
            if len(n.domain) > 1 and val in n.domain:
                count += 1
        return count

    def is_assigned(self):
        return self.value is not None and self.value != 0

    def __repr__(self):
        return self.name

class Csp(object):
    def __init__(self, name_var_map={}, constraint_funcs=[]):
        self.name_var_map = name_var_map
        self.assigned_vars = set()
        self.unassigned_vars = set()
        [(self.assigned_vars.add(var) 
          if var.is_assigned() else self.unassigned_vars.add(var))
         for var in self.name_var_map.values()]
        # self.init_assigned = len(self.assigned_vars)
        self.constraints = [(v, neighbour) for v in self.name_var_map.values()
                            for neighbour in v.neighbours]
        # self.constraint_funcs = constraint_funcs
        self.pruned_variables = []
        # self.variables_with_discarded_domain_vals = []
        self.show_log = True
    
    def print_log(self, str):
        if self.show_log:
            print(str)

    def select_unassigned_variable(self):
        unassigned = sorted([v for v in self.name_var_map.values() if not v.is_assigned()], key=lambda var: var.name)
        return min(unassigned, key=lambda var: len(var.domain))

    def backtrack(self):
        if self.is_solved():
            return True
        Sudoku.show_puzzle(self)
        var = self.select_unassigned_variable()
        print(str(var) + ' selected.')
        for value in var.order_domain_values():
            if self.consistent(var, value):
                print(str(var) + ' consistent with ' + str(value))
                self.assign(var, value)
                print('Assigned ' + str(value) + ' to ' + str(var))
                result = self.backtrack()
                if result:
                    return result
                self.unassign(var)
                print('Unassigned ' + str(value) + ' to ' + str(var))
        return False

    # def assign(self, var, value, assignment):
    #     assignment[var] = value
    #     self.forward_check(var, value, assignment)

    # def unassign(self, var, assignment):
    #     if var in assignment:
    #         for (D, v) in self.pruned[var]:
    #             self.domains[D].append(v)
    #         self.pruned[var] = []
    #         del assignment[var]

    # def forward_check(self, var, value, assignment):
    #     for neighbor in self.neighbors[var]:
    #         if neighbor not in assignment:
    #             if value in self.domains[neighbor]:
    #                 self.domains[neighbor].remove(value)
    #                 self.pruned[var].append((neighbor, value))

    def assign(self, var, value):
        var.value = value
        self.forward_check(var, value)
        self.assigned_vars.add(var)
        self.unassigned_vars.remove(var)

    def unassign(self, var):
        if var.is_assigned():
            for (D, v) in var.pruned: 
                D.domain.add(v)
            var.pruned = []
            # self.pruned_variables = []
            var.value = None
            self.unassigned_vars.add(var)
            self.assigned_vars.remove(var)

    def forward_check(self, var, value):
        for n in var.neighbours:
            if not n.is_assigned():
                if value in n.domain:
                    n.domain.discard(value)
                    assert type(value) == int
                    var.pruned.append((n, value))
                    # self.pruned_variables.append(var)

    def consistent(self, var, value):
        consistent = True
        for variable in self.name_var_map.values():
            val = var.value
            if val == value and variable in var.neighbours:
                consistent = False
        return consistent


    def ac3(self):
        def revise(xi, xj):
            revised = False
            for x in xi.domain.copy():
                if not any([x != y for y in xj.domain]):
                    xi.domain.discard(x)
                    revised = True
            return revised

        queue = deque(self.constraints)
        while queue:
            xi, xj = queue.popleft()
            if revise(xi, xj):
                if len(xi.domain) == 0:
                    return False
                for xk in xi.neighbours:
                    if xk != xi:
                        queue.append((xk, xi))
        return True

    def solve(self):
        if self.ac3():
            if self.is_solved():
                return True
            else:
                return self.backtrack()
        else:
            return False

    def is_solved(self):
        return len(self.unassigned_vars) == 0

class Sudoku:
    def __init__(self, board):
        self.variables, self.domains, self.constraints, self.neighbors, self.pruned = [], {}, [], {}, {}
        self.prepare(board)

    def prepare(self, board):
        game = list(board)
        self.variables = self.combine(characters, numbers)
        self.domains = {v: list(range(1, 10)) if game[i] == '0' else [int(game[i])] for i, v in enumerate(self.variables)}
        self.pruned = {v: list() if game[i] == '0' else [int(game[i])] for i, v in enumerate(self.variables)}
        self.build_constraints()
        self.build_neighbors()

    def build_constraints(self):
        blocks = (
            [self.combine(characters, number) for number in numbers] +
            [self.combine(character, numbers) for character in characters] +
            [self.combine(character, number) for character in ('ABC', 'DEF', 'GHI') for number in ('123', '456', '789')]
        )
        for block in blocks:
            combinations = self.permutate(block)
            for combination in combinations:
                if [combination[0], combination[1]] not in self.constraints:
                    self.constraints.append([combination[0], combination[1]])

    def build_neighbors(self):
        for x in self.variables:
            self.neighbors[x] = list()
            for c in self.constraints:
                if x == c[0]:
                    self.neighbors[x].append(c[1])

    def solved(self):
        for v in self.variables:
            if len(self.domains[v]) > 1:
                return False
        return True

    def consistent(self, assignment, var, value):
        consistent = True
        for key, val in assignment.iteritems():
            if val == value and key in self.neighbors[var]:
                consistent = False
        return consistent

    def assign(self, var, value, assignment):
        assignment[var] = value
        self.forward_check(var, value, assignment)

    def unassign(self, var, assignment):
        if var in assignment:
            for (D, v) in self.pruned[var]:
                self.domains[D].append(v)
            self.pruned[var] = []
            del assignment[var]

    def forward_check(self, var, value, assignment):
        for neighbor in self.neighbors[var]:
            if neighbor not in assignment:
                if value in self.domains[neighbor]:
                    self.domains[neighbor].remove(value)
                    self.pruned[var].append((neighbor, value))

    def constraint(self, xi, xj): return xi != xj

    @staticmethod
    def combine(alpha, beta):
        return [a + b for a in alpha for b in beta]

    @staticmethod
    def permutate(iterable):
        result = list()

        for L in range(0, len(iterable) + 1):
            if L == 2:
                for subset in itertools.permutations(iterable, L):
                    result.append(subset)

        return result

    @staticmethod
    def conflicts(sudoku, var, val):
        count = 0
        for n in sudoku.neighbors[var]:
            if len(sudoku.domains[n]) > 1 and val in sudoku.domains[n]:
                count += 1
        return count

def ac3(sudoku):
    def revise(sudoku, xi, xj):
        revised = False
        for x in sudoku.domains[xi]:
            if not any([sudoku.constraint(x, y) for y in sudoku.domains[xj]]):
                sudoku.domains[xi].remove(x)
                revised = True
        return revised

    queue = deque(sudoku.constraints)
    while queue:
        xi, xj = queue.popleft()
        if revise(sudoku, xi, xj):
            if len(sudoku.domains[xi]) == 0:
                return False
            for xk in sudoku.neighbors[xi]:
                if xk != xi:
                    queue.append([xk, xi])
    return True

def backtrack(assignment, sudoku):
    if len(assignment) == len(sudoku.variables):
        assert csp.is_solved()
        return assignment
    check_var(sudoku, csp)
    var = select_unassigned_variable(assignment, sudoku)
    var2 = csp.select_unassigned_variable()
    check_var(sudoku, csp)
    assert var == var2.name, str((var, var2))
    for value in order_domain_values(sudoku, var):
        if sudoku.consistent(assignment, var, value):
            assert csp.consistent(var2, value)
            check_var(sudoku, csp)
            csp.assign(var2, value)
            sudoku.assign(var, value, assignment)
            check_var(sudoku, csp)
            result = backtrack(assignment, sudoku)
            if result:
                return result
            check_var(sudoku, csp)
            csp.unassign(var2)
            sudoku.unassign(var, assignment)
            check_var(sudoku, csp)
    return False

def select_unassigned_variable(assignment, sudoku):
    unassigned = [v for v in sudoku.variables if v not in assignment]
    return min(unassigned, key=lambda var: len(sudoku.domains[var]))

def order_domain_values(sudoku, var):
    if len(sudoku.domains[var]) == 1:
        return sudoku.domains[var]
    return sorted(sudoku.domains[var], key=lambda val: sudoku.conflicts(sudoku, var, val))

def print_sudoku(sudoku, assignment):
    out = ''
    keys = sorted(sudoku.variables)
    for n, key in enumerate(keys):
        out += str(assignment.get(key, 0)) + (' ' if n != len(keys) else '') \
               + ('\n' if (n+1)%9 == 0 and n != len(keys)-1 else '')
    print(out)

parser = argparse.ArgumentParser()
parser.add_argument('board')
args = parser.parse_args()

sudoku = Sudoku(args.board)

def check_var(sudoku, csp):
    csp_variables = [k for k, v in sorted(csp.name_var_map.items())]
    csp_pruned = [(k, sorted([(var[0].name, sorted(var[1]) if type(var[1]) != int else var[1]) if type(var) != int else var for var in v.pruned])) for k, v in sorted(csp.name_var_map.items())]
    csp_constraints = sorted([[v.name, neighbour.name] for v in csp.name_var_map.values() for neighbour in v.neighbours])
    csp_domain = [(k, sorted(list(v.domain))) for k, v in sorted(csp.name_var_map.items())]
    csp_neighbours = [(k, sorted([var.name for var in v.neighbours])) for k, v in sorted(csp.name_var_map.items())]

    sudoku_variables = sorted(sudoku.variables)
    sudoku_domain = [(v[0], sorted(v[1])) if type(v) != int else v for v in sorted(sudoku.domains.items())]
    sudoku_pruned = [(v[0], sorted(v[1])) if type(v) != int else v for v in sorted(sudoku.pruned.items())]
    sudoku_constraints = sorted(sudoku.constraints)
    sudoku_neighbours = sorted({k: sorted(v) for k, v in sudoku.neighbors.items()}.items())
    
    assert csp_variables == sudoku_variables
    # if csp_pruned != sudoku_pruned:
    #     for i in range(len(csp_pruned)):
    #         if csp_pruned[i] != sudoku_pruned[i]:
    #             raise Exception(csp_pruned[i], sudoku_pruned[i])
    if csp_domain != sudoku_domain:
        for i in range(len(csp_domain)):
            if csp_domain[i] != sudoku_domain[i]:
                raise Exception(csp_domain[i], sudoku_domain[i])
    assert csp_pruned == sudoku_pruned, ('\n' + str(csp_pruned) + '\n\n' + str(sudoku_pruned))
    assert csp_constraints == sudoku_constraints
    assert csp_neighbours == sudoku_neighbours
    assert csp_domain == sudoku_domain, ('\n' + str(csp_domain) + '\n\n' + str(sudoku_domain))

f = open('public_tests_p2_sudoku/input1.txt', 'r')
mypuzzle = [[0 for i in range(9)] for j in range(9)]
lines = f.readlines()

i, j = 0, 0
for line in lines:
    for number in line:
        if '0' <= number <= '9':
            mypuzzle[i][j] = int(number)
            j += 1
            if j == 9:
                i += 1
                j = 0

def set_variable_neighbours(var_ls):
        for i in range(len(var_ls)-1):
            for j in range(i+1, len(var_ls)):
                # print(type(var_ls[i]))
                var_ls[i].add_neighbour(var_ls[j])
                var_ls[j].add_neighbour(var_ls[i])

def get_csp():
    name_var_map = {}
    row_constraints = {}
    col_constraints = {}
    box_constraints = {}
    for a, line in enumerate(mypuzzle):
        for n, number in enumerate(line):
            number = number if number != 0 else None
            row_letter = chr(a + 65)
            col_index = str(n + 1)
            name = row_letter + col_index
            var = Variable(name, number, 
                            set(range(1, 10) if number == None else [number]), 
                            [] if number == None else [number])
            name_var_map[name] = var
            try:
                row_constraints[row_letter].append(var)
            except KeyError:
                row_constraints[row_letter] = [var]
            try:
                col_constraints[col_index].append(var)
            except KeyError:
                col_constraints[col_index] = [var]
            box_row = a // 3
            box_col = n // 3
            box_index = box_row * 3 + box_col
            try:
                box_constraints[box_index].append(var)
            except KeyError:
                box_constraints[box_index] = [var]

    for constraints_map in [row_constraints, col_constraints, box_constraints]:
        for var_ls in constraints_map.values():
            set_variable_neighbours(var_ls)

    return Csp(name_var_map)        

csp = get_csp()
check_var(sudoku, csp)

# SOLVE function
if ac3(sudoku):
    csp.ac3()
    check_var(sudoku, csp)
    if sudoku.solved():
        output = open('output.txt', 'w')
        for n, var in enumerate(sudoku.variables):
        # for var in sudoku.variables:
            output.write(str(sudoku.domains[var][0]) + ' ' + ('\n' if (n+1)%9==0 else ''))
            # output.write(str(sudoku.domains[var][0]))
        output.close()
    else:
        assignment = {}
        for x in sudoku.variables:
            if len(sudoku.domains[x]) == 1:
                assignment[x] = sudoku.domains[x][0]

        assignment = backtrack(assignment, sudoku)
        for d in sudoku.domains:
            sudoku.domains[d] = assignment[d] if len(d) > 1 else sudoku.domains[d]

        if assignment:
            output = open('output.txt', 'w')
            for n, var in enumerate(sudoku.variables):
            # for var in sudoku.variables:
                output.write(str(sudoku.domains[var]) + ' ' + ('\n' if (n+1)%9==0 else ''))
                # output.write(str(sudoku.domains[var]))
            output.close()

        else:
            print "No solution exists"