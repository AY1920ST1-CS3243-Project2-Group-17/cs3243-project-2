import argparse
from sudoku import Sudoku
import os
from collections import deque

# Source: https://github.com/speix/sudoku-solver

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

count = 0
def backtrack(assignment, sudoku):
    global count
    print('')
    count += 1
    if count > 10:
        exit()
    if len(assignment) == len(sudoku.variables):
        return assignment
    print_sudoku(sudoku, assignment)
    var = select_unassigned_variable(assignment, sudoku)
    print(str(var) + ' selected.')
    for value in order_domain_values(sudoku, var):
        if sudoku.consistent(assignment, var, value):
            print(str(var) + ' consistent with ' + str(value))
            sudoku.assign(var, value, assignment)
            print('Assigned ' + str(value) + ' to ' + str(var))
            result = backtrack(assignment, sudoku)
            if result:
                return result
            sudoku.unassign(var, assignment)
            print('Unassigned ' + str(value) + ' to ' + var)
    return False

# Most Constrained Variable heuristic
# Pick the unassigned variable that has fewest legal values remaining.
def select_unassigned_variable(assignment, sudoku):
    unassigned = [v for v in sudoku.variables if v not in assignment]
    return min(unassigned, key=lambda var: len(sudoku.domains[var]))

# Least Constraining Value heuristic
# Prefers the value that rules out the fewest choices for the neighboring variables in the constraint graph.
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

if ac3(sudoku):
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