import os
NUM_OF_VARS = 81
assignment = [None]*NUM_OF_VARS
for puzzle_num in range(1,5):
    fname = 'public_tests_p2_sudoku/input' + str(puzzle_num) + '.txt'
    with open(fname) as f:
        content = f.readlines()

    content = [x.strip() for x in content] 
    for i in range(0,len(content)):
        line = content[i]
        variables = line.split(' ')
        for j in range(0,len(variables)):
            value = variables[j]
            assignment[9*i+j] = int(value)
            # assignment[9*i+j] = int(value) if value is not '0' else None
    directory = 'modified_outputs'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file = open(directory + '/input' + str(puzzle_num) + '.txt', 'w+')
    file.write(''.join(str(i) for i in assignment))