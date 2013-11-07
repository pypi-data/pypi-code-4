# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/pluginmanagerdialog.ui'
#
# Created: Thu Oct 10 15:24:46 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_PluginManagerDialog(object):
    def setupUi(self, PluginManagerDialog):
        PluginManagerDialog.setObjectName("PluginManagerDialog")
        PluginManagerDialog.resize(567, 496)
        self.verticalLayout = QtGui.QVBoxLayout(PluginManagerDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtGui.QGroupBox(PluginManagerDialog)
        self.groupBox.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox.setFlat(False)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.directoryListing = QtGui.QListWidget(self.groupBox)
        self.directoryListing.setObjectName("directoryListing")
        self.verticalLayout_3.addWidget(self.directoryListing)
        self.defaultPluginCheckBox = QtGui.QCheckBox(self.groupBox)
        self.defaultPluginCheckBox.setChecked(True)
        self.defaultPluginCheckBox.setObjectName("defaultPluginCheckBox")
        self.verticalLayout_3.addWidget(self.defaultPluginCheckBox)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.addButton = QtGui.QPushButton(self.groupBox)
        self.addButton.setObjectName("addButton")
        self.verticalLayout_2.addWidget(self.addButton)
        self.removeButton = QtGui.QPushButton(self.groupBox)
        self.removeButton.setObjectName("removeButton")
        self.verticalLayout_2.addWidget(self.removeButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.reloadButton = QtGui.QPushButton(self.groupBox)
        self.reloadButton.setObjectName("reloadButton")
        self.verticalLayout_2.addWidget(self.reloadButton)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtGui.QDialogButtonBox(PluginManagerDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PluginManagerDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), PluginManagerDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), PluginManagerDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PluginManagerDialog)

    def retranslateUi(self, PluginManagerDialog):
        PluginManagerDialog.setWindowTitle(QtGui.QApplication.translate("PluginManagerDialog", "Plugin Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("PluginManagerDialog", "Plugin Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("PluginManagerDialog", "Plugin directories:", None, QtGui.QApplication.UnicodeUTF8))
        self.defaultPluginCheckBox.setText(QtGui.QApplication.translate("PluginManagerDialog", "Use default plugin directory", None, QtGui.QApplication.UnicodeUTF8))
        self.addButton.setText(QtGui.QApplication.translate("PluginManagerDialog", "Add Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.removeButton.setText(QtGui.QApplication.translate("PluginManagerDialog", "Remove Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setToolTip(QtGui.QApplication.translate("PluginManagerDialog", "Reload the plugins from the current plugin directories", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setText(QtGui.QApplication.translate("PluginManagerDialog", "Reload", None, QtGui.QApplication.UnicodeUTF8))

