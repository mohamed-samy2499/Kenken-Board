import enum
import numpy as np

class Operator(enum.Enum):
    Add = 0
    Subtract = 1
    Multiply = 2
    Divide = 3
    Constant = 4

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.domain = np.empty((0),np.int32)

class Cage:
    def __init__(self, operator, value, cells=[], solutions=[]):
        self.operator = operator
        self.value = value
        self.cells = cells