import argparse
from sudoku import Sudoku

def ac3(sudoku):
    def revise(sudoku, xi, xj):
        revised = False
        for x in sudoku.domains[xi]:
            if not any(x != y for y in sudoku.domains[xj]):
                sudoku.domains[xi].remove(x)
                revised = True
        return revised

    queue = list(sudoku.constraints)
    while queue:
        xi, xj = queue.pop(0)
        if revise(sudoku, xi, xj):
            if not sudoku.domains[xi]:
                return False    
            [queue.append([xk, xi]) for xk in sudoku.neighbors[xi] if xk != xi]
    return True

def backtrack(assignment, sudoku):
    if len(assignment) == len(sudoku.variables):
        return assignment
    var = select_unassigned_variable(assignment, sudoku)
    for value in order_domain_values(sudoku, var):
        if sudoku.consistent(assignment, var, value):
            assignment[var] = value
            sudoku.forward_check(var, value, assignment)
            result = backtrack(assignment, sudoku)
            if result:
                return result
            sudoku.unassign(var, assignment)
    return False

def select_unassigned_variable(assignment, sudoku):
    unassigned = [v for v in sudoku.variables if v not in assignment]
    return min(unassigned, key=lambda var: len(sudoku.domains[var]))

def order_domain_values(sudoku, var):
    if len(sudoku.domains[var]) == 1:
        return sudoku.domains[var]
    return sorted(sudoku.domains[var], key=lambda val: sudoku.conflicts(sudoku, var, val))


# print('hello')
parser = argparse.ArgumentParser()
parser.add_argument('board')
args = parser.parse_args()

sudoku = Sudoku(list(args.board))

if ac3(sudoku):
    if sudoku.solved():
        output = open('output.txt', 'w')
        for var in sudoku.variables:
            output.write(str(sudoku.domains[var][0]))
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
            for var in sudoku.variables:
                output.write(str(sudoku.domains[var]))
            output.close()