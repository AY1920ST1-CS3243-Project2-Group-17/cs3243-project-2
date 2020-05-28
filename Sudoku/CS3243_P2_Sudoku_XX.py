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
        self.is_filled = True if self.value is not None else False
        self.domain = set() if domain is None else domain
        self.neighbours = set() if neighbours is None else neighbours
        self.discarded_domain = []

    def add_neighbour(self, other):
        self.neighbours.add(other)

    def get_ordered_domain_values(self):
        def comparator(val):
            return sum(1 if val in neighbour.domain else 0 
                       for neighbour in self.neighbours)
        return sorted(self.domain, key=comparator)

    def update_init_domain(self):
        if self.value is not None:
            self.domain = set()
        else:
            [self.domain.discard(neighbour.value) 
             for neighbour in self.neighbours]
    
    def set_value_and_update_neighbours(self, val):
        if not self.is_assigned:
            self.value = val
            for neighbour in self.neighbours:
                neighbour.domain.discard(val)
            [self.discard_from_domain(i) for i in self.domain.copy()]
        # self.is_filled = True

    def unset_value_and_update_neighbours(self, val):
        self.value = None
        for neighbour in self.neighbours:
            if not neighbour.is_assigned:
                neighbour.domain.add(val)
        self.restore_discarded_domain()
        # self.is_filled = False

    def is_assigned(self):
        return self.value is not None

    # def discard_from_domain(self, val):
    #     self.domain.discard(val)
    #     self.discarded_domain.append(val)
    
    # def clear_discarded_domain(self):
    #     self.discarded_domain = []

    # def restore_discarded_domain(self):
    #     for val in self.discarded_domain:
    #         self.domain.add(val)
    #     self.clear_discarded_domain()

    @staticmethod
    def not_equal(var, other):
        # print(var.value, other.value)
        return (var is None or other is None 
                or var.value != other.value)
    
    def __repr__(self):
        return str((self.name, self.value, self.domain))

