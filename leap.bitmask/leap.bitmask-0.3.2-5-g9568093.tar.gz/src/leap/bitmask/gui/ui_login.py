# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/leap/bitmask/gui/ui/login.ui'
#
# Created: Wed Sep 11 16:37:39 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_LoginWidget(object):
    def setupUi(self, LoginWidget):
        LoginWidget.setObjectName("LoginWidget")
        LoginWidget.resize(356, 223)
        self.gridLayout = QtGui.QGridLayout(LoginWidget)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.cmbProviders = QtGui.QComboBox(LoginWidget)
        self.cmbProviders.setObjectName("cmbProviders")
        self.gridLayout.addWidget(self.cmbProviders, 1, 1, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 5, 0, 1, 1)
        self.btnCreateAccount = QtGui.QPushButton(LoginWidget)
        self.btnCreateAccount.setObjectName("btnCreateAccount")
        self.gridLayout.addWidget(self.btnCreateAccount, 6, 1, 1, 1)
        self.label_4 = QtGui.QLabel(LoginWidget)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.lnPassword = QtGui.QLineEdit(LoginWidget)
        self.lnPassword.setInputMask("")
        self.lnPassword.setObjectName("lnPassword")
        self.gridLayout.addWidget(self.lnPassword, 3, 1, 1, 2)
        self.lnUser = QtGui.QLineEdit(LoginWidget)
        self.lnUser.setObjectName("lnUser")
        self.gridLayout.addWidget(self.lnUser, 2, 1, 1, 2)
        self.chkRemember = QtGui.QCheckBox(LoginWidget)
        self.chkRemember.setObjectName("chkRemember")
        self.gridLayout.addWidget(self.chkRemember, 4, 1, 1, 2)
        self.label_2 = QtGui.QLabel(LoginWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.label_3 = QtGui.QLabel(LoginWidget)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.btnLogin = QtGui.QPushButton(LoginWidget)
        self.btnLogin.setObjectName("btnLogin")
        self.gridLayout.addWidget(self.btnLogin, 5, 1, 1, 1)
        self.lblStatus = QtGui.QLabel(LoginWidget)
        self.lblStatus.setText("")
        self.lblStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.lblStatus.setWordWrap(True)
        self.lblStatus.setObjectName("lblStatus")
        self.gridLayout.addWidget(self.lblStatus, 0, 0, 1, 3)

        self.retranslateUi(LoginWidget)
        QtCore.QMetaObject.connectSlotsByName(LoginWidget)
        LoginWidget.setTabOrder(self.cmbProviders, self.lnUser)
        LoginWidget.setTabOrder(self.lnUser, self.lnPassword)
        LoginWidget.setTabOrder(self.lnPassword, self.chkRemember)
        LoginWidget.setTabOrder(self.chkRemember, self.btnLogin)
        LoginWidget.setTabOrder(self.btnLogin, self.btnCreateAccount)

    def retranslateUi(self, LoginWidget):
        LoginWidget.setWindowTitle(QtGui.QApplication.translate("LoginWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnCreateAccount.setText(QtGui.QApplication.translate("LoginWidget", "Create a new account", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("LoginWidget", "<b>Provider:</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.chkRemember.setText(QtGui.QApplication.translate("LoginWidget", "Remember username and password", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("LoginWidget", "<b>Username:</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("LoginWidget", "<b>Password:</b>", None, QtGui.QApplication.UnicodeUTF8))
        self.btnLogin.setText(QtGui.QApplication.translate("LoginWidget", "Log In", None, QtGui.QApplication.UnicodeUTF8))

