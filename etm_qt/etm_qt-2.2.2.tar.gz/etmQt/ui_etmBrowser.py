# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmBrowser.ui'
#
# Created: Wed Mar 20 10:21:16 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(497, 179)
        Dialog.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        Dialog.setStyleSheet(_fromUtf8("font-size:10pt"))
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setMargin(6)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.browserWindow = QtGui.QTextBrowser(Dialog)
        self.browserWindow.setObjectName(_fromUtf8("browserWindow"))
        self.gridLayout.addWidget(self.browserWindow, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "etm", None, QtGui.QApplication.UnicodeUTF8))

