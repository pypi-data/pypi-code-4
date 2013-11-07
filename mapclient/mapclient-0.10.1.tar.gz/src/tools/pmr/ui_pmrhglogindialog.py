# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/pmrhglogindialog.ui'
#
# Created: Mon Jun 24 21:56:09 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PMRHgLoginDialog(object):
    def setupUi(self, PMRHgLoginDialog):
        PMRHgLoginDialog.setObjectName("PMRHgLoginDialog")
        PMRHgLoginDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(PMRHgLoginDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(PMRHgLoginDialog)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.usernameLineEdit = QtGui.QLineEdit(self.groupBox)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.usernameLineEdit)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.passwordLineEdit = QtGui.QLineEdit(self.groupBox)
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.passwordLineEdit)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(PMRHgLoginDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.usernameLineEdit)
        self.label_2.setBuddy(self.passwordLineEdit)

        self.retranslateUi(PMRHgLoginDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), PMRHgLoginDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PMRHgLoginDialog)
        PMRHgLoginDialog.setTabOrder(self.usernameLineEdit, self.passwordLineEdit)
        PMRHgLoginDialog.setTabOrder(self.passwordLineEdit, self.buttonBox)

    def retranslateUi(self, PMRHgLoginDialog):
        PMRHgLoginDialog.setWindowTitle(QtGui.QApplication.translate("PMRHgLoginDialog", "PMR Mercurial Login", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PMRHgLoginDialog", "PMR Mercurial Login", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PMRHgLoginDialog", "username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PMRHgLoginDialog", "password:", None, QtGui.QApplication.UnicodeUTF8))

