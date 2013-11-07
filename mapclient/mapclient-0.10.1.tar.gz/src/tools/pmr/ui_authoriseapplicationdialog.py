# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/authoriseapplicationdialog.ui'
#
# Created: Thu Jun 20 17:39:33 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AuthoriseApplicationDialog(object):
    def setupUi(self, AuthoriseApplicationDialog):
        AuthoriseApplicationDialog.setObjectName("AuthoriseApplicationDialog")
        AuthoriseApplicationDialog.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(AuthoriseApplicationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(AuthoriseApplicationDialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.tokenLineEdit = QtGui.QLineEdit(self.groupBox)
        self.tokenLineEdit.setObjectName("tokenLineEdit")
        self.verticalLayout_2.addWidget(self.tokenLineEdit)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(AuthoriseApplicationDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AuthoriseApplicationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), AuthoriseApplicationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), AuthoriseApplicationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AuthoriseApplicationDialog)

    def retranslateUi(self, AuthoriseApplicationDialog):
        AuthoriseApplicationDialog.setWindowTitle(QtGui.QApplication.translate("AuthoriseApplicationDialog", "Authorise Application", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("AuthoriseApplicationDialog", "Authorise Application", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AuthoriseApplicationDialog", "Paste authorisation token here:", None, QtGui.QApplication.UnicodeUTF8))

