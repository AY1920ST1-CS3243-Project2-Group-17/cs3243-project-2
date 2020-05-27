import sys
import copy
import inspect
from collections import deque

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Variable(object):
    def __init__(self, name, value=None, domain=None, 
                 neighbours=None):
        self.name = name
        self.value = value
        self.domain = set() if domain is None else domain
        self.neighbours = set() if neighbours is None else neighbours
        self.discarded_domain = []

    def add_neighbour(self, other):
        self.neighbours.add(other)
        # if self.name == 'A1':
        #     print(self, other, self.neighbours, len(self.neighbours))
        # elif other.name == 'A1':
        #     print(other, self, self.neighbours)

    def get_ordered_domain_values(self):
        def comparator(val):
            return sum(1 if val in neighbour.domain else 0 
                       for neighbour in self.neighbours)
        return sorted(self.domain, key=comparator)

    def update_domain(self):
        if self.value is not None:
            self.domain = set()
        else:
            [self.domain.discard(neighbour.value) 
             for neighbour in self.neighbours]
    
    def is_assigned(self):
        return self.value is not None

    def discard_from_domain(self, val):
        self.domain.discard(val)
        self.discarded_domain.append(val)
    
    def clear_discarded_domain(self):
        self.discarded_domain = []

    def restore_discarded_domain(self):
        for val in self.discarded_domain:
            self.domain.add(val)
        self.clear_discarded_domain()

    @staticmethod
    def not_equal(var, other):
        return (var is not None and other is not None 
                and var.value != other.value)

    # def __eq__(self, other):
    #     return self.value == other.value

    # def __hash__(self):
    #     return hash(self.name)
    
    def __repr__(self):
        return str((self.name, self.value))

# class AllDiffChecker(object):
#     def __init__(self, var):
#         self.var = var


# class AllDiffChecker(object):
#     def __init__(self, var_ls):
#         self.var_ls = var_ls
#     def check(self):
#         # print(self.var_ls)
#         # print([var.name for var in self.var_ls])
#         for i in range(len(self.var_ls)-1):
#             for j in range(i+1, len(self.var_ls)):
#                 if (self.var_ls[i].value is not None 
#                     and self.var_ls[j].value is not None
#                     and self.var_ls[i].value == self.var_ls[j].value):
#                     return False
#         return True

class Csp(object):
    def __init__(self, name_var_map={}, constraint_funcs=[]):
        self.name_var_map = name_var_map
        self.assigned_vars = set()
        self.unassigned_vars = set()
        [(self.assigned_vars.add(var) 
          if var.is_assigned() else self.unassigned_vars.add(var))
         for var in self.name_var_map.values()]
        self.constraint_funcs = constraint_funcs
    
    def select_unassigned_var(self):
        return min(self.unassigned_vars, key=lambda var: len(var.domain))

    def backtrack(self):
        if self.is_solved():
            return True
        var = self.select_unassigned_var()
        for value in var.get_ordered_domain_values():
            if all(self.satisfies_constraints_between(var, neighbour) 
                   for neighbour in var.neighbours):
                if not self.ac_3(var, value):
                    var.value = value
                    self.unassigned_vars.discard(var)
                    self.assigned_vars.add(var)
                    return self.backtrack()
        return False
    
    def satisfies_constraints_between(self, var, other, 
                                      new_val, new_other_val=None):
        if new_val is not None:
            temp = var.val
            var.val = new_val
        if new_other_val is not None:
            temp2 = other.val
            other.val = new_other_val
        is_valid = all(func(var, other) 
                       for func in self.constraint_funcs)
        if new_val is not None:
            var.val = temp
        if new_other_val is not None:
            other.val = temp2
        return is_valid

    def ac_3(self, var, val):
        queue = deque()
        for neighbour in var.neighbours:
            queue.add((var, neighbour))
            queue.add((neighbour, var))
        variables_with_discarded_domain_vals = []

        def revise(xi, xj):
            revised = False
            for x in xi.domain:
                if not any(self.satisfies_constraints_between(xi, xj, x, y) 
                           for y in xj.domain):
                    xi.domain.discard(x)
                    variables_with_discarded_domain_vals.append(xi)
                    revised = True
            return revised

        while queue:
            xi, xj = queue.pop()
            if revise(xi, xj):
                if len(xi.domain) == 0:
                    for var in variables_with_discarded_domain_vals:
                        var.restore_discarded_domain()
                    return False
                for xk in xi.neighbours:
                    if xk is not xj:
                        queue.add((xk, xi))
        for var in variables_with_discarded_domain_vals:
            var.clear_discarded_domain()
        return True


    def is_solved(self):
        return len(self.unassigned_vars) == 0

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    def solve(self):
        # TODO: Write your code here

        def set_variable_neighbours(var_ls):
            for i in range(len(var_ls)-1):
                for j in range(i+1, len(var_ls)):
                    # print(type(var_ls[i]))
                    var_ls[i].add_neighbour(var_ls[j])
                    var_ls[j].add_neighbour(var_ls[i])

        def show_puzzle(csp):
            puzzle = [[None for i in range(9)] for i in range(9)]
            for k, v in csp.name_var_map.items():
                puzzle[ord(k[0])-65][int(k[1])-1] = v.value if v.value is not None else 0
            for row in puzzle:
                print(' '.join(str(i) for i in row))

        def get_csp():
            name_var_map = {}
            row_constraints = {}
            col_constraints = {}
            box_constraints = {}
            for a, line in enumerate(self.puzzle):
                for n, number in enumerate(line):
                    number = number if number != 0 else None
                    row_letter = chr(a + 65)
                    col_index = str(n + 1)
                    name = row_letter + col_index
                    var = Variable(name, number, set(range(1, 10)))
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
            # print(sorted(name_var_map.items()))

            # constraint_funcs = []
            for constraints_map in [row_constraints, col_constraints, box_constraints]:
                for var_ls in constraints_map.values():
                    # constraint_funcs.append(AllDiffChecker(var_ls).check)
                    set_variable_neighbours(var_ls)
            # print(sorted(name_var_map['A1'].neighbours))
            [var.update_domain() for var in name_var_map.values()]
            # for k, var in sorted(name_var_map.items()):
                # print(var, sorted(var.neighbours))
                # print(var, var.domain, var.get_possible_values())
                # print(var, var.domain)
                # print('')
            # print([func() for func in constraint_funcs])
            # name_var_map['A9'].value = 8
            # print([func() for func in constraint_funcs])

            return Csp(name_var_map, [Variable.not_equal])
        
        # print(self.puzzle)
        csp = get_csp()
        # print(csp.name_var_map)
        show_puzzle(csp)

        # print(box_constraints)
        # print(row_constraints)
        # print(col_constraints)

        # print(sorted(csp.name_var_map.items()))
        # print([inspect.getsource(func) for func in csp.constraint_funcs])
        # def backtracking_search(csp):
        #     return backtrack([], csp)
        # def backtrack(assignment, csp):
        #     if assignment.is_complete():
        #         return assignment
        #     var = csp.select_unassigned_var()
        #     for value in order_domain_values(var, assignment, csp):
        #         if val.is_consistent_with(assignment):
        #             assignment.add(var, value)
        #             inferences = inference(csp, var, value)
        #             if inferences != False:
        #                 assignment.add(inferences)
        #                 result = backtrack(assignment, csp)
        #                 if result != False:
        #                     return result
        #      return False

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
