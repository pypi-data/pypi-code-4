# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmWhich.ui'
#
# Created: Mon Feb 25 09:05:38 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_whichDialog(object):
    def setupUi(self, whichDialog):
        whichDialog.setObjectName(_fromUtf8("whichDialog"))
        whichDialog.resize(436, 136)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(whichDialog.sizePolicy().hasHeightForWidth())
        whichDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(whichDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.theQuestion = QtGui.QLabel(whichDialog)
        self.theQuestion.setObjectName(_fromUtf8("theQuestion"))
        self.gridLayout.addWidget(self.theQuestion, 0, 0, 1, 1)
        self.comboBox = QtGui.QComboBox(whichDialog)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout.addWidget(self.comboBox, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(whichDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(whichDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), whichDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), whichDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(whichDialog)

    def retranslateUi(self, whichDialog):
        whichDialog.setWindowTitle(QtGui.QApplication.translate("whichDialog", "which", None, QtGui.QApplication.UnicodeUTF8))
        self.theQuestion.setText(QtGui.QApplication.translate("whichDialog", "You have selected instance ...", None, QtGui.QApplication.UnicodeUTF8))

