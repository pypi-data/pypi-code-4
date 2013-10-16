# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmCalendars.ui'
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
        Dialog.resize(268, 159)
        Dialog.setStyleSheet(_fromUtf8("font-size: 10pt"))
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setContentsMargins(8, -1, 8, 6)
        self.gridLayout.setVerticalSpacing(8)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 1, 1, 1, 2)
        self.calendarBox = QtGui.QGroupBox(Dialog)
        self.calendarBox.setStatusTip(_fromUtf8(""))
        self.calendarBox.setStyleSheet(_fromUtf8(""))
        self.calendarBox.setObjectName(_fromUtf8("calendarBox"))
        self.gridLayout.addWidget(self.calendarBox, 0, 0, 1, 3)
        self.gridLayout.setRowStretch(0, 1)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Calendars", None, QtGui.QApplication.UnicodeUTF8))
        self.calendarBox.setToolTip(QtGui.QApplication.translate("Dialog", "Click here or press Ctrl-E to export the selected calendars.", None, QtGui.QApplication.UnicodeUTF8))
        self.calendarBox.setTitle(QtGui.QApplication.translate("Dialog", "Limit display to selected calendars", None, QtGui.QApplication.UnicodeUTF8))

