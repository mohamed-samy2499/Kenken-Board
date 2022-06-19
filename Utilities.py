from datetime import datetime
# import enum
# from math import fabs
import numpy as np
from Generate import generate, generate_n_boards
from main_utilities import *
import copy
# import timeit


class KenKenBoard:
    def __init__(self, size, cages):
        self.size = size
        self.cages = cages
        self.mRowHash = np.full((self.size, self.size), False)
        self.mColHash = np.full((self.size, self.size), False)
        self.mstate = np.full((self.size, self.size), 0)
        self.mDomain = [[[0] for i in range(self.size)] for j in range(self.size)]
        self.queue = []
    
    def validate_cage_constraint(self, cage): 
        expansion_of_cage = list()
        for cell in cage.cells:
            expansion_of_cage.append(self.mstate[cell.x][cell.y])

        if cage.operator == Operator.Add :
            return sum(expansion_of_cage) == cage.value
        elif cage.operator == Operator.Subtract : #Subtract Cages is only 2 cells
            """
            Subtract Cages is only 2 cells
            Because order of subrtacting among more than 2 cells will be distinctive
            """
            if len(expansion_of_cage) != 2 :
                return False
            return abs(expansion_of_cage[0]-expansion_of_cage[1]) == cage.value

        elif cage.operator == Operator.Multiply :
            return np.prod(expansion_of_cage) == cage.value

        elif cage.operator == Operator.Divide : #Division Cages is only 2 cells
            """
            Subtract Cages is only 2 cells
            Because order of subrtacting among more than 2 cells will be distinctive
            """
            if(expansion_of_cage[0] > expansion_of_cage[1]):
                return (expansion_of_cage[0] / expansion_of_cage[1]) == cage.value
            elif(expansion_of_cage[0] < expansion_of_cage[1]):
                return (expansion_of_cage[1] / expansion_of_cage[0]) == cage.value
        elif cage.operator == Operator.Constant :
            return True

    """Initially fill all cells with all possible values and filling constants with its value only"""
    def init_domain_fill(self):
        default_domain = [x for x in range(1, self.size+1)]
        for cage in self.cages:
            if cage.operator == Operator.Constant:
                cage.cells[0].domain = [cage.value] # should be removed
                index_x = cage.cells[0].x
                index_y = cage.cells[0].y
                self.mDomain[index_x][index_y] = [cage.value]
            else:
                for cell in cage.cells:
                    self.mDomain[cell.x][cell.y] = default_domain
                # should be removed
                for j in range(len(cage.cells)):
                    cage.cells[j].domain = default_domain
        # print(self.mDomain)

    def can_place(self, value, x, y):
        return not(self.mColHash[y][value-1] or self.mRowHash[x][value-1])

    def forward_checking(self, value, x_pos, y_pos, mDomain, freebie_domain=False):
        mDomain_temp = copy.deepcopy(mDomain)
        for col_iter in range(self.size):
            if not col_iter == y_pos:
                domain_temp = list(mDomain_temp[x_pos][col_iter])
                if value in domain_temp:
                    domain_temp.remove(value)
                    mDomain_temp[x_pos][col_iter] = domain_temp
        for row_iter in range(self.size):
            if not row_iter == x_pos: 
                domain_temp = list(mDomain_temp[row_iter][y_pos])
                if value in domain_temp:
                    domain_temp.remove(value)
                    mDomain_temp[row_iter][y_pos] = domain_temp
        
        if freebie_domain == True:
            mDomain_temp[x_pos][y_pos] = [-1]
        else:
            domain_temp = list(mDomain_temp[x_pos][y_pos])
            domain_temp.remove(value)
            mDomain_temp[x_pos][y_pos] = domain_temp
        return mDomain_temp

    def fill_freebie(self, algorithm = 0):
        filtered_list = list(self.cages)
        for cage in self.cages:
            if len(cage.cells) == 1:
                x_pos = cage.cells[0].x
                y_pos = cage.cells[0].y
                self.mstate[x_pos][y_pos] = cage.value
                self.mColHash[y_pos][cage.value - 1] = True
                self.mRowHash[x_pos][cage.value - 1] = True
                filtered_list.remove(cage)
                if algorithm == 1:
                    self.mDomain = self.forward_checking(cage.value, x_pos, y_pos, self.mDomain, True)
        self.cages = filtered_list
        # print('mDomain after freebie filling:\n', self.mDomain)
        # print('mstate after freebie filling:\n', self.mstate)

    def solve_with_backtracking(self, arc_consistency= False):
        if np.all(self.mRowHash) and np.all(self.mColHash):
            # print('Final mstate:\n', self.mstate)
            return True
        for cage in self.cages:
            for cell in cage.cells:
                x_pos = cell.x
                y_pos = cell.y
                if self.mstate[x_pos][y_pos] == 0:
                    old_domain = cell.domain
                    for val in old_domain:
                        if self.can_place(val, x_pos, y_pos):
                            cell.domain = [val]
                            self.mColHash[y_pos][val - 1] = True
                            self.mRowHash[x_pos][val - 1] = True
                            self.mstate[x_pos][y_pos] = val
                            
                            if cell == cage.cells[-1]:
                                
                                cage_validated = self.validate_cage_constraint(cage)
                            else:
                                cage_validated = True
                            
                            if cage_validated:
                                if arc_consistency:
                                    self.generate_queue(cell=cell, cage=cage)
                                    if self.AC3():
                                        result = self.solve_with_backtracking(arc_consistency=True)
                                    else :
                                        result = False
                                else :
                                    result = self.solve_with_backtracking()
                            elif not cage_validated:
                                result = False

                            if not result:
                                cell.domain = old_domain
                                self.mColHash[y_pos][val - 1] = False
                                self.mRowHash[x_pos][val - 1] = False
                                self.mstate[x_pos][y_pos] = 0
                            elif result:
                                return True
                            # print('Current mstate: \n', self.mstate)
                            # input('Press any key to continue')
                    return False

    def solve_with_backtracking_and_forward_checking(self, var_domains):
        if np.all(self.mRowHash) and np.all(self.mColHash):
            # print('Final mstate:\n', self.mstate)
            return True
        for cage in self.cages:
            for cell in cage.cells:
                x_pos = cell.x
                y_pos = cell.y
                if self.mstate[x_pos][y_pos] == 0:
                    for val in var_domains[x_pos][y_pos]:
                        if self.can_place(val, x_pos, y_pos):
                            self.mColHash[y_pos][val - 1] = True
                            self.mRowHash[x_pos][val - 1] = True
                            self.mstate[x_pos][y_pos] = val
                            new_var_domains = self.forward_checking(val, x_pos, y_pos, var_domains)

                            if cell == cage.cells[-1]:
                                cage_validated = self.validate_cage_constraint(cage)
                            else:
                                cage_validated = True
                            
                            if cage_validated:
                                result = self.solve_with_backtracking_and_forward_checking(new_var_domains)
                            elif not cage_validated:
                                result = False

                            if not result:
                                self.mColHash[y_pos][val - 1] = False
                                self.mRowHash[x_pos][val - 1] = False
                                self.mstate[x_pos][y_pos] = 0
                            elif result:
                                # print('Backtracked')
                                return True
                            # print('Current mstate: \n', self.mstate)
                            # input('Press any key to continue')
                    return False



            
    def generate_queue(self, cage, cell, filter = False, cell2 = None):
        # for cage in self.cages :
        #     for cell in cage.cells:
        for cage1 in self.cages :
            for cell1 in cage1.cells:

                if (cell == cell1) or (filter and (cell1 == cell2)):
                    continue

                if (cage == cage1) and (len(cage.cells) == 2) and ((cage,cell),cell1) not in self.queue:
                    self.queue.append(((cage,cell),cell1))
                    continue
                
                if (cell1.x != cell.x and cell1.y == cell.y) or (cell1.x == cell.x and cell1.y != cell.y) and ((cage,cell),cell1) not in self.queue:
                    self.queue.append(((cage,cell),cell1))

                        

  
        # x1 = cell.x
        # y1 = cell.y
        
        # domain = cell.domain

        
        # if(len(domain) > 1):
        #     return 0
        # elif (len(domain) == 0) :
        #     return -1
        
        # if len(cage.cells) == 2 : #Has two elements
        #     index_of_cell = cage.cells.where(cage.cells == cell)

        #     if cage.operation == Operator.Multiply :
        #         expected = cage.value / cell.domain[0]
        #         if expected == cell.domain[0] :
        #             return -1
        #         domain_neighbour = cage.cells[1-index_of_cell].domain
        #         cage.cells[1-index_of_cell].domain = intersection(cage.cells[1-index_of_cell].domain, [expected])
        #         v = self.check_constraints(cage, cage.cells[1-index_of_cell])
        #         if v == -1:
        #             cage.cells[1-index_of_cell].domain = domain_neighbour
        #             return -1
        #     elif cage.operation == Operator.Add :
        #         expected = cage.value - cell.domain[0]
                
        #         domain_neighbour = cage.cells[1-index_of_cell].domain
        #         cage.cells[1-index_of_cell].domain = intersection(cage.cells[1-index_of_cell].domain, [expected])
        #         v = self.check_constraints(cage, cage.cells[1-index_of_cell])
        #         if v == -1:
        #             cage.cells[1-index_of_cell].domain = domain_neighbour
        #             return -1
        #     elif cage.operation == Operator.Subtract :
        #         expected = cage.value + cell.domain[0]
        #         if expected > self.size :
        #             expected = cage.value - cell.domain[0]
        #             if expected > self.size :
        #                 return -1
        #         if expected == cell.domain[0] :
        #             return -1
        #         domain_neighbour = cage.cells[1-index_of_cell].domain
        #         cage.cells[1-index_of_cell].domain = intersection(cage.cells[1-index_of_cell].domain, [expected])
        #         v = self.check_constraints(cage, cage.cells[1-index_of_cell])
        #         if v == -1:
        #             cage.cells[1-index_of_cell].domain = domain_neighbour
        #             return -1
        #     elif cage.operation == Operator.Divide :
        #         expected = cage.value * cell.domain[0] #Numerator
        #         if expected > self.size :
        #             expected = cell.domain[0] / self.size
        #             if expected > self.size :
        #                 return -1
        #         if expected == cell.domain[0] :
        #             return -1
        #         domain_neighbour = cage.cells[1-index_of_cell].domain
        #         cage.cells[1-index_of_cell].domain = intersection(cage.cells[1-index_of_cell].domain, [expected])
        #         v = self.check_constraints(cage, cage.cells[1-index_of_cell])
        #         if v == -1:
        #             cage.cells[1-index_of_cell].domain = domain_neighbour
        #             return -1


        # #Row and col
        # for c in self.cages:
        #     for ce in c.cells:
            
        #         dom = ce.domain
        #         v = None
        #         if ce.x != x1 and ce.y == y1 : #Same Column
        #             next = Diff(dom, domain)
        #             if ce.domain == next:
        #                 return 0
        #             ce.domain = next
        #             if len(c.cells) == 1 :
        #                 # self.mstate[ce.x][ce.y] = cage.value
        #                 # self.mColHash[ce.y][cage.value - 1] = True
        #                 # self.mRowHash[ce.x][cage.value - 1] = True
        #                 cage.cells[0].domain = [cage.value]
        #             v = self.check_constraints(c, ce)
        #         # elif ce.x == (x1+2) % 3  and ce.y == y1 :
        #         #     ce.domain = np.setdiff1d(ce.domain, domain)
        #         #     if len(c.cells) == 1 :
        #         #         # self.mstate[ce.x][ce.y] = cage.value
        #         #         # self.mColHash[ce.y][cage.value - 1] = True
        #         #         # self.mRowHash[ce.x][cage.value - 1] = True
        #         #         cage.cells[0].domain = np.array([cage.value])
        #         #     v = self.check_constraints(c, ce)
        #         elif ce.x == x1  and ce.y != y1 : #Same Row
                    
        #             next = Diff(dom, domain)
        #             if ce.domain == next:
        #                 return 0
        #             ce.domain = next
        #             if len(c.cells) == 1 :
        #                 # self.mstate[ce.x][ce.y] = cage.value
        #                 # self.mColHash[ce.y][cage.value - 1] = True
        #                 # self.mRowHash[ce.x][cage.value - 1] = True
        #                 cage.cells[0].domain = [cage.value]
        #             v = self.check_constraints(c, ce)
        #         # elif ce.x == x1  and ce.y == (y1+2)%3 :
        #         #     ce.domain = np.setdiff1d(ce.domain, domain)
        #         #     if len(c.cells) == 1 :
        #         #         # self.mstate[ce.x][ce.y] = cage.value
        #         #         # self.mColHash[ce.y][cage.value - 1] = True
        #         #         # self.mRowHash[ce.x][cage.value - 1] = True
        #         #         cage.cells[0].domain = np.array([cage.value])
        #         #     v = self.check_constraints(c, ce)
                
        #         if v == -1  :
        #             ce.domain = dom
        #             return -1
        
        # return 1

    def remove_inconsistent_values(self, cage, cell1, cell2):
        removed = False

        # to_be_removed = False

        #only compare to single element domain in cell2
        if len(cell2.domain) == 1:
            if (cell1.x != cell2.x and cell1.y == cell2.y) or (cell1.x == cell2.x and cell1.y != cell2.y) :
                virtual_domain = cell1.domain
                for domain in cell1.domain:
                    if domain == cell2.domain[0]:
                        virtual_domain.remove(domain)
                        removed = True
        
                cell1.domain = virtual_domain
        return removed

    def AC3(self):
        while len(self.queue) != 0:
            binary_arc = self.queue[0]
            self.queue = self.queue[1:]
            cage = binary_arc[0][0]
            cell = binary_arc[0][1]
            cell1 = binary_arc[1]
            old_domain = [] + cell.domain
            if self.remove_inconsistent_values(cage, cell, cell1):
                if len(cell.domain) == 0 :
                    cell.domain = old_domain
                    return False
                self.generate_queue(cage, cell, filter=True, cell2 = cell1)
        return True

