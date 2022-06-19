import numpy as np
import random
from main_utilities import *
from random import choice
import math

def Initiate(size):
    row = np.arange(1,size+1)
    # creating 2 d board with the range given and satisfying the base condition (no element shall be repeated in a row or a column)
    board = np.empty((0,size),np.int32)
    row = np.array([np.arange(1,size+1)])
    for _ in range(size):
        board = np.append(board,row,axis=0)
        row = (row+1)%size
    board = np.where(board==0,size,board)
    # shuffling the rows
    np.random.shuffle(board)
    # shuffling the cols
    np.random.shuffle(board.T) 

    return board

def create_cages(board,size):
    main_cages = []
    cages = []
    caged_state = np.full((size,size),False)
    uncaged_cells_indecies = np.where(caged_state == False)
    uncaged_cells_indecies_size =  uncaged_cells_indecies[0].size
    uncaged_cells = np.empty(0,Cell)
    for j in range(uncaged_cells_indecies_size):
        temp_cell = Cell(uncaged_cells_indecies[0][j],uncaged_cells_indecies[1][j])
        # if temp_cell.x == 0 and temp_cell.y == 0: print("Hooraaay!")
        uncaged_cells = np.append(uncaged_cells, temp_cell)
    while not np.all(caged_state):
        # if uncaged_cells.size==0:
        #     break
        cage_size = random.randint(1,4)
        cage = np.empty(0,np.int32)
        cell = uncaged_cells[0]
        # print('uncaged cell x: {}, y: {}'.format(cell.x, cell.y))
        uncaged_cells = np.delete(uncaged_cells,0)
        caged_state[cell.x][cell.y] = True
        cage = np.append(cage,cell)
        adj_flag = 1
        for i in range(cage_size-1):
            #  (cell.x == tmp.x and |cell.y - tmp.y| == 1) or (cell.y == tmp.y and |cell.x-tmpx == 1|) condition for adjacent
            bool_adj = [not ((p.x == cell.x and abs(p.y - cell.y) == 1) or (p.y == cell.y and abs(p.x-cell.x) == 1)) for p in uncaged_cells]
            bool_adj_mask = np.array([bool_adj])
            adj_cells = np.ma.masked_array(uncaged_cells,bool_adj_mask)
            adj_cells = adj_cells.compressed()
            if adj_cells.size == 0:
                adj_flag = 0
                break
            # choose a random cell from the adjacents to the current cell
            cell = np.random.choice(adj_cells)
            cell_index = list(uncaged_cells).index(cell)
            caged_state[cell.x][cell.y] = True
            uncaged_cells = np.delete(uncaged_cells,cell_index)
            cage = np.append(cage,cell)
        cage_size = len(cage) 
        cages.append(cage)
        constant_cages_num = sum([item.size == 1 for item in cages])
        if cage_size == 1:
            cell = cage[0]
            # if constant_cages_num <= round(math.sqrt(size)) or adj_flag == 0:
            subcage = Cage(Operator.Constant,board[cell.x][cell.y],cage)
            # else:
            #     caged_state[cell.x][cell.y] = False
            #     uncaged_cells = np.append(uncaged_cells,cell)
            #     cages.pop()
        elif cage_size == 2:
            first = board[cage[0].x][cage[0].y]
            second = board[cage[1].x][cage[1].y]
            max1 = max(first,second)
            min1 = min(first,second)
            if max1 % min1 == 0 :
                subcage = Cage(Operator.Divide,max1/min1,cage)
            else:
                subcage = Cage(Operator.Subtract,max1-min1,cage)
        else:
            op = choice([Operator.Add,Operator.Multiply])
            values = [board[h.x][h.y] for h in cage]
            if op == Operator.Add:
                value = sum(values)
            else:
                value = math.prod(values)
            subcage = Cage(op,value,cage)
        main_cages.append(subcage)
    return main_cages

def generate(size):
    board = Initiate(size)
    final = create_cages(board,size)
    return final,board

def generate_n_boards(n,size):

    boards = []
    solutions = []
    for i in range(n):
        board,soln = generate(size)
        boards.append(board)
        solutions.append(soln)
    return boards,solutions
# cages, solution = generate(4)
# cells_count = 0
# # print(cages)
# for cage in cages:
#     # print(i.cells)
#     cells_count += len(cage.cells)
#     print('Cage operator: {} \t cage value: {} \t cage cells: {}'.format(cage.operator, cage.value, [(cell.x, cell.y) for cell in cage.cells]))
# print(cells_count)