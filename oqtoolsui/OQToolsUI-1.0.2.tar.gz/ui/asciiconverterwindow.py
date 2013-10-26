from PyQt4 import QtGui as gui, QtCore as core

from ui.widgets import BrowseFileText
from ui.panels import BaseWindow
from controllers.asciiconvertercontroller import *


class AsciiConverterWindow(BaseWindow):

    def __init__(self, parent=None):
        super(BaseWindow, self).__init__(parent=parent)
        self.initGui()

    def initGui(self):
        self.sourceFile = BrowseFileText(self, isDir=False)
        self.sourceFile.initGui(self, 'Source File Name', 10, 10)

        self.targetFile = BrowseFileText(self, isDir=False)
        self.targetFile.initGui(self, 'Target File Name', 10, 60)

        self.outputFileType = gui.QComboBox(self)
        self.outputFileType.addItem(core.QString('Hazard Map'))
        self.outputFileType.addItem(core.QString('Hazard Curve'))
        self.outputFileType.addItem(core.QString('UH Spectra'))
        self.outputFileType.setGeometry(260, 100, 150, 30)

        converter = gui.QPushButton('Convert', self)
        converter.setGeometry(410, 150, 120, 40)
        converter.clicked.connect(self.__convertFile)

    def __convertFile(self):
        s = self.sourceFile.getSelectedFile()
        t = self.targetFile.getSelectedFile()
        outputFileType = self.outputFileType.currentIndex()
        func = None

        if outputFileType == 0:
            func = convertHazardMapToAscii
        elif outputFileType == 1:
            func = convertHazardCurveToAscii
        elif outputFileType == 2:
            func = convertUhSpectraToAscii

        self.callFunction(lambda: func(s, t), 'Conversion is successful')