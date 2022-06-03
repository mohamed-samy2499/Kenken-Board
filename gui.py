from ntpath import join
import sys
import enum
from tkinter import Spinbox
from webbrowser import Opera
from cv2 import multiply, subtract
import numpy as np
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Generate import generate
from Utilities import solve
from main_utilities import *

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Welcome to KenKen!'
        self.left = 800
        self.top = 300
        self.size = 4
        self.width = (self.size + 6)*40
        self.height = (self.size + 2)*40
        self.welcomeUI()

    def welcomeUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.welcome_label = QLabel("Welcome to", self)
        self.kenken_label = QLabel("KENKEN", self)

        QFontDatabase.addApplicationFont("PressStart2P-Regular.ttf")
        self.welcome_label.setFont(QFont('Press Start 2P', 10))
        self.kenken_label.setFont(QFont('Press Start 2P', 22))

        self.welcome_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.kenken_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.kenken_label.setAlignment(Qt.AlignCenter)

        self.welcome_label.resize(self.width-200, self.height-75)
        self.kenken_label.resize(self.width-200, self.height-75)

        self.welcome_label.move(40, 40)
        self.kenken_label.move(40, 80)

        self.welcome_label.setStyleSheet("border: solid gray; color: solid gray;"
                                    "border-width: 3px 3px 3px 3px;")
        self.kenken_label.setStyleSheet("color: red;")



        self.spinbox = QSpinBox(self)
        self.spinbox.resize(75, 25)
        self.spinbox.move(int(self.width/1.45), int(self.height/2.2))
        self.spinbox.setRange(3, 100)

        # Create generate button in the window
        button_start = QPushButton('Start', self)
        button_start.resize(75, 25)
        button_start.move(int(self.width/1.45),int(self.height/1.76))
        # connect button to function on_click
        button_start.clicked.connect(self.start_on_click)
        
        self.show()
    
    @pyqtSlot()
    def start_on_click(self):
        print("size: ", self.spinbox.text())
        self.cams = PuzzleWindow(int(self.spinbox.text())) 
        self.cams.show()
        self.close()

