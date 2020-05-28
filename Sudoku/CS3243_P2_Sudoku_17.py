import sys
import copy
import inspect
from collections import deque

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
        self.backup_domain = set()

    def order_domain_values(self):
        return sorted(self.domain, key=lambda val:\
                      sum(1 if val in neighbour.domain else 0 
                          for neighbour in self.neighbours))

    def is_consistent(self, value):
        for neighbour in self.neighbours:
            if neighbour.value == value:
                return False
        return True

    def forward_check(self, value):
        for neighbour in self.neighbours:
            if value in neighbour.domain:
                neighbour.domain.discard(value)
                self.pruned[neighbour] = value
   
    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name + ', ' + str(self.value)

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
            return True
        var = self.select_unassigned_variable()
        init_var = var
        for value in var.order_domain_values():
            if var.value is None and var.is_consistent(value):
                curr_domain = var.domain.copy()
                assert var not in self.assigned_vars
                assert var in self.unassigned_vars
                self.assign(var, value)
                assert var in self.assigned_vars
                inferred_as_possible, original_var_domain_map = self.ac3(var)
                if inferred_as_possible:
                    for neighbour in var.neighbours:
                        if value in neighbour.domain:
                            assert False
                    result = self.backtrack()
                    if result:
                        return result
                for var2, domain in original_var_domain_map.items():
                    var2.domain = domain
                assert var is init_var
                assert var not in self.unassigned_vars
                assert var in self.assigned_vars
                self.unassign(var)
                assert var in self.unassigned_vars
                assert var.domain == curr_domain
        return False

    def assign(self, var, value):
        var.value = value
        var.backup_domain = var.domain
        var.domain = set([value])
        # var.forward_check(value)
        self.assigned_vars.add(var)
        self.unassigned_vars.remove(var)

    def unassign(self, var):
        # [neighbour.domain.add(value) for (neighbour, value) in var.pruned.items()]
        # var.pruned = {}
        var.value = None
        var.domain = var.backup_domain
        var.backup_domain = set()
        self.unassigned_vars.add(var)
        self.assigned_vars.remove(var)

    def ac3(self, var=None):
        original_var_domain_map = {}
        def revise(xi, xj, discarded_var_domain_map):
            revised = False
            updated_domain = set()
            for x in xi.domain:
                if any(x != y for y in xj.domain):
                    updated_domain.add(x)
                else:
                    revised = True
            if revised:
                try:
                    original_var_domain_map[xi]
                except KeyError:
                    original_var_domain_map[xi] = xi.domain
                xi.domain = updated_domain
            return revised, original_var_domain_map

        queue = deque()
        # queue = deque(self.constraints)
        for var in (self.unassigned_vars if var is None else [var]):
            for neighbour in var.neighbours:
                queue.append((var, neighbour))
                queue.append((neighbour, var))    

        while queue:
            xi, xj = queue.popleft()
            curr = xi.domain.copy()
            revised, original_var_domain_map = revise(xi, xj, original_var_domain_map)
            if revised:
                if not xi.domain:
                    return False, original_var_domain_map
                [queue.append((xk, xi)) for xk in xi.neighbours 
                 if xk != xi]
        return True, original_var_domain_map

    def solve(self):
        inferred_as_possible, original_domain_map = self.ac3()
        return inferred_as_possible and (not self.unassigned_vars or self.backtrack())

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def get_puzzle(self, csp):
        for k, v in csp.name_var_map.items():
            self.ans[ord(k[0])-65][int(k[1])-1] = (v.value if v.value is not None 
                                                   else 0)
        for row in self.ans:
            print(' '.join(str(i) for i in row))
        return self.ans

    def solve(self):
        # TODO: Write your code here

        def set_variable_neighbours(var_ls):
            for i in range(len(var_ls)-1):
                for j in range(i+1, len(var_ls)):
                    var_ls[i].neighbours.add(var_ls[j])
                    var_ls[j].neighbours.add(var_ls[i])

        def get_csp():
            name_var_map = {}
            row_constraints, col_constraints, box_constraints = {}, {}, {}
            for a, line in enumerate(self.puzzle):
                for n, number in enumerate(line):
                    number = number if number != 0 else None
                    row_letter, col_index = chr(a + 65), str(n + 1)
                    name = row_letter + col_index
                    var = Variable(name, number, 
                                   set(range(1, 10) if number is None else [number]))
                    name_var_map[name] = var
                    box_row, box_col = a // 3, n // 3
                    box_index = box_row * 3 + box_col
                    
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
        return self.get_puzzle(csp)

        # self.ans is a list of lists
        # return self.ans

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
