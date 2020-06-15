# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from collections import deque
# import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Variable(object):
    def __init__(self, name, value=None, domain=None, 
                 pruned=None, neighbours=None):
        self.name = name
        self.value = value
        self.domain = set() if domain is None else domain
        self.pruned = {} if pruned is None else pruned
        self.neighbours = set() if neighbours is None else neighbours

    def order_domain_values(self):
        return sorted(self.domain, key=lambda val:\
                      sum(1 for neighbour in self.neighbours if val in neighbour.domain))

    def is_consistent(self, value):
        # determines if the given value for this variable is consistent
        for neighbour in self.neighbours:
            if neighbour.value == value:
                return False
        return True

    def forward_check(self, value):
        for neighbour in self.neighbours:
            if value in neighbour.domain:
                neighbour.domain.remove(value)
                self.pruned[neighbour] = value
    
    def __repr__(self):
        return self.name + ', ' + str(self.value)

class Csp(object):
    def __init__(self, name_var_map={}):
        self.name_var_map = name_var_map
        self.assigned_vars, self.unassigned_vars = set(), set()
        for var in self.name_var_map.values():
            self.assigned_vars.add(var) if var.value is not None else self.unassigned_vars.add(var)
        self.constraints = [(v, neighbour) for v in self.name_var_map.values()
                            for neighbour in v.neighbours]

    def select_unassigned_variable(self):
        return min(self.unassigned_vars, key=lambda var: len(var.domain))

    def backtrack(self):
        if not self.unassigned_vars:
            # no more unassigned variables, the Csp is solved
            return True
        var = self.select_unassigned_variable()

        # for each possible value in the variable's domain
        for value in var.order_domain_values():
            if var.is_consistent(value):
                self.assign(var, value)
                result = self.backtrack()
                if result:
                    return result
                self.unassign(var)
        
        # no consistent values are found; the Csp cannot be solved
        return False

    def assign(self, var, value):
        var.value = value
        var.forward_check(value)
        self.assigned_vars.add(var)
        self.unassigned_vars.remove(var)

    def unassign(self, var):
        [neighbour.domain.add(value) for (neighbour, value) in var.pruned.items()]
        var.pruned = {}
        var.value = None
        self.unassigned_vars.add(var)
        self.assigned_vars.remove(var)

    def ac3(self):
        # start = time.time()
        def revise(xi, xj):
            revised = False
            for x in list(xi.domain):
                if all(x == y for y in xj.domain):
                    xi.domain.remove(x)
                    revised = True
            return revised

        queue = deque(self.constraints)
        while queue:
            xi, xj = queue.popleft()
            revised = revise(xi, xj)
            if revised and xi.domain:
                for xk in xi.neighbours:
                    if xk != xi:      
                        queue.append((xk, xi))
            elif revised:
                return False

        return True
        # end = time.time()
        # print("Time taken: {} seconds" .format(round((end - start),2)))

        return True

    def solve(self):
        return self.ac3() and (not self.unassigned_vars or self.backtrack())

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        # TODO: Write your code here

        def set_ans(csp):
            # sets the ans attributes to the solved values
            for k, v in csp.name_var_map.items():
                self.ans[ord(k[0])-65][int(k[1])-1] = (v.value if v.value is not None 
                                                    else 0)

        def set_variable_neighbours(var_ls):
            for i in range(len(var_ls)-1):
                for j in range(i+1, len(var_ls)):
                    var_ls[i].neighbours.add(var_ls[j])
                    var_ls[j].neighbours.add(var_ls[i])       

        def get_csp():
            # returns a Csp object with the given constraints and inputs
            name_var_map = {}
            row_constraints, col_constraints, box_constraints = {}, {}, {}

            for a, line in enumerate(self.puzzle):
                for n, number in enumerate(line):
                    # creates the Variable object corresponding to the variable
                    number = number if number != 0 else None
                    row_letter, col_index = chr(a + 65), str(n + 1)
                    name = row_letter + col_index
                    var = Variable(name, number, 
                                   set(range(1, 10) if number is None else [number]))
                    
                    # sets the corresponding entry in name_var_map of the Csp
                    # to the created Variable object
                    name_var_map[name] = var
                    box_row, box_col = a // 3, n // 3
                    box_index = box_row * 3 + box_col
                    
                    # adds the row, column and box constraints
                    try:
                        row_constraints[row_letter].append(var)
                    except KeyError:
                        row_constraints[row_letter] = [var]
                    try:
                        col_constraints[col_index].append(var)
                    except KeyError:
                        col_constraints[col_index] = [var]
                    try:
                        box_constraints[box_index].append(var)
                    except KeyError:
                        box_constraints[box_index] = [var]

                    [set_variable_neighbours(var_ls) 
                     for constraints_map in [row_constraints, col_constraints, box_constraints]
                     for var_ls in constraints_map.values()]

            return Csp(name_var_map)
        
        csp = get_csp()
        csp.solve()
        set_ans(csp)

        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
