#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
# import sip
# sip.setapi('QVariant', 2)

from PySide import QtCore, QtGui
import os, signal
from os.path import expanduser
import ConfigParser
from transporter import client
from multiprocessing import Process, Pipe
import platform

on_windows = platform.system() == 'Windows'
on_macos = platform.system() == 'Darwin'
on_linux = platform.system() == 'Linux'

class Window(QtGui.QDialog):
    def __init__(self):
        super(Window, self).__init__()

        self.settings = {}
        self.settings['syncdir'] = ''
        self.settings['url'] = 'http://...'

        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(self.getSettingsFile()))
            self.settings['syncdir'] = config.get("main", "syncdir")
            self.settings['url'] = config.get("main", "url")
        except Exception as e:
            print ">>>", e

        self.running = False

        self.createIconGroupBox()
        self.createMessageGroupBox()

        self.createActions()
        self.createTrayIcon()

        self.trayIcon.messageClicked.connect(self.messageClicked)
        self.trayIcon.activated.connect(self.iconActivated)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.messageGroupBox)
        self.setLayout(mainLayout)

        #self.iconComboBox.setCurrentIndex(1)
        self.setIcon(0)
        self.trayIcon.show()

        self.setWindowTitle("Transporter")
        self.resize(400, 300)


    def desktopNotify(self, title, message):
        if on_macos:
            import macnotification
            macnotification.notify(title, None, message, delay=0)
            return

        if on_windows:
            self.trayIcon.showMessage(title, message)
            return

    def closeEvent(self, event):
        if self.trayIcon.isVisible():
            QtGui.QMessageBox.information(self, "Systray",
                    "The program will keep running in the system tray. To "
                    "terminate the program, choose <b>Quit</b> in the "
                    "context menu of the system tray entry.")
            self.hide()
            event.ignore()

    def setIcon(self, index):
        print index
        icon = self.iconComboBox.itemIcon(index)
        self.trayIcon.setIcon(icon)
        self.setWindowIcon(icon)
        self.trayIcon.setToolTip(self.iconComboBox.itemText(index))

    def iconActivated(self, reason):
        if reason in (QtGui.QSystemTrayIcon.Trigger, QtGui.QSystemTrayIcon.DoubleClick):
            self.iconComboBox.setCurrentIndex(
                    (self.iconComboBox.currentIndex() + 1)
                    % self.iconComboBox.count())
        elif reason == QtGui.QSystemTrayIcon.MiddleClick:
            self.showMessage()

    def showMessage(self):
        print "showing message"
        self.desktopNotify("hello", "hello world.")


    def messageClicked(self):
        #QtGui.QMessageBox.information(None, "Systray",
        #        "Sorry, I already gave what help I could.\nMaybe you should "
        #        "try asking a human?")
        return

    def createIconGroupBox(self):
        self.iconLabel = QtGui.QLabel("Icon:")
        self.iconComboBox = QtGui.QComboBox()
        f = './icons/transporter.tif' #bird-red-icon.png'
        self.iconComboBox.addItem(QtGui.QIcon(f), "Transporter")
        f = './icons/birds-green-icon.png'
        self.iconComboBox.addItem(QtGui.QIcon(f), "Transporter")
        self.iconComboBox.addItem(QtGui.QIcon(f), "Transporter")

    def setSyncDirectory(self):
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                self.directoryEdit.text(), options)
        if directory:
            self.directoryEdit.setText(directory)

    def getSettingsFile(self):
        home = expanduser("~")
        d = os.path.join(home, '.kd-transporter')
        if not os.path.exists(d):
            try:
                os.mkdir(d)
            except:
                raise Exception('couldnt create settings path')
        return os.path.join(d, 'settings.ini')

    def saveSettings(self):
        print ">>> sync dir: ", self.directoryEdit.text()
        print ">>> url: ", self.urlEdit.text()
        config = ConfigParser.RawConfigParser()
        config.add_section('main')
        config.set('main', 'url', self.urlEdit.text())
        config.set('main', 'syncdir', self.directoryEdit.text())

        with open(self.getSettingsFile(), 'wb') as f:
            config.write(f)

    def createMessageGroupBox(self):
        self.messageGroupBox = QtGui.QGroupBox("Settings")

        urlLabel = QtGui.QLabel("Url:")
        self.urlEdit = QtGui.QLineEdit(self.settings['url'])

        directoryLabel = QtGui.QLabel("Syncing directory:")
        self.directoryEdit = QtGui.QLineEdit(self.settings['syncdir'])
        self.directoryEditBtn = QtGui.QPushButton("...")

        self.directoryEditBtn.clicked.connect(self.setSyncDirectory)

        self.saveSettingsButton = QtGui.QPushButton("Save settings")
        self.saveSettingsButton.clicked.connect(self.saveSettings)

        messageLayout = QtGui.QGridLayout()
        messageLayout.addWidget(urlLabel, 2, 0)
        messageLayout.addWidget(self.urlEdit, 2, 1, 1, 4)
        messageLayout.addWidget(directoryLabel, 3, 0)
        #
        messageLayout.addWidget(self.directoryEdit, 3, 1, rowSpan=1, columnSpan=1)
        messageLayout.addWidget(self.directoryEditBtn, 3, 2, rowSpan=1, columnSpan=3)
        messageLayout.addWidget(self.saveSettingsButton, 4, 1, rowSpan=1, columnSpan=1)
        #
        messageLayout.setColumnStretch(3, 1)
        messageLayout.setRowStretch(4, 1)
        self.messageGroupBox.setLayout(messageLayout)

    def myShowNormal(self):
        window.showNormal()
        window.activateWindow()
        window.raise_()

    def openSyncFolder(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl("file:///%s" % self.settings['syncdir'], QtCore.QUrl.TolerantMode))

    def stopClient(self):
        if on_macos:
            try:
                if self.process:
                    self.process.terminate()
            except Exception as e:
                return
        else:
            try:
                print "sending quit signal...."
                print ">>>", self.parent_conn.send({'cmd':'quit'})
                print "done "
            except Exception as e:
                print "exception on stop:", e

    def __read(self):
        print "client>>>", self.process.readAllStandardOutput()
        print "client e:>>>", self.process.readAllStandardError()

    def startClient(self):
        if on_macos:
            program = 'transporter-client'
            arguments = [self.settings['syncdir'], self.settings['url']]
            self.process = QtCore.QProcess()
            self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
            self.process.readyReadStandardOutput.connect(self.__read)
            self.process.start(program, arguments)
        else:
            self.parent_conn, self.child_conn = Pipe()
            self.process = Process(target=client.run_client, args=(self.settings['syncdir'], self.settings['url'], self.child_conn))
            self.process.start()

    def runSync(self):
        print "running -- ", self.running
        if self.running:
            print "now stopping"
            self.stopClient()
            self.runSyncAction.setText("&Run Sync")
            self.running = False
            self.setIcon(0)
        else:
            print "now starting...."
            self.startClient()
            self.runSyncAction.setText("S&top Sync")
            self.running = True
            self.setIcon(1)

        print "running - ", self.running

    def quit_app(self):
        self.stopClient()
        QtGui.qApp.quit()

    def createActions(self):

        self.runSyncAction = QtGui.QAction("&Run Sync", self,
                triggered=self.runSync)

        self.openSyncFolderAction = QtGui.QAction("&Open Sync Folder", self,
                triggered=self.openSyncFolder)

        self.showMessageAction = QtGui.QAction("&Show Message", self,
                triggered=self.showMessage)


        self.settingsAction = QtGui.QAction("&Settings", self,
                triggered=self.myShowNormal)

        self.quitAction = QtGui.QAction("&Quit", self,
                triggered=self.quit_app)

    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)

        self.trayIconMenu.addAction(self.runSyncAction)
        self.trayIconMenu.addAction(self.openSyncFolderAction)
        self.trayIconMenu.addAction(self.settingsAction)
        self.trayIconMenu.addAction(self.showMessageAction)

        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)

        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setContextMenu(self.trayIconMenu)

def hideMacDockIcon():
    import AppKit
    # https://developer.apple.com/library/mac/#documentation/AppKit/Reference/NSRunningApplication_Class/Reference/Reference.html
    NSApplicationActivationPolicyRegular = 0
    NSApplicationActivationPolicyAccessory = 1
    NSApplicationActivationPolicyProhibited = 2
    AppKit.NSApp.setActivationPolicy_(NSApplicationActivationPolicyProhibited)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
        QtGui.QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
        sys.exit(1)

    QtGui.QApplication.setQuitOnLastWindowClosed(False)

    #hideMacDockIcon()

    window = Window()
    #window.hide()
    #window.setWindowFlags(QtCore.Qt.Tool);
    sys.exit(app.exec_())