backtrack_id = 0
class Csp(object):
    def __init__(self, name_var_map={}, constraint_funcs=[]):
        self.name_var_map = name_var_map
        self.assigned_vars = set()
        self.unassigned_vars = set()
        [(self.assigned_vars.add(var) 
          if var.is_assigned() else self.unassigned_vars.add(var))
         for var in self.name_var_map.values()]
        self.init_assigned = len(self.assigned_vars)
        self.constraint_funcs = constraint_funcs
        self.variables_with_discarded_domain_vals = []
        self.show_log = False
    
    def print_log(self, str):
        if self.show_log:
            print(str)

    def select_unassigned_var(self):
        sorted_unassigned_vars = sorted(self.unassigned_vars, key=lambda var: len(var.domain))
        min_domain_len = len(sorted_unassigned_vars[0].domain)
        tie_breakers = []
        for var in sorted_unassigned_vars:
            if len(var.domain) > min_domain_len:
                break
            tie_breakers.append(var)
        def tie_breaker_comparator(var):
            return sum(1 if any(i in neighbour.domain for i in var.domain) else 0 
                       for neighbour in var.neighbours)
        return min(tie_breakers, key=tie_breaker_comparator)        

    def backtrack(self):
        if self.is_solved():
            return True
        var = self.select_unassigned_var()
        for value in var.get_ordered_domain_values():
            if all(self.satisfies_constraints_between(var, neighbour, value) 
                   for neighbour in var.neighbours):
                var.set_value_and_update_neighbours(value)
                self.unassigned_vars.discard(var)
                self.assigned_vars.add(var)
                result = self.backtrack()
                if result:
                    return result
                var.unset_value_and_update_neighbours(value)
                self.assigned_vars.discard(var)
                self.unassigned_vars.add(var)
        return False

    def ac3(self):
        def revise(xi, xj):
            revised = False
            for x in xi.domain.copy():
                if not any (self.satisfies_constraints_between(xi, xj, x, y) 
                            for y in xj.domain):
                    xi.domain.discard(x)
                    revised = True
            return revised

        queue = deque()
        for v in self.name_var_map.values():
            for neighbour in v.neighbours:
                queue.append((v, neighbour))
            
        while queue:
            xi, xj = queue.popleft()
            if revise(xi, xj):
                if not xi.domain:
                    return False
                for xk in xi.neighbours:
                    if xk != xi:
                        queue.append((xk, xi))
        return True

    def solve(self):
        return self.ac3() or self.is_solved() or self.backtrack()

    # for d in sudoku.domains:
    #     sudoku.domains[d] = assignment[d] if len(d) > 1 else sudoku.domains[d]
    # if assignment:
    #     output = open('output.txt', 'w')
    #     for n, var in enumerate(sudoku.variables):
    #     # for var in sudoku.variables:
    #         output.write(str(sudoku.domains[var]) + ' ' + ('\n' if (n+1)%9==0 else ''))
    #         # output.write(str(sudoku.domains[var]))
    #     output.close()
    # else:
    #     print "No solution exists"
    # def backtrack(self, caller=backtrack_id):
    #     global backtrack_id
    #     backtrack_id += 1
    #     # if backtrack_id == 200000:
    #     #     exit()
    #     curr_id = backtrack_id
    #     if backtrack_id % 10000 == 0:
    #         print(backtrack_id)
    #     if len(self.assigned_vars) - self.init_assigned >= 50:
    #         print(str(len(self.assigned_vars) - self.init_assigned) + ' variables assigned. ' 
    #             + str(len(self.unassigned_vars)) + ' remaining.')
    #         Sudoku.show_puzzle(self, show_log=True)
    #     self.print_log('')
    #     self.print_log('ID' + str(curr_id) + ' called by ' + str(caller))
    #     if self.is_solved():
    #         return True
    #     var = self.select_unassigned_var()
    #     self.print_log('ID' + str(curr_id) + ': ' + str(var) + ' selected with ordered domain ' + str(var.get_ordered_domain_values()))
    #     for value in var.get_ordered_domain_values():
    #         # self.print_log('Trying ' + str(value) + ' for ' + str(var))
    #         if all(self.satisfies_constraints_between(var, neighbour, value) 
    #                for neighbour in var.neighbours):
    #             self.print_log('ID' + str(curr_id) + ': ' + str(value) + ' satisfies constraints for ' + str(var))
    #             self.print_log('ID' + str(curr_id) + ': ' + str(value) + ' assigned to ' + str(var))
    #             self.print_log('ID' + str(curr_id) + ': Checking Arc consistency for ' + str(var))
    #             var.set_value_and_update_neighbours(value)
    #             self.unassigned_vars.discard(var)
    #             self.assigned_vars.add(var)
    #             is_arc_consistent = self.ac_3(var)
    #             if is_arc_consistent:
    #                 self.confirm_inference()
    #                 self.print_log('ID' + str(curr_id) + ': Arc consistency maintained for ' + str(var) + ' with value ' + str(value))
    #                 self.print_log('ID' + str(curr_id) + ' calling ' + str(backtrack_id + 1))
    #                 result = self.backtrack(curr_id)
    #                 if result != False:
    #                     return result
    #                 else:
    #                     self.print_log('ID' + str(curr_id) + ' received failed result, backtracking...')
    #             else:
    #                 self.print_log('ID' + str(curr_id) + ': ' + 'Arc Consistency not maintained for ' + str(var) + ' with value ' + str(value))
    #             var.unset_value_and_update_neighbours(value)
    #             if not is_arc_consistent:
    #                 var.domain.discard(value)
    #             # else:
    #             #     self.undo_inference()
    #             self.assigned_vars.discard(var)
    #             self.unassigned_vars.add(var)
    #             self.print_log('ID' + str(curr_id) + ': ' + str(value) + ' unassigned from ' + str(var))
    #         else:
    #             self.print_log('ID' + str(curr_id) + ': ' + str(value) + ' does not satisfy constraints for ' + str(var))
    #     return False
    
    def satisfies_constraints_between(self, var, other, 
                                      new_val, new_other_val=None):
        if new_val is not None:
            temp = var.value
            var.value = new_val
        if new_other_val is not None:
            temp2 = other.value
            other.value = new_other_val
        is_valid = all(func(var, other) 
                       for func in self.constraint_funcs)
        if new_val is not None:
            var.value = temp
        if new_other_val is not None:
            other.value = temp2
        return is_valid

    # def undo_inference(self):
    #     for var in self.variables_with_discarded_domain_vals:
    #         var.restore_discarded_domain()
    #     self.variables_with_discarded_domain_vals = []

    # def confirm_inference(self):
    #     for var in self.variables_with_discarded_domain_vals:
    #         var.clear_discarded_domain()
    #     self.variables_with_discarded_domain_vals = []

    # def ac_3(self, var):
    #     queue = deque()
    #     for neighbour in var.neighbours:
    #         queue.append((var, neighbour))
    #         queue.append((neighbour, var))
    #     # print('Initial AC3 Queue: ' + str(queue))
    #     # variables_with_discarded_domain_vals = []

    #     def revise(xi, xj):
    #         revised = False
                
    #         for x in xi.domain.copy():
    #             # if xi.name == 'I9' or xj.name == 'I9':
    #             if not any(self.satisfies_constraints_between(xi, xj, x, y) 
    #                        for y in (xj.domain if not len(xj.domain) == 0 else [xj.value])):
    #                 print(str(x) + ' discarded from xi: ' + str(xi) + ' when compared to xj: ' +  str(xj))
    #                 xi.discard_from_domain(x)
    #                 self.variables_with_discarded_domain_vals.append(xi)
    #                 revised = True
    #             elif len(xj.domain) != 0:
    #                 print('Arc consistency maintained between xi: ' + str(xi) + ' with value ' + str(x)
    #                 + ' and xj: ' +  str(xj))
    #         return revised

    #     while queue:
    #         xi, xj = queue.popleft()
    #         if revise(xi, xj):
    #             if not xi.is_filled and len(xi.domain) == 0:
    #                 print(str(xi) + ' failed Arc Consistency test.')
    #                 return False
    #             for xk in xi.neighbours:
    #                 if xk is not xj:
    #                     queue.append((xk, xi))
    #     return True

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
            print('')

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

            for constraints_map in [row_constraints, col_constraints, box_constraints]:
                for var_ls in constraints_map.values():
                    set_variable_neighbours(var_ls)
            [var.update_init_domain() for var in name_var_map.values()]

            return Csp(name_var_map, [Variable.not_equal])
        
        csp = get_csp()
        Sudoku.show_puzzle(csp)
        # print('\n'.join([str((v, v.domain)) for k, v in sorted(csp.name_var_map.items())]))
        print(csp.solve())
        Sudoku.show_puzzle(csp)

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
