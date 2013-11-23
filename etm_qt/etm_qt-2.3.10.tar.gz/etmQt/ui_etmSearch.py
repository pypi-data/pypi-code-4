# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './etmSearch.ui'
#
# Created: Wed Mar 20 10:21:17 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.setWindowModality(QtCore.Qt.NonModal)
        Form.resize(186, 33)
        Form.setStyleSheet(_fromUtf8("font-size: 10pt"))
        self.horizontalLayout = QtGui.QHBoxLayout(Form)
        self.horizontalLayout.setMargin(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.previous = QtGui.QToolButton(Form)
        self.previous.setStyleSheet(_fromUtf8("border: 0px"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/previous.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.previous.setIcon(icon)
        self.previous.setIconSize(QtCore.QSize(18, 18))
        self.previous.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.previous.setAutoRaise(True)
        self.previous.setObjectName(_fromUtf8("previous"))
        self.horizontalLayout.addWidget(self.previous)
        self.search = QtGui.QLineEdit(Form)
        self.search.setMinimumSize(QtCore.QSize(120, 0))
        self.search.setStyleSheet(_fromUtf8("padding: 0px"))
        self.search.setObjectName(_fromUtf8("search"))
        self.horizontalLayout.addWidget(self.search)
        self.next = QtGui.QToolButton(Form)
        self.next.setStyleSheet(_fromUtf8("border: 0px"))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/next.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.next.setIcon(icon1)
        self.next.setIconSize(QtCore.QSize(18, 18))
        self.next.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.next.setAutoRaise(True)
        self.next.setObjectName(_fromUtf8("next"))
        self.horizontalLayout.addWidget(self.next)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.search, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.next.animateClick)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.previous.setToolTip(QtGui.QApplication.translate("Form", "Click here or press Shift Ctrl-G to search backward.", None, QtGui.QApplication.UnicodeUTF8))
        self.previous.setText(QtGui.QApplication.translate("Form", "&Previous", None, QtGui.QApplication.UnicodeUTF8))
        self.search.setPlaceholderText(QtGui.QApplication.translate("Form", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.next.setToolTip(QtGui.QApplication.translate("Form", "Click here or press Ctrl-G to search forward.", None, QtGui.QApplication.UnicodeUTF8))
        self.next.setText(QtGui.QApplication.translate("Form", "&Next", None, QtGui.QApplication.UnicodeUTF8))

