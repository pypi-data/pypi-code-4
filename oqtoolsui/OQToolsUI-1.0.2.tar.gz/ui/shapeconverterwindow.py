from PyQt4 import QtGui as gui
from PyQt4 import QtCore as core
from ui.panels import BaseWindow
from ui.widgets import BrowseFileText, NamedTextArea
from controllers.convertercontroller import convert


class ShapeConverterWindow(BaseWindow):

    def __init__(self, parent=None):
        super(BaseWindow, self).__init__(parent=parent)
        self.initGui()

    def initGui(self):
        self.sourceFile = BrowseFileText(self, isDir=False)
        self.sourceFile.initGui(self, 'Source File Name', 10, 10)

        self.targetFile = BrowseFileText(self, isDir=False)
        self.targetFile.initGui(self, 'Target File Name', 10, 60)

        label = gui.QLabel('Source Model Type', self)
        label.setGeometry(10, 110, 150, 30)

        self.modelType = gui.QComboBox(self)
        self.modelType.addItem(core.QString('Point'))
        self.modelType.addItem(core.QString('Area'))
        self.modelType.addItem(core.QString('Simple Fault'))
        self.modelType.addItem(core.QString('Complex Fault'))
        self.modelType.setGeometry(160, 110, 100, 30)

        label = gui.QLabel('Parameters', self)
        label.setGeometry(10, 160, 150, 30)

        self.aValPrm = NamedTextArea(self)
        self.aValPrm.initGui(self, 'A', 10, 210)
        self.aValPrm.setText('AGRVAL')

        self.bValPrm = NamedTextArea(self)
        self.bValPrm.initGui(self, 'B', 10, 260)
        self.bValPrm.setText('BGRVAL')

        self.idPrm = NamedTextArea(self)
        self.idPrm.initGui(self, 'ID', 10, 310)
        self.idPrm.setText('EMME_IDAS')

        self.namePrm = NamedTextArea(self)
        self.namePrm.initGui(self, 'Name', 10, 360)
        self.namePrm.setText('EMME_IDAS')

        converter = gui.QPushButton('Convert', self)
        converter.setGeometry(410, 410, 120, 40)
        converter.clicked.connect(self.__convertFiles)

    def __convertFiles(self):
        sourceFileName = self.sourceFile.getSelectedFile()
        targetFileName = self.targetFile.getSelectedFile()

        params = dict()
        params['A'] = self.aValPrm.getText()
        params['B'] = self.bValPrm.getText()
        params['ID'] = self.idPrm.getText()
        params['NAME'] = self.namePrm.getText()

        self.callFunction(lambda: convert(sourceFileName, targetFileName, str(self.modelType.currentText()), params),
                                   'Source model file is generated')
