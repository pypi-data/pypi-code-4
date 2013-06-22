# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/import.ui'
#
# Created: Sat Jun 22 12:53:38 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Import(object):
    def setupUi(self, Import):
        Import.setObjectName(_fromUtf8("Import"))
        Import.resize(672, 504)
        self.gridLayout = QtGui.QGridLayout(Import)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Import)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.accountTypeComboBox = QtGui.QComboBox(Import)
        self.accountTypeComboBox.setObjectName(_fromUtf8("accountTypeComboBox"))
        self.gridLayout.addWidget(self.accountTypeComboBox, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(469, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.view = QtGui.QTableView(Import)
        self.view.setObjectName(_fromUtf8("view"))
        self.gridLayout.addWidget(self.view, 1, 0, 1, 3)
        self.frame = QtGui.QFrame(Import)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_4 = QtGui.QLabel(self.frame)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout.addWidget(self.label_4)
        self.selectedCounter = QtGui.QLabel(self.frame)
        self.selectedCounter.setObjectName(_fromUtf8("selectedCounter"))
        self.horizontalLayout.addWidget(self.selectedCounter)
        spacerItem1 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.label_5 = QtGui.QLabel(self.frame)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout.addWidget(self.label_5)
        self.toImportCounter = QtGui.QLabel(self.frame)
        self.toImportCounter.setObjectName(_fromUtf8("toImportCounter"))
        self.horizontalLayout.addWidget(self.toImportCounter)
        spacerItem2 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.importedCounter = QtGui.QLabel(self.frame)
        self.importedCounter.setObjectName(_fromUtf8("importedCounter"))
        self.horizontalLayout.addWidget(self.importedCounter)
        spacerItem3 = QtGui.QSpacerItem(130, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.label_3 = QtGui.QLabel(self.frame)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout.addWidget(self.label_3)
        self.errorsCounter = QtGui.QLabel(self.frame)
        self.errorsCounter.setObjectName(_fromUtf8("errorsCounter"))
        self.horizontalLayout.addWidget(self.errorsCounter)
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 3)
        self.CsvImport = QtGui.QWidget(Import)
        self.CsvImport.setObjectName(_fromUtf8("CsvImport"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.CsvImport)
        self.horizontalLayout_2.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.progressBar = QtGui.QProgressBar(self.CsvImport)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout_2.addWidget(self.progressBar)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.selectAllButton = QtGui.QPushButton(self.CsvImport)
        self.selectAllButton.setObjectName(_fromUtf8("selectAllButton"))
        self.horizontalLayout_2.addWidget(self.selectAllButton)
        self.importCancelButton = QtGui.QPushButton(self.CsvImport)
        self.importCancelButton.setObjectName(_fromUtf8("importCancelButton"))
        self.horizontalLayout_2.addWidget(self.importCancelButton)
        self.closeButton = QtGui.QPushButton(self.CsvImport)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.horizontalLayout_2.addWidget(self.closeButton)
        self.gridLayout.addWidget(self.CsvImport, 3, 0, 1, 3)

        self.retranslateUi(Import)
        QtCore.QMetaObject.connectSlotsByName(Import)

    def retranslateUi(self, Import):
        Import.setWindowTitle(_translate("Import", "Import CSV", None))
        self.label_2.setText(_translate("Import", "Select account", None))
        self.label_4.setText(_translate("Import", "selected:", None))
        self.selectedCounter.setText(_translate("Import", "0", None))
        self.label_5.setText(_translate("Import", "available:", None))
        self.toImportCounter.setText(_translate("Import", "0", None))
        self.label.setText(_translate("Import", "imported:", None))
        self.importedCounter.setText(_translate("Import", "0", None))
        self.label_3.setText(_translate("Import", "errors:", None))
        self.errorsCounter.setText(_translate("Import", "0", None))
        self.selectAllButton.setText(_translate("Import", "Select all", None))
        self.importCancelButton.setText(_translate("Import", "&Import", None))
        self.closeButton.setText(_translate("Import", "&Close", None))

import pydosh_rc
