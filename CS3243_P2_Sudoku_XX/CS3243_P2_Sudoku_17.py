# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from collections import deque
import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Variable(object):
    def __init__(self, var_name, value=None, domain=None, 
                 pruned=None, neighbours=None):
        self.var_name = var_name
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
                neighbour.domain.discard(value)
                self.pruned[neighbour] = value
    
    def __repr__(self):
        return self.var_name + ', ' + str(self.value)

class Csp(object):
    def __init__(self, name_var_map={}):
        self.name_var_map = name_var_map
        self.assigned_vars, self.unassigned_vars = set(), set()
        [(self.assigned_vars.add(var) 
          if var.value is not None else self.unassigned_vars.add(var))
         for var in self.name_var_map.values()]
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
            if revise(xi, xj):
                if not xi.domain:
                    return False
                [queue.append((xk, xi)) for xk in xi.neighbours 
                 if xk != xi]

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

        var_names = []
        var_nums = {}
        var_vals = {}
        var_neighbours = {}
        var_domains = {}
        var_pruned = {}
        
        def set_variable_neighbours(var_ls):
            for i in range(len(var_ls)-1):
                for j in range(i+1, len(var_ls)):
                    var_neighbours[var_ls[i]].add(var_ls[j])
                    var_neighbours[var_ls[j]].add(var_ls[i])  

        row_constraints, col_constraints, box_constraints = {}, {}, {}
        assigned_vars, unassigned_vars = set(), set()
        [(assigned_vars.add(var_name) if var_vals[var_name] is not None else unassigned_vars.add(var_name))
        for var_name in var_names]

        for a, line in enumerate(self.puzzle):
            for n, number in enumerate(line):
                # creates the Variable object corresponding to the variable
                number = number if number != 0 else None
                row_letter, col_index = chr(a + 65), str(n + 1)
                var_name = row_letter + col_index
                var_names.append(var_name)
                var_vals[var_name] = set(range(1, 10) if number is None else [number]) 
                var_domains[var_name] = set()
                var_pruned[var_name] = {}
                var_neighbours[var_name] = set()

                # sets the corresponding entry in name_var_map of the Csp
                # to the created Variable object
                box_row, box_col = a // 3, n // 3
                box_index = box_row * 3 + box_col
                
                # adds the row, column and box constraints
                try:
                    row_constraints[row_letter].append(var_name)
                except KeyError:
                    row_constraints[row_letter] = [var_name]
                try:
                    col_constraints[col_index].append(var_name)
                except KeyError:
                    col_constraints[col_index] = [var_name]
                try:
                    box_constraints[box_index].append(var_name)
                except KeyError:
                    box_constraints[box_index] = [var_name]

                [set_variable_neighbours(var_ls) 
                 for constraints_map in [row_constraints, col_constraints, box_constraints]
                 for var_ls in constraints_map.values()]
        
        if 1 == 1:
            pass

        def backtrack():
            if not unassigned_vars:
                # no more unassigned variables, the Csp is solved
                return True
            var_name = min(unassigned_vars, key=lambda var_name: len(var_domains[var_name]))
            # for each possible value in the variable's domain
            ordered_domain_values = sorted(var_domains[var_name], 
                key=lambda val: sum(1 for neighbour in var_neighbours[var_name] 
                                    if val in var_domains[neighbour]))
            for value in ordered_domain_values:
                if not any(var_vals[neighbour] == value for neighbour in var_neighbours[var_name]):
                    var_vals[var_name] = value
                    for neighbour in var_neighbours[var_name]:
                        if value in var_domains[neighbour]:
                            var_domains[neighbour].discard(value)
                            var_pruned[var_name][neighbour] = value
                    assigned_vars.add(var_name)
                    unassigned_vars.remove(var_name)
                    result = self.backtrack()
                    if result:
                        return result
                    [var_domains[neighbour].add(value) for (neighbour, value) in var_pruned[var_name].items()]
                    var_pruned[var_name] = {}
                    var_value[var_name] = None
                    unassigned_vars.add(var_name)
                    assigned_vars.remove(var_name)

            # no consistent values are found; the Csp cannot be solved
            return False

        def ac3():
            # start = time.time()
            def revise(xi, xj):
                revised = False
                for x in list(var_domains[xi]):
                    if all(x == y for y in var_domains[xj]):
                        var_domains[xi].remove(x)
                        revised = True
                return revised

            queue = set([(var_name, neighbour) for var_name in var_names
                          for neighbour in var_neighbours[var_name]])
            while queue:
                xi, xj = queue.pop()
                if revise(xi, xj):
                    if not var_domains[xi]:
                        return False
                    [queue.add((xk, xi)) for xk in var_neighbours[xi]
                     if xk != xi]
            # end = time.time()
            # print("Time taken: {} seconds" .format(round((end - start),2)))
            return True

        ac3() and (not unassigned_vars or backtrack())
        for var_name in var_names:
            self.ans[ord(var_name[0])-65][int(var_name[1])-1] = (var_vals[var_name]\
                if var_vals[var_name] is not None else 0)

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
