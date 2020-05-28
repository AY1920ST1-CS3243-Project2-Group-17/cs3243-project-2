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
        # self.is_filled = True if self.value is not None else False
        self.domain = set() if domain is None else domain
        self.pruned = [] if pruned is None else pruned
        self.neighbours = set() if neighbours is None else neighbours
        # self.discarded_domain = []

    def add_neighbour(self, other):
        self.neighbours.add(other)

    def order_domain_values(self):
        if len(self.domain) == 1:
            return list(self.domain)
        return sorted(self.domain, key=lambda val: self.conflicts(val))

    # def order_domain_values(self):
    #     # if len(self.domain) == 1:
    #     #     return self.domain
    #     return sorted(self.domain, key=lambda val: self.conflicts(val))

    # def conflicts(self, val):
    #     count = 0
    #     for n in self.neighbours:
    #         if len(n.domain) > 1 and val in n.domain:
    #             count += 1
    #     return count
    def conflicts(self, val):
        count = 0
        for n in self.neighbours:
            if len(n.domain) > 1 and val in n.domain:
                count += 1
        return count

    # def get_ordered_domain_values(self):
    #     def comparator(val):
    #         return sum(1 if val in neighbour.domain else 0 
    #                    for neighbour in self.neighbours)
    #     return sorted(self.domain, key=comparator)
    
    # def set_value_and_update_neighbours(self, val):
    #     if not self.is_assigned:
    #         self.value = val
    #         for neighbour in self.neighbours:
    #             neighbour.domain.discard(val)
    #         [self.discard_from_domain(i) for i in self.domain.copy()]
    #     # self.is_filled = True

    # def unset_value_and_update_neighbours(self, val):
    #     self.value = None
    #     for neighbour in self.neighbours:
    #         if not neighbour.is_assigned:
    #             neighbour.domain.add(val)
    #     self.restore_discarded_domain()
    #     # self.is_filled = False

    def is_assigned(self):
        return self.value is not None and self.value != 0

    # @staticmethod
    # def not_equal(var, other):
    #     # print(var.value, other.value)
    #     return (var is None or other is None 
    #             or var.value != other.value)
    
    def __repr__(self):
        return self.name
        # return str((self.name, self.value, self.domain))

# backtrack_id = 0
# count = 0
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
        # self.pruned_variables = []
        # self.variables_with_discarded_domain_vals = []
        self.show_log = True
    
    def print_log(self, str):
        if self.show_log:
            print(str)

    # def select_unassigned_var(self):
    #     sorted_unassigned_vars = sorted(self.unassigned_vars, key=lambda var: len(var.domain))
    #     min_domain_len = len(sorted_unassigned_vars[0].domain)
    #     tie_breakers = []
    #     for var in sorted_unassigned_vars:
    #         if len(var.domain) > min_domain_len:
    #             break
    #         tie_breakers.append(var)
    #     def tie_breaker_comparator(var):
    #         return sum(1 if any(i in neighbour.domain for i in var.domain) else 0 
    #                    for neighbour in var.neighbours)
    #     return min(tie_breakers, key=tie_breaker_comparator)        

    # def select_unassigned_variable(self):
    #     return min(self.unassigned_vars, key=lambda var: len(var.domain))

    # def select_unassigned_variable(self):
    #     unassigned = sorted([v for v in self.name_var_map.values() if not v.is_assigned()])
    #     return min(unassigned, key=lambda var: len(var.domain))
    def select_unassigned_variable(self):
        unassigned = sorted([v for v in self.name_var_map.values() if not v.is_assigned()], key=lambda var: var.name)
        return min(unassigned, key=lambda var: len(var.domain))

    def backtrack(self):
        # global count
        # print('')
        # count += 1
        # if count > 10:
        #     exit()
        if self.is_solved():
            return True
        # Sudoku.show_puzzle(self)
        var = self.select_unassigned_variable()
        # print(str(var) + ' selected.')
        for value in var.order_domain_values():
            if self.consistent(var, value):
                # print(str(var) + ' consistent with ' + str(value))
                self.assign(var, value)
                # print('Assigned ' + str(value) + ' to ' + str(var))
                result = self.backtrack()
                if result:
                    return result
                self.unassign(var)
                # print('Unassigned ' + str(value) + ' to ' + str(var))
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
                    var.pruned.append((n, value))

    # def forward_check(self, var, value):
    #     for n in var.neighbours:
    #         if not n.is_assigned():
    #             if value in n.domain:
    #                 n.domain.discard(value)
    #                 assert type(value) == int
    #                 var.pruned.append((n, value))

    # def assign(self, var, value):
    #     var.value = value
    #     self.forward_check(var, value)
    #     self.assigned_vars.add(var)
    #     self.unassigned_vars.remove(var)

    # def unassign(self, var):
    #     if var.is_assigned():
    #         for v in self.pruned_variables: 
    #             for i in v.pruned:
    #                 v.domain.add(i)
    #             v.pruned = set()
    #         self.pruned_variables = []
    #         var.value = None
    #         self.unassigned_vars.add(var)
    #         self.assigned_vars.remove(var)

    # def forward_check(self, var, value):
    #     for n in var.neighbours:
    #         if not n.is_assigned():
    #             if value in n.domain:
    #                 n.domain.discard(value)
    #                 var.pruned.add(value)
    #                 self.pruned_variables.append(var)
                    # self.pruned[var].append((neighbor, value))

    # def backtrack(self):
    #     if self.is_solved():
    #         return True
    #     var = self.select_unassigned_var()
    #     for value in var.get_ordered_domain_values():
    #         if all(self.satisfies_constraints_between(var, neighbour, value) 
    #                for neighbour in var.neighbours):
    #             var.set_value_and_update_neighbours(value)
    #             self.unassigned_vars.discard(var)
    #             self.assigned_vars.add(var)
    #             result = self.backtrack()
    #             if result:
    #                 return result
    #             var.unset_value_and_update_neighbours(value)
    #             self.assigned_vars.discard(var)
    #             self.unassigned_vars.add(var)
    #     return False

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
        # print(cond1)
        # cond2 = self.is_solved()
        # print(cond2)
        # cond3 = self.backtrack()
        # print(cond3)
        # return cond1 or cond2 or cond3
    
    # def satisfies_constraints_between(self, var, other, 
    #                                   new_val, new_other_val=None):
    #     if new_val is not None:
    #         temp = var.value
    #         var.value = new_val
    #     if new_other_val is not None:
    #         temp2 = other.value
    #         other.value = new_other_val
    #     is_valid = all(func(var, other) 
    #                    for func in self.constraint_funcs)
    #     if new_val is not None:
    #         var.value = temp
    #     if new_other_val is not None:
    #         other.value = temp2
    #     return is_valid

    def is_solved(self):
        return len(self.unassigned_vars) == 0

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists

    @staticmethod
    def show_puzzle(csp,  show_log=True):
        if show_log:
            puzzle = [[None for i in range(9)] for i in range(9)]
            for k, v in csp.name_var_map.items():
                puzzle[ord(k[0])-65][int(k[1])-1] = v.value if v.value is not None else 0
            for row in puzzle:
                print(' '.join(str(i) for i in row))
            # print('')

    def solve(self):
        # TODO: Write your code here

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
            for a, line in enumerate(self.puzzle):
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
        # Sudoku.show_puzzle(csp)
        print(csp.solve())
        # Sudoku.show_puzzle(csp)        

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