def solve(cages, size, algorithm):
    """
    algorithm = 0   => normal backtracking
    algorithm = 1   => backtracking with forward checking
    algorithm = 2   => backtracking with arc consistency
    """
    # sub1 = Cage(Operator.Constant, 2, [Cell(0, 0)])
    # sub2 = Cage(Operator.Subtract, 2, [Cell(0, 1), Cell(1, 1)])
    # sub3 = Cage(Operator.Subtract, 1, [Cell(0, 2), Cell(1, 2)])
    # sub4 = Cage(Operator.Add, 6, [Cell(1, 0), Cell(2, 0), Cell(2, 1)])
    # sub5 = Cage(Operator.Constant, 1, [Cell(2, 2)])
    # cages = [sub1, sub2, sub3, sub4, sub5]
    board = KenKenBoard(size=size, cages=cages)
    board.init_domain_fill()
    
    # algorithm = 2
    if algorithm == 0:
        board.fill_freebie(algorithm)
        board.solve_with_backtracking()
        # print("My solution:\n", board.mstate)
        return board.mstate
    elif algorithm == 1:
        board.fill_freebie(algorithm)
        board.solve_with_backtracking_and_forward_checking(board.mDomain)
        # print("My solution:\n", board.mstate)
        return board.mstate
    elif algorithm == 2:
        board.solve_with_backtracking(arc_consistency=True)
        return board.mstate



def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))


def Diff(li1, li2):
    return list(set(li1) - set(li2))







"""Random Testcase"""
# size = 3
# cages, solution = generate(size)
# cells_count = 0
# for cage in cages:
#     cells_count += len(cage.cells)
#     print('Cage operator: {} \t cage value: {} \t\t cage cells: {}'.format(cage.operator, cage.value, [(cell.x, cell.y) for cell in cage.cells]))
# print(cells_count)
# print("Solution\n", solution)
# t1 = datetime.now()
# print("My solution:\n", solve(cages, size, 0))
# print(datetime.now() - t1)

"""Random n boards testcase"""
# size = 6
# n = 100
# algorithms = ['Bactracking','Forward Checking' , 'Arc Consistency']
# algorithm = 2
# boards,solutions = generate_n_boards(n,size)
# # print(type(boards[0][0]))
# my_solutions = []
# time1 = datetime.now()
# for board in boards:
#     my_solutions.append(solve(board,size,algorithm))
# time2 = datetime.now()
# print("algorithm used: {}    total_time: {}   number of boards: {}    size of each board: {}".format(algorithms[algorithm],time2-time1,n,size))
