# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgQtFAI.ui'
#
# Created: Wed Feb 27 15:46:23 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FAIDialog(object):
    def setupUi(self, FAIDialog):
        FAIDialog.setObjectName(_fromUtf8("FAIDialog"))
        FAIDialog.resize(430, 400)
        self.Par = QtGui.QGroupBox(FAIDialog)
        self.Par.setGeometry(QtCore.QRect(9, 9, 411, 50))
        self.Par.setMinimumSize(QtCore.QSize(0, 50))
        self.Par.setMaximumSize(QtCore.QSize(16777215, 50))
        self.Par.setObjectName(_fromUtf8("Par"))
        self.paramTxt = QtGui.QLineEdit(self.Par)
        self.paramTxt.setGeometry(QtCore.QRect(10, 20, 291, 20))
        self.paramTxt.setObjectName(_fromUtf8("paramTxt"))
        self.paramFileButton = QtGui.QPushButton(self.Par)
        self.paramFileButton.setGeometry(QtCore.QRect(310, 20, 41, 23))
        self.paramFileButton.setObjectName(_fromUtf8("paramFileButton"))
        self.paramViewButton = QtGui.QPushButton(self.Par)
        self.paramViewButton.setEnabled(False)
        self.paramViewButton.setGeometry(QtCore.QRect(360, 20, 41, 23))
        self.paramViewButton.setObjectName(_fromUtf8("paramViewButton"))
        self.groupBox = QtGui.QGroupBox(FAIDialog)
        self.groupBox.setGeometry(QtCore.QRect(9, 65, 411, 241))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.listWidget = QtGui.QListWidget(self.groupBox)
        self.listWidget.setGeometry(QtCore.QRect(10, 20, 291, 211))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.addButton = QtGui.QPushButton(self.groupBox)
        self.addButton.setGeometry(QtCore.QRect(310, 20, 91, 23))
        self.addButton.setObjectName(_fromUtf8("addButton"))
        self.buttonClearList = QtGui.QPushButton(self.groupBox)
        self.buttonClearList.setGeometry(QtCore.QRect(310, 80, 91, 23))
        self.buttonClearList.setObjectName(_fromUtf8("buttonClearList"))
        self.buttonRemove = QtGui.QPushButton(self.groupBox)
        self.buttonRemove.setGeometry(QtCore.QRect(310, 50, 91, 23))
        self.buttonRemove.setObjectName(_fromUtf8("buttonRemove"))
        self.buttonViewImage = QtGui.QPushButton(self.groupBox)
        self.buttonViewImage.setGeometry(QtCore.QRect(310, 120, 91, 23))
        self.buttonViewImage.setObjectName(_fromUtf8("buttonViewImage"))
        self.groupBox_2 = QtGui.QGroupBox(FAIDialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 310, 411, 50))
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.outputDirTxt = QtGui.QLineEdit(self.groupBox_2)
        self.outputDirTxt.setGeometry(QtCore.QRect(20, 20, 301, 20))
        self.outputDirTxt.setObjectName(_fromUtf8("outputDirTxt"))
        self.changeOutputDirButton = QtGui.QPushButton(self.groupBox_2)
        self.changeOutputDirButton.setGeometry(QtCore.QRect(360, 20, 41, 23))
        self.changeOutputDirButton.setObjectName(_fromUtf8("changeOutputDirButton"))
        self.buttonClose = QtGui.QDialogButtonBox(FAIDialog)
        self.buttonClose.setGeometry(QtCore.QRect(11, 370, 61, 23))
        self.buttonClose.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonClose.setObjectName(_fromUtf8("buttonClose"))
        self.progressBar = QtGui.QProgressBar(FAIDialog)
        self.progressBar.setGeometry(QtCore.QRect(218, 370, 201, 21))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.RADButton = QtGui.QPushButton(FAIDialog)
        self.RADButton.setGeometry(QtCore.QRect(110, 370, 91, 23))
        self.RADButton.setObjectName(_fromUtf8("RADButton"))

        self.retranslateUi(FAIDialog)
        QtCore.QObject.connect(self.buttonClose, QtCore.SIGNAL(_fromUtf8("clicked(QAbstractButton*)")), FAIDialog.close)
        QtCore.QMetaObject.connectSlotsByName(FAIDialog)

    def retranslateUi(self, FAIDialog):
        FAIDialog.setWindowTitle(QtGui.QApplication.translate("FAIDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.Par.setTitle(QtGui.QApplication.translate("FAIDialog", "Parameters file", None, QtGui.QApplication.UnicodeUTF8))
        self.paramFileButton.setText(QtGui.QApplication.translate("FAIDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.paramViewButton.setText(QtGui.QApplication.translate("FAIDialog", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("FAIDialog", "Data :", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("FAIDialog", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonClearList.setText(QtGui.QApplication.translate("FAIDialog", "Clear list", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRemove.setText(QtGui.QApplication.translate("FAIDialog", "Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonViewImage.setText(QtGui.QApplication.translate("FAIDialog", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("FAIDialog", "Output directory :", None, QtGui.QApplication.UnicodeUTF8))
        self.changeOutputDirButton.setText(QtGui.QApplication.translate("FAIDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.RADButton.setText(QtGui.QApplication.translate("FAIDialog", "Radial average", None, QtGui.QApplication.UnicodeUTF8))