class PuzzleWindow(QDialog):
    def __init__(self, size, parent=None):
        super().__init__(parent)
        self.color_space = ['#00FFFF','red','yellow','purple','#7FFFD4','orange','brown','green','pink']
        self.title = 'KenKen Puzzle!'
        self.left = 800
        self.top = 300
        self.size = size
        self.solved_board = None
        self.cages = []
        self.labels = np.empty((self.size,self.size),QLabel)
        self.operator = '#'
        self.width = (self.size + 6)*60
        self.height = (self.size + 2)*60
        self.x1 = 50
        self.y1 = 50
        self.x2 = 50
        self.y2 = 60
        self.lines = []
        self.algorithm = 0
        self.counter = 0
        self.drawBoard()
    def set_operator_value(self,op,value,cells,color):
        min_cell = cells[0]
        for cell in cells:
            if cell.x < min_cell.x and cell.y < min_cell.y:
                min_cell = cell
        self.label = self.labels[min_cell.y][min_cell.x]
        self.label.setText("<div style='position:fixed;top:0;left:0;font-size:20px;'><sup>{}</sup><sup>{}</sup></div>".format(op,value))
        for cell in cells:
            self.label = self.labels[cell.y][cell.x]
            self.label.setStyleSheet("border : solid {};""border-width : 2px 2px 2px 2px;".format(self.color_space[self.counter]))
        self.counter = (self.counter+ 1) % len(self.color_space)
    def drawBoard(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # call generate function from generate.py
        self.cages,sol = generate(self.size)

        self.alg_box = QComboBox(self)
        self.alg_box.resize(130, 25)
        self.alg_box.move(int(self.width-170),int(self.height/1.9))
        alg_list = ["Backtracking", "Forward Checking", "Arc Consistency"]
        self.alg_box.addItems(alg_list)
        self.alg_box.setEditable(True)
        self.alg_box.currentIndexChanged.connect(self.algorithm_change)

        self.spinbox = QSpinBox(self)
        self.spinbox.resize(75, 25)
        self.spinbox.move(int(self.width-150), int(self.height/4))
        self.spinbox.setRange(3, 100)

        for i in range(self.size):
            for j in range(self.size):
                self.label = QLabel("", self)
                self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                # self.label.setAlignment(Qt.AlignLeft)
        
                self.label.resize(60, 60)
                self.label.move((i+1)*60, (j+1)*60)

                self.x1 = self.label.x()
                self.y1 = self.label.y()
                self.x2 = self.x1 + 40
                self.y2 = self.y1 + 40

                # print(i, j, self.label.x(), self.label.y())
                self.label.setStyleSheet("border : solid black;"
                                            "border-width : 1px 1px 1px 1px;")

                self.labels[i][j] = self.label

        
        for cage in self.cages:
            xIndex = cage.cells[0].x
            yIndex = cage.cells[0].y
            self.label = self.labels[yIndex][xIndex]
            op = cage.operator
            if op == Operator.Constant:
                self.label.setText("<div style='position:fixed;top:0;left:0;font-size:20px;'><sup>{}</sup></div>".format(cage.value))
                self.label.setStyleSheet("border : solid black;""border-width : 2px 2px 2px 2px;")
            elif op == Operator.Add:
                self.set_operator_value("+",cage.value,cage.cells,"red")
            elif op == Operator.Subtract:
                self.set_operator_value("-",cage.value,cage.cells,"yellow")
            elif op == Operator.Multiply:
                self.set_operator_value("*",cage.value,cage.cells,"blue")
            elif op == Operator.Divide:
                self.set_operator_value("÷",cage.value,cage.cells,"purple")
                
        
        
        # Create a button in the window
        self.button_generate = QPushButton('New Board', self)
        self.button_generate.resize(75, 25)
        self.button_generate.move(int(self.width-150), int(self.height/2.7))

        self.button_solve = QPushButton('Slove', self)
        self.button_solve.resize(75, 25)
        self.button_solve.move(int(self.width-150),int(self.height/1.55))

        self.button_reset = QPushButton('Reset', self)
        self.button_reset.resize(75, 25)
        self.button_reset.move(int(self.width-150),int(self.height/1.26))
        
        # connect button to function on_click
        self.button_generate.clicked.connect(self.generate_board)
        self.show()

        self.button_solve.clicked.connect(self.solve_board)
        self.show()

        self.button_reset.clicked.connect(self.reset_board)

    # def paintEvent(self, e):
    #     qp = QPainter()
    #     qp.begin(self)
    #     self.drawLines(qp)
    #     qp.end()

    # def drawLines(self, qp):
    #     painter = QPainter(self)
    #     painter.setPen(Qt.red)
    #     line = painter.drawLine(self.x1, self.y1, self.x2, self.y2)
        # QPainter.save()
        # if line not in self.lines:
        #     self.lines.append(line)
        #     self.update()

    def algorithm_change(self, i):
        self.algorithm = i


    def generate_board(self):
        # print("size: ", self.spinbox.text())
        self.cams = PuzzleWindow(int(self.spinbox.text())) 
        self.cams.show()
        self.close()
       
    
    def solve_board(self):
        # print(self.algorithm)
        solved = solve(self.cages, self.size, self.algorithm)
        self.solved_board = solved
        # print("abdo soln: {}".format(self.solved_board))
        self.fill()

    def fill(self):
        # print(self.solve_board.shape)
        for i in range(self.size):
            for j in range(self.size):
                self.label = self.labels[j][i]
                if(self.label.text() == ''):
                    self.label.setText("<div style='position:fixed;top:0;left:0;font-size:20px;color:#f0f0f0;'><sup>3-</sup></div>")
                self.label.setText(self.label.text() + "<div style='font-size:30px;text-align:center;'>{}</div>".format(self.solved_board[i][j]))
                


    def reset_board(self):
        for i in range(self.size):
            for j in range(self.size):
                self.label = self.labels[i][j]
                self.label.setText(" ")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())