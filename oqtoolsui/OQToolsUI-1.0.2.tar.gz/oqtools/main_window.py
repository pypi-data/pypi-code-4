from ui.asciiconverterwindow import AsciiConverterWindow
from PyQt4 import QtGui as gui
from ui.shapeconverterwindow import ShapeConverterWindow
from ui.inputfilegenwindow import InputFileGeneratorWindow
from ui.nrmlconverterwindow import NrmlConverterWindow

class MainWindow():
    def __init__(self):
        self.__mainWindow = gui.QMainWindow()
        self.initGui()
        
        self.showInputFileGeneratorWindow()

    def initGui(self):
        self.initMenu()
        
        self.__mainWindow.setGeometry(100, 100, 1024, 768)
        self.__mainWindow.setWindowTitle('OpenQuake Admin')

    def initMenu(self):
        menuBar = self.__mainWindow.menuBar()
        menu = menuBar.addMenu('Input')

        action = gui.QAction('&Convert Shape Files', self.__mainWindow)
        action.triggered.connect(self.showConverterWindow)
        menu.addAction(action)

        action = gui.QAction('&NRML v0.3 -> NRML v0.4', self.__mainWindow)
        action.triggered.connect(self.showNrmlConverterWindow)
        menu.addAction(action)

        action = gui.QAction('&Generate Input Files', self.__mainWindow)
        action.triggered.connect(self.showInputFileGeneratorWindow)
        menu.addAction(action)

        menu = menuBar.addMenu('Result')
        action = gui.QAction('&Convert Result Files to XLS', self.__mainWindow)
        action.triggered.connect(self.showAsciiConverterWindow)
        menu.addAction(action)

    def showConverterWindow(self):
        self.__mainWindow.setCentralWidget(ShapeConverterWindow(parent=self.__mainWindow))

    def showInputFileGeneratorWindow(self):
        self.__mainWindow.setCentralWidget(InputFileGeneratorWindow(parent=self.__mainWindow))

    def showAsciiConverterWindow(self):
        self.__mainWindow.setCentralWidget(AsciiConverterWindow(parent=self.__mainWindow))

    def showNrmlConverterWindow(self):
        self.__mainWindow.setCentralWidget(NrmlConverterWindow(parent=self.__mainWindow))

    def show(self):
        self.__mainWindow.show()