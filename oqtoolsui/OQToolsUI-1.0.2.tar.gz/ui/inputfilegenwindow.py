from PyQt4 import QtGui as gui
from os.path import split
from string import join

from controllers.inputfilegencontroller import save, load, execute
from ui.panels import BaseWindow
from ui.widgets import BrowseFileText, NamedTextArea, CompositeListWidgetItem
from common.values import gmpes
from common.entities import Gmpe


class InputFileGeneratorWindow(BaseWindow):
    
    def __init__(self, parent=None):
        super(BaseWindow, self).__init__(parent=parent)
        self.initGui()
        
    def initGui(self):
        self.__initTopFrame()
        self.__initGmpeFrame()
        self.__initGridFrame()
        self.__initOtherPrmFrame()
        self.__initActionButtons()
    
    def __initTopFrame(self):
        topFrame = gui.QFrame(self)
        topFrame.setFrameStyle(gui.QFrame.Box)
        topFrame.setGeometry(10, 10, 550, 180)

        self.__targetDir = BrowseFileText(topFrame, isDir=True)
        self.__targetDir.initGui(topFrame, 'Target Directory', 10, 10)
        
        self.__runName = NamedTextArea(topFrame)
        self.__runName.initGui(topFrame, 'Name', 10, 50)
        
        self.__description = NamedTextArea(topFrame)
        self.__description.initGui(topFrame, 'Description', 10, 90)

    def __initGmpeFrame(self):
        gmpeFrame = gui.QFrame(self)
        gmpeFrame.setFrameStyle(gui.QFrame.Box)
        gmpeFrame.setGeometry(10, 210, 550, 270)
        
        self.__sourceGmpeList = gui.QListWidget(gmpeFrame)
        self.__sourceGmpeList.setGeometry(10, 10, 230, 250)
        for gmpe in gmpes:
            self.__sourceGmpeList.addItem(gmpe)
            
        addButton = gui.QPushButton('>>', gmpeFrame)
        addButton.setGeometry(260, 40, 30, 30)
        addButton.clicked.connect(self.__addGmpe)
        
        removeButton = gui.QPushButton('<<', gmpeFrame)
        removeButton.setGeometry(260, 80, 30, 30)
        removeButton.clicked.connect(self.__removeGmpe)
            
        self.__targetGmpeList = gui.QListWidget(gmpeFrame)
        self.__targetGmpeList.setGeometry(310, 10, 230, 250)
        
    def __addGmpe(self):
        selectedItem = self.__sourceGmpeList.currentItem()
        
        if selectedItem is not None:
            selectedItemText = selectedItem.text()
            count = self.__targetGmpeList.count()
            
            for itemIndex in xrange(count):
                currentData = self.__targetGmpeList.item(itemIndex).customData
                if selectedItemText == currentData.name:
                    return

            try:
                inputDialog = gui.QInputDialog()
                res = float(str(inputDialog.getText(self.__sourceGmpeList, 'Weight', 'Weight of GMPE?')[0]))
                g = Gmpe(str(selectedItemText), res)
                self.__addGmpeToList(g)
            except:
                self.showMessage('Invalid weight', 'Error')

    def __addGmpeToList(self, g):
        widgetItem = CompositeListWidgetItem()
        widgetItem.setCustomData(g)

        self.__targetGmpeList.addItem(widgetItem)
        self.__targetGmpeList.sortItems()

    def __removeGmpe(self):
        selectedItem = self.__targetGmpeList.currentRow()
        
        if selectedItem >= 0:
            self.__targetGmpeList.takeItem(selectedItem)
            self.__targetGmpeList.sortItems()
            
    def __initGridFrame(self):
        gridFrame = gui.QFrame(self)
        gridFrame.setFrameStyle(gui.QFrame.Box)
        gridFrame.setGeometry(10, 500, 550, 150)
        
        self.__coordinates = NamedTextArea(gridFrame)
        self.__coordinates.initGui(gridFrame, 'Lat & Lon.', 10, 10, textLength=250)
        
        self.__gridSpace = NamedTextArea(gridFrame)
        self.__gridSpace.initGui(gridFrame, 'Grid Space', 10, 50, textLength=100)
        
    def __initOtherPrmFrame(self):
        otherPrmFrame = gui.QFrame(self)
        otherPrmFrame.setFrameStyle(gui.QFrame.Box)
        otherPrmFrame.setGeometry(570, 210, 430, 440)
        
        self.__period = NamedTextArea(otherPrmFrame)
        self.__period.initGui(otherPrmFrame, 'Periods', 10, 10)
        
        self.__poes = NamedTextArea(otherPrmFrame)
        self.__poes.initGui(otherPrmFrame, 'PoE Values', 10, 50)
        
        self.__quantiles = NamedTextArea(otherPrmFrame)
        self.__quantiles.initGui(otherPrmFrame, 'Quantiles', 10, 90)
        
        self.__minMagnitude = NamedTextArea(otherPrmFrame)
        self.__minMagnitude.initGui(otherPrmFrame, 'Min. Magnitude', 10, 130, textLength=75)

        self.__investigationTime = NamedTextArea(otherPrmFrame)
        self.__investigationTime.initGui(otherPrmFrame, 'Investigation Time', 10, 170, textLength=75)
        
    def __initActionButtons(self):
        saveButton = gui.QPushButton('Save', self)
        saveButton.setGeometry(570, 660, 100, 30)
        saveButton.clicked.connect(self.__saveConfig)
        
        loadButton = gui.QPushButton('Load', self)
        loadButton.setGeometry(680, 660, 100, 30)
        loadButton.clicked.connect(self.__loadConfig)
        
        executeButton = gui.QPushButton('Execute', self)
        executeButton.setGeometry(790, 660, 100, 30)
        executeButton.clicked.connect(self.__executeConfig)
        
    def __prepareInputs(self):
        parameters = {'name': self.__runName.getText(), 'description': self.__description.getText()}

        gmpes = []
        l = self.__targetGmpeList.count()
        for i in xrange(l):
            gmpes.append(self.__targetGmpeList.item(i).customData)

        parameters['gmpes'] = gmpes
        parameters['gmpes_str'] = join([str(g) for g in gmpes], ',')
        
        parameters['grid'] = self.__coordinates.getText()
        parameters['grid_space'] = str(self.__gridSpace.getText())
        parameters['periods'] = str(self.__period.getText())
        parameters['poes'] = str(self.__poes.getText())
        parameters['quantiles'] = str(self.__quantiles.getText())
        parameters['min_magnitude'] = str(self.__minMagnitude.getText())
        parameters['investigation_time'] = str(self.__investigationTime.getText())
        
        return parameters
    
    def __changeParameters(self, parameters):
        self.__runName.setText(parameters.get('name', ''))
        self.__description.setText(parameters.get('description', ''))
        self.__gridSpace.setText(parameters.get('grid_space', ''))
        self.__period.setText(parameters.get('periods', ''))
        self.__poes.setText(parameters.get('poes', ''))
        self.__quantiles.setText(parameters.get('quantiles', ''))
        self.__minMagnitude.setText(parameters.get('min_magnitude', ''))
        self.__investigationTime.setText(parameters.get('investigation_time', ''))
        self.__coordinates.setText(parameters.get('grid', ''))

        self.__targetGmpeList.clear()
        gmpeList = parameters.get('gmpes_str', '').split(',')
        for gmpe in gmpeList:
            ind = gmpe.index('(')
            g = Gmpe(gmpe[:ind], float(gmpe[ind+1:len(gmpe)-1]))
            self.__addGmpeToList(g)

    def __saveConfig(self):
        targetFile = gui.QFileDialog.getSaveFileName(self, 'Select File to Save')
        if targetFile is not None and len(str(targetFile)) != 0:
            targetFileName = str(targetFile)
            parts = split(targetFileName)
            self.__lastVisited = parts[0]
            parameters = self.__prepareInputs()
            del parameters['gmpes']

            self.callFunction(lambda: save(parameters, targetFileName), 'Config file saved')

    def __loadConfig(self):
        fileDialog = gui.QFileDialog()
        sourceFile = fileDialog.getOpenFileName(self, 'Select File to Load')
        if sourceFile is not None and len(str(sourceFile)) != 0:
            sourceFileName = str(sourceFile)
            parameters, status = self.callFunction(lambda: load(sourceFileName))
            if status:
                self.__changeParameters(parameters)

    def __executeConfig(self):
        targetDir = str(self.__targetDir.getSelectedFile()).strip()
        if len(targetDir) > 0:
            parameters = self.__prepareInputs()
            self.callFunction(lambda: execute(parameters, targetDir), 'Execution successful')