# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/workflowwidget.ui'
#
# Created: Fri Jun 14 11:25:00 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_WorkflowWidget(object):
    def setupUi(self, WorkflowWidget):
        WorkflowWidget.setObjectName("WorkflowWidget")
        WorkflowWidget.resize(574, 399)
        WorkflowWidget.setWindowTitle("")
        self.gridLayout = QtGui.QGridLayout(WorkflowWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.splitter = QtGui.QSplitter(WorkflowWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.stepTree = StepTree(self.splitter)
        self.stepTree.setObjectName("stepTree")
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.graphicsView = WorkflowGraphicsView(self.widget)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.executeButton = QtGui.QPushButton(self.widget)
        self.executeButton.setObjectName("executeButton")
        self.horizontalLayout.addWidget(self.executeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(WorkflowWidget)
        QtCore.QMetaObject.connectSlotsByName(WorkflowWidget)

    def retranslateUi(self, WorkflowWidget):
        self.executeButton.setText(QtGui.QApplication.translate("WorkflowWidget", "E&xecute", None, QtGui.QApplication.UnicodeUTF8))

from widgets.steptree import StepTree
from widgets.workflowgraphicsview import WorkflowGraphicsView
