import PyQt4.QtGui as gui
from oqtoolsui.ui.panels import *
from oqtoolsui.ui.widgets import *
from oqtoolsui.controllers.nrmlconvertercontroller import convert


class NrmlConverterWindow(BaseWindow):
    def __init__(self, parent=None):
        super(BaseWindow, self).__init__(parent=parent)
        self.initGui()

    def initGui(self):
        self.sourceFile = BrowseFileText(self, isDir=False)
        self.sourceFile.initGui(self, 'NRML v0.3 File', 10, 10)

        self.targetFile = BrowseFileText(self, isDir=False)
        self.targetFile.initGui(self, 'NRML v0.4 File', 10, 60)

        converter = gui.QPushButton('Convert', self)
        converter.setGeometry(380, 120, 100, 40)
        converter.clicked.connect(self.__convertFile)

    def __convertFile(self):
        s = self.sourceFile.getSelectedFile()
        t = self.targetFile.getSelectedFile()

        self.callFunction(lambda: convert(s, t), 'Conversion is successful')