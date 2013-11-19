# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './vizmdend.ui'
#
# Created: Sun Nov  3 18:22:24 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Vizmdend(object):
    def setupUi(self, Vizmdend):
        Vizmdend.setObjectName(_fromUtf8("Vizmdend"))
        Vizmdend.resize(738, 676)
        self.embedGraph = QtGui.QWidget(Vizmdend)
        self.embedGraph.setGeometry(QtCore.QRect(30, 130, 641, 501))
        self.embedGraph.setObjectName(_fromUtf8("embedGraph"))
        self.widget = QtGui.QWidget(Vizmdend)
        self.widget.setGeometry(QtCore.QRect(24, 60, 126, 29))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.yFieldLabel = QtGui.QLabel(self.widget)
        self.yFieldLabel.setObjectName(_fromUtf8("yFieldLabel"))
        self.horizontalLayout_2.addWidget(self.yFieldLabel)
        self.yComboBox = QtGui.QComboBox(self.widget)
        self.yComboBox.setObjectName(_fromUtf8("yComboBox"))
        self.horizontalLayout_2.addWidget(self.yComboBox)
        self.widget1 = QtGui.QWidget(Vizmdend)
        self.widget1.setGeometry(QtCore.QRect(25, 90, 126, 29))
        self.widget1.setObjectName(_fromUtf8("widget1"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.widget1)
        self.horizontalLayout_3.setMargin(0)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.xFieldLabel = QtGui.QLabel(self.widget1)
        self.xFieldLabel.setObjectName(_fromUtf8("xFieldLabel"))
        self.horizontalLayout_3.addWidget(self.xFieldLabel)
        self.xComboBox = QtGui.QComboBox(self.widget1)
        self.xComboBox.setObjectName(_fromUtf8("xComboBox"))
        self.horizontalLayout_3.addWidget(self.xComboBox)
        self.plotButton = QtGui.QPushButton(Vizmdend)
        self.plotButton.setGeometry(QtCore.QRect(191, 58, 85, 27))
        self.plotButton.setObjectName(_fromUtf8("plotButton"))
        self.closeButton = QtGui.QPushButton(Vizmdend)
        self.closeButton.setGeometry(QtCore.QRect(191, 91, 85, 27))
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.widget2 = QtGui.QWidget(Vizmdend)
        self.widget2.setGeometry(QtCore.QRect(25, 26, 551, 29))
        self.widget2.setObjectName(_fromUtf8("widget2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.fileLabel = QtGui.QLabel(self.widget2)
        self.fileLabel.setObjectName(_fromUtf8("fileLabel"))
        self.horizontalLayout.addWidget(self.fileLabel)
        self.filenameEdit = QtGui.QLineEdit(self.widget2)
        self.filenameEdit.setObjectName(_fromUtf8("filenameEdit"))
        self.horizontalLayout.addWidget(self.filenameEdit)
        self.browseButton = QtGui.QPushButton(Vizmdend)
        self.browseButton.setGeometry(QtCore.QRect(580, 30, 85, 27))
        self.browseButton.setObjectName(_fromUtf8("browseButton"))

        self.retranslateUi(Vizmdend)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), Vizmdend.reject)
        QtCore.QMetaObject.connectSlotsByName(Vizmdend)

    def retranslateUi(self, Vizmdend):
        Vizmdend.setWindowTitle(QtGui.QApplication.translate("Vizmdend", "Plot mdend", None, QtGui.QApplication.UnicodeUTF8))
        self.yFieldLabel.setText(QtGui.QApplication.translate("Vizmdend", "yField", None, QtGui.QApplication.UnicodeUTF8))
        self.xFieldLabel.setText(QtGui.QApplication.translate("Vizmdend", "xField", None, QtGui.QApplication.UnicodeUTF8))
        self.plotButton.setText(QtGui.QApplication.translate("Vizmdend", "Plot", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("Vizmdend", "Close", None, QtGui.QApplication.UnicodeUTF8))
        self.fileLabel.setText(QtGui.QApplication.translate("Vizmdend", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.browseButton.setText(QtGui.QApplication.translate("Vizmdend", "Browse", None, QtGui.QApplication.UnicodeUTF8))

