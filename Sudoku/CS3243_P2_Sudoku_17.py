import sys
import copy
import inspect
from collections import deque

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class PriorityQueue(object):
    def __init__(self, ls=None, minheap=True, 
                 comparator=lambda x: x):
        self.pq = [0]
        self.BinaryHeapSize = 0
        self.key_index_map = {}
        self.minheap = minheap
        self.comparator = comparator
        if ls is not None:
            self.create_heap(ls)

    def as_sorted_list(self):
        copy = self.copy()
        ls = []
        while copy:
            ls.append(copy.pop())
        return ls

    def copy(self):
        newheap = MinHeap()
        newheap.pq = self.pq[:]
        newheap.BinaryHeapSize = self.BinaryHeapSize
        newheap.key_index_map = {k: v for k, v in self.key_index_map.items()}
        return newheap

    def parent(self, i):
        return i//2
  
    def left(self, i):
        return 2*i
  
    def right(self, i):
        return 2*i + 1

    def update(self, old_key, new_key):
        index = self.key_index_map[old_key][-1]
        try:
            self.key_index_map[new_key].append(index)
        except KeyError:
            self.key_index_map[new_key] = [index]
        self.pq[index] = new_key
        try:
            self.key_index_map[old_key].pop()
        except IndexError:
            del self.key_index_map[old_key]
        self.shift_up(index)
        self.shift_down(index)
    
    def remove(self, key):
        index = self.key_index_map[key][-1]
        self.key_index_map[self.pq[-1]][-1] = index
        try:
            self.key_index_map[key].pop()
        except IndexError:
            del self.key_index_map[key]
        self.pq[index], self.pq[-1] = self.pq[-1], self.pq[index]   
        self.pq.pop()
        self.BinaryHeapSize -= 1
        if index < self.BinaryHeapSize:
            self.shift_up(index)
            self.shift_down(index)
  
    def shift_up(self, i):
        f = self.comparator
        while (i > 1 and (f(self.pq[self.parent(i)]) > f(self.pq[i])
                          if self.minheap else f(self.pq[self.parent(i)]) < f(self.pq[i]))):
            self.pq[i], self.pq[self.parent(i)] = self.pq[self.parent(i)], self.pq[i]
            self.key_index_map[self.pq[i]][-1], self.key_index_map[self.pq[self.parent(i)]][-1] = (
                self.key_index_map[self.pq[self.parent(i)]][-1], self.key_index_map[self.pq[i]][-1])
            i = self.parent(i)

    def push(self, key):
        self.BinaryHeapSize += 1
        if self.BinaryHeapSize >= len(self.pq):
            self.pq.append(key)
        else:
            self.pq[self.BinaryHeapSize] = key
        try:
            self.key_index_map[key].append(self.BinaryHeapSize)
        except KeyError:
            self.key_index_map[key] = [self.BinaryHeapSize]
        self.shift_up(self.BinaryHeapSize)

    def shift_down(self, i):
        f = self.comparator
        while i <= self.BinaryHeapSize:
            extreme_v = self.pq[i]
            max_id = i

            if (self.left(i) <= self.BinaryHeapSize and (f(extreme_v) > f(self.pq[self.left(i)]) 
                                                         if self.minheap else 
                                                         f(extreme_v) < f(self.pq[self.left(i)]))): 
                extreme_v = self.pq[self.left(i)]
                max_id = self.left(i)

            if (self.right(i) <= self.BinaryHeapSize and (f(extreme_v) > f(self.pq[self.right(i)])
                                                          if self.minheap else 
                                                          f(extreme_v) < f(self.pq[self.right(i)]))):
                extreme_v = self.pq[self.right(i)]
                max_id = self.right(i)
        
            if max_id != i:
                self.pq[i], self.pq[max_id] = self.pq[max_id], self.pq[i]
                self.key_index_map[self.pq[i]][-1], self.key_index_map[self.pq[max_id]][-1] = (
                    self.key_index_map[self.pq[max_id]][-1], self.key_index_map[self.pq[i]][-1])
                i = max_id
            else:
                break
  
    def pop(self):
        if self.BinaryHeapSize != 0:
            extreme_v = self.pq[1]
            try:
                self.key_index_map[extreme_v].pop()
            except IndexError:
                del self.key_index_map[extreme_v]
            self.pq[1] = self.pq[self.BinaryHeapSize]
            self.BinaryHeapSize -= 1
            self.shift_down(1)
        else:
            raise IndexError('Heap is empty!')
        return extreme_v

    def peek(self):
        return self.pq[1]

    def create_heap(self, ls):
        self.BinaryHeapSize = len(ls)
        self.pq = [0]
        [self.pq.append(ls[i-1]) for i in range(1, self.BinaryHeapSize+1)]
        [self.shift_down(i) for i in range(self.parent(self.BinaryHeapSize), 0, -1)]

    def heap_sort(self, ls):
        self.create_heap(ls)
        n = len(ls)
        for i in range(1, n+1):
            self.pq[n-i+1] = self.pop()
        return self.pq

    def is_heapified(self):
        copy = self.copy()
        sorted_ls = self.as_sorted_list()
        return sorted_ls == sorted(sorted_ls)

    def __len__(self):
        return self.BinaryHeapSize
  
    def __nonzero__(self):
        return self.BinaryHeapSize != 0

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
    
    def __repr__(self):
        return self.name + ', ' + str(self.value)

class Csp(object):
    def __init__(self, name_var_map={}):
        self.name_var_map = name_var_map
        self.assigned_vars = set()
        self.unassigned_vars = PriorityQueue(comparator=lambda var: len(var.domain))
        [(self.assigned_vars.add(var) 
          if var.value is not None else self.unassigned_vars.push(var))
         for var in self.name_var_map.values()]
        self.constraints = [(v, neighbour) for v in self.name_var_map.values()
                            for neighbour in v.neighbours]

    def select_unassigned_variable(self):
        return self.unassigned_vars.peek()

    def backtrack(self):
        if not self.unassigned_vars:
            return True
        var = self.select_unassigned_variable()
        for value in var.order_domain_values():
            if var.is_consistent(value):
                self.assign(var, value)
                result = self.backtrack()
                if result:
                    return result
                self.unassign(var)
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
        self.unassigned_vars.push(var)
        self.assigned_vars.remove(var)

    def ac3(self):
        def revise(xi, xj):
            revised = False
            updated_domain = set()
            for x in xi.domain:
                if any(x != y for y in xj.domain):
                    updated_domain.add(x)
                else:
                    revised = True
            if revised:
                xi.domain = updated_domain
            return revised

        queue = deque(self.constraints)
        while queue:
            xi, xj = queue.popleft()
            if revise(xi, xj):
                if not xi.domain:
                    return False
                [queue.append((xk, xi)) for xk in xi.neighbours 
                 if xk != xi]
        return True

    def solve(self):
        return self.ac3() and (not self.unassigned_vars or self.backtrack())

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
