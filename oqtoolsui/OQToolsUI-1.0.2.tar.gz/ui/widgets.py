from PyQt4 import QtGui as gui
from PyQt4 import QtCore as core
from os.path import split


class CompositeListWidgetItem(gui.QListWidgetItem):
    def __init__(self):
        super(gui.QListWidgetItem, self).__init__()

    def setCustomData(self, data):
        self.setText(core.QString(str(data)))
        self.customData = data


class NamedTextArea(gui.QWidget):
    def __init__(self, parent=None):
        super(gui.QWidget, self).__init__(parent=parent)
        
    def initGui(self, parent, text, x, y, labelLength=150, textLength=250):
        label = gui.QLabel(parent)
        label.setText(text)
        label.setGeometry(x, y, labelLength, 40)
        
        self.__textArea = gui.QLineEdit(parent)
        self.__textArea.setGeometry(x + labelLength, y, textLength, 30)
        
        self.setGeometry(x, y, labelLength + textLength, 40)
        
    def setText(self, text):
        self.__textArea.setText(core.QString(text))
        
    def getText(self):
        return str(self.__textArea.text())


class BrowseFileText(gui.QWidget):

    __lastVisited = '.'

    def __init__(self, parent=None, isDir=False):
        super(gui.QWidget, self).__init__(parent=parent)
        self.__selectDirectories = isDir
        
    def initGui(self, parent, text, x, y):
        self.__namedText = NamedTextArea(parent)
        self.__namedText.initGui(parent, text, x, y)
        
        button = gui.QPushButton(parent)
        button.setText('..')
        button.setGeometry(x + 420, y, 50, 30)
        button.clicked.connect(self.__selectFile)

        self.setGeometry(x, y, 550, 40)
        
    def __selectFile(self):
        if self.__selectDirectories:
            func = gui.QFileDialog.getExistingDirectory
        else:
            func = gui.QFileDialog.getOpenFileName

        openFileName = func(self, 'Select File', self.__lastVisited)

        if openFileName is not None and len(str(openFileName)) > 0:
            self.__namedText.setText(openFileName)
            parts = split(str(openFileName))
            self.__lastVisited = parts[0]
        
    def getSelectedFile(self):
        return self.__namedText.getText()