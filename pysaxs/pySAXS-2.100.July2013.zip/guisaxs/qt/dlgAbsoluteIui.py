# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgAbsoluteI.ui'
#
# Created: Fri Jun 14 13:42:20 2013
#      by: PyQt4 UI code generator 4.9.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_dlgSAXSAbsolute(object):
    def setupUi(self, dlgSAXSAbsolute):
        dlgSAXSAbsolute.setObjectName(_fromUtf8("dlgSAXSAbsolute"))
        dlgSAXSAbsolute.resize(417, 553)
        dlgSAXSAbsolute.setMinimumSize(QtCore.QSize(0, 553))
        self.verticalLayout = QtGui.QVBoxLayout(dlgSAXSAbsolute)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelDataset = QtGui.QLabel(dlgSAXSAbsolute)
        self.labelDataset.setMinimumSize(QtCore.QSize(0, 20))
        self.labelDataset.setBaseSize(QtCore.QSize(0, 0))
        self.labelDataset.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.labelDataset.setObjectName(_fromUtf8("labelDataset"))
        self.verticalLayout.addWidget(self.labelDataset)
        self.groupBox = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkQrange = QtGui.QCheckBox(self.groupBox_2)
        self.checkQrange.setObjectName(_fromUtf8("checkQrange"))
        self.horizontalLayout.addWidget(self.checkQrange)
        self.checkIrange = QtGui.QCheckBox(self.groupBox_2)
        self.checkIrange.setObjectName(_fromUtf8("checkIrange"))
        self.horizontalLayout.addWidget(self.checkIrange)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBoxReference = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBoxReference.setEnabled(True)
        self.groupBoxReference.setObjectName(_fromUtf8("groupBoxReference"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBoxReference)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.checkSubstractRef = QtGui.QCheckBox(self.groupBoxReference)
        self.checkSubstractRef.setObjectName(_fromUtf8("checkSubstractRef"))
        self.horizontalLayout_2.addWidget(self.checkSubstractRef)
        self.txtReference = QtGui.QLineEdit(self.groupBoxReference)
        self.txtReference.setObjectName(_fromUtf8("txtReference"))
        self.horizontalLayout_2.addWidget(self.txtReference)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.label = QtGui.QLabel(self.groupBoxReference)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout.addWidget(self.groupBoxReference)
        self.buttonBox = QtGui.QDialogButtonBox(dlgSAXSAbsolute)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Open|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgSAXSAbsolute)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgSAXSAbsolute.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgSAXSAbsolute)

    def retranslateUi(self, dlgSAXSAbsolute):
        dlgSAXSAbsolute.setWindowTitle(QtGui.QApplication.translate("dlgSAXSAbsolute", "Absolute Intensities", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDataset.setText(QtGui.QApplication.translate("dlgSAXSAbsolute", "dataset", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("dlgSAXSAbsolute", "Parameters :", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("dlgSAXSAbsolute", "Scaling", None, QtGui.QApplication.UnicodeUTF8))
        self.checkQrange.setText(QtGui.QApplication.translate("dlgSAXSAbsolute", "scaling Q range", None, QtGui.QApplication.UnicodeUTF8))
        self.checkIrange.setText(QtGui.QApplication.translate("dlgSAXSAbsolute", "scaling I range", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBoxReference.setTitle(QtGui.QApplication.translate("dlgSAXSAbsolute", "Automatic reference substraction* :", None, QtGui.QApplication.UnicodeUTF8))
        self.checkSubstractRef.setText(QtGui.QApplication.translate("dlgSAXSAbsolute", "substract reference :", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("dlgSAXSAbsolute", "* Datas must have the same size. Use Calculator tool instead. ", None, QtGui.QApplication.UnicodeUTF8))

