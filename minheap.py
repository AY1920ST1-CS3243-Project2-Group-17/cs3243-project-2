class MinHeap:
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

    def update(self, old_key, new_key=None):
        if new_key is None:
            new_key = old_key
        index = self.key_index_map[old_key][0]
        try:
            self.key_index_map[new_key].append(index)
        except KeyError:
            self.key_index_map[new_key] = [index]
        self.pq[index] = new_key
        self.shift_up(index)
        self.shift_down(index)
  
    def shift_up(self, i):
        f = self.comparator
        while (i > 1 and (f(self.pq[self.parent(i)]) > f(self.pq[i])
                          if self.minheap else f(self.pq[self.parent(i)]) < f(self.pq[i]))):
            self.pq[i], self.pq[self.parent(i)] = self.pq[self.parent(i)], self.pq[i]
            self.key_index_map[self.pq[i]][0], self.key_index_map[self.pq[self.parent(i)]][0] = (
                self.key_index_map[self.pq[self.parent(i)]][0], self.key_index_map[self.pq[i]][0])
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
                self.key_index_map[self.pq[i]][0], self.key_index_map[self.pq[max_id]][0] = (
                    self.key_index_map[self.pq[max_id]][0], self.key_index_map[self.pq[i]][0])
                i = max_id
            else:
                break
  
    def pop(self):
        extreme_v=0
        if self.BinaryHeapSize != 0:
            extreme_v = self.pq[1]    
            self.pq[1] = self.pq[self.BinaryHeapSize]
            self.BinaryHeapSize -= 1
            self.shift_down(1)
        else:
            raise IndexError('Heap is empty!')
        return extreme_v
  
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

heap = MinHeap(comparator=lambda x: x[0])
unsorted = [(1, 3), (2, 1), (1, 4), (2, 0), (1, 5), (2, -1), (2, -3), (3, -1)]
[heap.push(i) for i in unsorted]
ls = []
heap.update((2, 1), (2, 10))
heap.push((2, 10))
# heap.update(2, 11)
heap.push((3, -1))
heap.update((3, -1), (5, 11))

# heap.update(2, 12)
# heap.update(1, 13)

while heap:
    ls.append(heap.pop())
print(ls)