# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'src/leap/bitmask/gui/ui/eippreferences.ui'
#
# Created: Tue Oct  1 11:53:10 2013
#      by: pyside-uic 0.2.15 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EIPPreferences(object):
    def setupUi(self, EIPPreferences):
        EIPPreferences.setObjectName("EIPPreferences")
        EIPPreferences.resize(400, 170)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/mask-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        EIPPreferences.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(EIPPreferences)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gbGatewaySelector = QtGui.QGroupBox(EIPPreferences)
        self.gbGatewaySelector.setEnabled(True)
        self.gbGatewaySelector.setCheckable(False)
        self.gbGatewaySelector.setObjectName("gbGatewaySelector")
        self.gridLayout = QtGui.QGridLayout(self.gbGatewaySelector)
        self.gridLayout.setObjectName("gridLayout")
        self.cbProvidersGateway = QtGui.QComboBox(self.gbGatewaySelector)
        self.cbProvidersGateway.setObjectName("cbProvidersGateway")
        self.cbProvidersGateway.addItem("")
        self.gridLayout.addWidget(self.cbProvidersGateway, 0, 1, 1, 2)
        self.lblSelectProvider = QtGui.QLabel(self.gbGatewaySelector)
        self.lblSelectProvider.setObjectName("lblSelectProvider")
        self.gridLayout.addWidget(self.lblSelectProvider, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.gbGatewaySelector)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.cbGateways = QtGui.QComboBox(self.gbGatewaySelector)
        self.cbGateways.setObjectName("cbGateways")
        self.cbGateways.addItem("")
        self.gridLayout.addWidget(self.cbGateways, 1, 1, 1, 2)
        self.pbSaveGateway = QtGui.QPushButton(self.gbGatewaySelector)
        self.pbSaveGateway.setObjectName("pbSaveGateway")
        self.gridLayout.addWidget(self.pbSaveGateway, 5, 2, 1, 1)
        self.lblProvidersGatewayStatus = QtGui.QLabel(self.gbGatewaySelector)
        self.lblProvidersGatewayStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.lblProvidersGatewayStatus.setObjectName("lblProvidersGatewayStatus")
        self.gridLayout.addWidget(self.lblProvidersGatewayStatus, 2, 0, 1, 3)
        self.verticalLayout.addWidget(self.gbGatewaySelector)
        self.lblSelectProvider.setBuddy(self.cbProvidersGateway)

        self.retranslateUi(EIPPreferences)
        QtCore.QMetaObject.connectSlotsByName(EIPPreferences)

    def retranslateUi(self, EIPPreferences):
        EIPPreferences.setWindowTitle(QtGui.QApplication.translate("EIPPreferences", "EIP Preferences", None, QtGui.QApplication.UnicodeUTF8))
        self.gbGatewaySelector.setTitle(QtGui.QApplication.translate("EIPPreferences", "Select gateway for provider", None, QtGui.QApplication.UnicodeUTF8))
        self.cbProvidersGateway.setItemText(0, QtGui.QApplication.translate("EIPPreferences", "<Select provider>", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSelectProvider.setText(QtGui.QApplication.translate("EIPPreferences", "&Select provider:", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EIPPreferences", "Select gateway:", None, QtGui.QApplication.UnicodeUTF8))
        self.cbGateways.setItemText(0, QtGui.QApplication.translate("EIPPreferences", "Automatic", None, QtGui.QApplication.UnicodeUTF8))
        self.pbSaveGateway.setText(QtGui.QApplication.translate("EIPPreferences", "Save this provider settings", None, QtGui.QApplication.UnicodeUTF8))
        self.lblProvidersGatewayStatus.setText(QtGui.QApplication.translate("EIPPreferences", "< Providers Gateway Status >", None, QtGui.QApplication.UnicodeUTF8))

import mainwindow_rc
