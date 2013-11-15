# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/leap/bitmask/gui/ui/advanced_key_management.ui'
#
# Created: Fri Nov 15 08:39:16 2013
#      by: pyside-uic 0.2.15 running on PySide 1.2.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_AdvancedKeyManagement(object):
    def setupUi(self, AdvancedKeyManagement):
        AdvancedKeyManagement.setObjectName("AdvancedKeyManagement")
        AdvancedKeyManagement.resize(431, 188)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/mask-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        AdvancedKeyManagement.setWindowIcon(icon)
        self.gridLayout_3 = QtGui.QGridLayout(AdvancedKeyManagement)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.container = QtGui.QWidget(AdvancedKeyManagement)
        self.container.setObjectName("container")
        self.gridLayout_2 = QtGui.QGridLayout(self.container)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self.container)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.leUser = QtGui.QLineEdit(self.container)
        self.leUser.setEnabled(True)
        self.leUser.setAlignment(QtCore.Qt.AlignCenter)
        self.leUser.setReadOnly(True)
        self.leUser.setObjectName("leUser")
        self.gridLayout_2.addWidget(self.leUser, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.container)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.leKeyID = QtGui.QLineEdit(self.container)
        self.leKeyID.setEnabled(True)
        self.leKeyID.setAlignment(QtCore.Qt.AlignCenter)
        self.leKeyID.setReadOnly(True)
        self.leKeyID.setObjectName("leKeyID")
        self.gridLayout_2.addWidget(self.leKeyID, 1, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.container)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 2, 0, 1, 1)
        self.leFingerprint = QtGui.QLineEdit(self.container)
        self.leFingerprint.setEnabled(True)
        self.leFingerprint.setAlignment(QtCore.Qt.AlignCenter)
        self.leFingerprint.setReadOnly(True)
        self.leFingerprint.setObjectName("leFingerprint")
        self.gridLayout_2.addWidget(self.leFingerprint, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 1, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pbExportKeys = QtGui.QPushButton(self.container)
        self.pbExportKeys.setObjectName("pbExportKeys")
        self.gridLayout.addWidget(self.pbExportKeys, 1, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 0, 2, 1)
        self.pbImportKeys = QtGui.QPushButton(self.container)
        self.pbImportKeys.setObjectName("pbImportKeys")
        self.gridLayout.addWidget(self.pbImportKeys, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 4, 0, 1, 2)
        self.gridLayout_3.addWidget(self.container, 0, 0, 1, 1)
        self.lblStatus = QtGui.QLabel(AdvancedKeyManagement)
        self.lblStatus.setText("")
        self.lblStatus.setObjectName("lblStatus")
        self.gridLayout_3.addWidget(self.lblStatus, 1, 0, 1, 1)

        self.retranslateUi(AdvancedKeyManagement)
        QtCore.QMetaObject.connectSlotsByName(AdvancedKeyManagement)

    def retranslateUi(self, AdvancedKeyManagement):
        AdvancedKeyManagement.setWindowTitle(QtGui.QApplication.translate("AdvancedKeyManagement", "Advanced Key Management", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "User:", None, QtGui.QApplication.UnicodeUTF8))
        self.leUser.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "user_name@provider", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "Key ID:", None, QtGui.QApplication.UnicodeUTF8))
        self.leKeyID.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "key ID", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "Key fingerprint:", None, QtGui.QApplication.UnicodeUTF8))
        self.leFingerprint.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "fingerprint", None, QtGui.QApplication.UnicodeUTF8))
        self.pbExportKeys.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "Export current key pair", None, QtGui.QApplication.UnicodeUTF8))
        self.pbImportKeys.setText(QtGui.QApplication.translate("AdvancedKeyManagement", "Import custom key pair", None, QtGui.QApplication.UnicodeUTF8))

import mainwindow_rc
