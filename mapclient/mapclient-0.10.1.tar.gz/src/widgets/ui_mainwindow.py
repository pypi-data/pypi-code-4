# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/mainwindow.ui'
#
# Created: Wed Oct 30 13:52:47 2013
#      by: pyside-uic 0.2.14 running on PySide 1.1.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/mapclient/images/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stackedWidget = QtGui.QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.horizontalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 19))
        self.menubar.setObjectName("menubar")
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menu_Edit = QtGui.QMenu(self.menubar)
        self.menu_Edit.setObjectName("menu_Edit")
        self.menu_Tools = QtGui.QMenu(self.menubar)
        self.menu_Tools.setObjectName("menu_Tools")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_About = QtGui.QAction(MainWindow)
        self.action_About.setObjectName("action_About")
        self.action_Quit = QtGui.QAction(MainWindow)
        self.action_Quit.setObjectName("action_Quit")
        self.actionPluginManager = QtGui.QAction(MainWindow)
        self.actionPluginManager.setObjectName("actionPluginManager")
        self.actionPMR = QtGui.QAction(MainWindow)
        self.actionPMR.setObjectName("actionPMR")
        self.actionAnnotation = QtGui.QAction(MainWindow)
        self.actionAnnotation.setObjectName("actionAnnotation")
        self.actionPluginWizard = QtGui.QAction(MainWindow)
        self.actionPluginWizard.setObjectName("actionPluginWizard")
        self.menu_Help.addAction(self.action_About)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menu_Tools.addAction(self.actionPluginManager)
        self.menu_Tools.addAction(self.actionPluginWizard)
        self.menu_Tools.addAction(self.actionPMR)
        self.menu_Tools.addAction(self.actionAnnotation)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_Tools.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MAP Client", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Help.setTitle(QtGui.QApplication.translate("MainWindow", "&Help", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_File.setTitle(QtGui.QApplication.translate("MainWindow", "&File", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Edit.setTitle(QtGui.QApplication.translate("MainWindow", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menu_Tools.setTitle(QtGui.QApplication.translate("MainWindow", "&Tools", None, QtGui.QApplication.UnicodeUTF8))
        self.action_About.setText(QtGui.QApplication.translate("MainWindow", "&About", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setText(QtGui.QApplication.translate("MainWindow", "&Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setStatusTip(QtGui.QApplication.translate("MainWindow", "Quit the application", None, QtGui.QApplication.UnicodeUTF8))
        self.action_Quit.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+Q", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPluginManager.setText(QtGui.QApplication.translate("MainWindow", "Plugin &Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPMR.setText(QtGui.QApplication.translate("MainWindow", "&PMR", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAnnotation.setText(QtGui.QApplication.translate("MainWindow", "&Annotation", None, QtGui.QApplication.UnicodeUTF8))
        self.actionPluginWizard.setText(QtGui.QApplication.translate("MainWindow", "Plugin Wi&zard", None, QtGui.QApplication.UnicodeUTF8))

from . import resources_rc
