# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/pmrhgcommitdialog.ui'
#
# Created: Thu Jun 27 14:17:03 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PMRHgCommitDialog(object):
    def setupUi(self, PMRHgCommitDialog):
        PMRHgCommitDialog.setObjectName("PMRHgCommitDialog")
        PMRHgCommitDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(PMRHgCommitDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(PMRHgCommitDialog)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName("formLayout")
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_3)
        self.commentTextEdit = QtGui.QPlainTextEdit(self.groupBox)
        self.commentTextEdit.setObjectName("commentTextEdit")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.commentTextEdit)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.usernameLineEdit = QtGui.QLineEdit(self.groupBox)
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.usernameLineEdit)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_2)
        self.passwordLineEdit = QtGui.QLineEdit(self.groupBox)
        self.passwordLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.passwordLineEdit)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(PMRHgCommitDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label_3.setBuddy(self.commentTextEdit)
        self.label.setBuddy(self.usernameLineEdit)
        self.label_2.setBuddy(self.passwordLineEdit)

        self.retranslateUi(PMRHgCommitDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), PMRHgCommitDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PMRHgCommitDialog)
        PMRHgCommitDialog.setTabOrder(self.commentTextEdit, self.usernameLineEdit)
        PMRHgCommitDialog.setTabOrder(self.usernameLineEdit, self.passwordLineEdit)
        PMRHgCommitDialog.setTabOrder(self.passwordLineEdit, self.buttonBox)

    def retranslateUi(self, PMRHgCommitDialog):
        PMRHgCommitDialog.setWindowTitle(QtGui.QApplication.translate("PMRHgCommitDialog", "PMR Mercurial Commit", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PMRHgCommitDialog", "PMR Mercurial Commit", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("PMRHgCommitDialog", "comment:", None, QtGui.QApplication.UnicodeUTF8))
        self.commentTextEdit.setPlainText(QtGui.QApplication.translate("PMRHgCommitDialog", "Lazy commit message from MAP Client user.", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PMRHgCommitDialog", "username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("PMRHgCommitDialog", "password:", None, QtGui.QApplication.UnicodeUTF8))

