#!/usr/bin/env python
# coding=UTF-8

"""
PySide Widget showing a list of external system commands to execute and show a
window with output, success or failure of the call. Each command supplied in
a constructor list is assigned to a button with a corresponding label.
"""

import sys

from QtBindingHelper import loadUi
import QtGui
import QtCore
from QtGui import QPushButton, QHBoxLayout, QVBoxLayout
import subprocess
from functools import partial
import logging


USE_KDIALOG = False


#success_mark = u'✓' # U+2713CHECK MARK
success_mark = u'✔' # U+2714HEAVY CHECK MARK
#fail_mark = u'✗' # U+2717BALLOT X
fail_mark = u'✘' # U+2718HEAVY BALLOT X



class CommandLauncher(QtGui.QWidget):
    def __init__(self, command_list=[], parent=None):
        super(CommandLauncher, self).__init__(parent)
        self.title = "Simple Command Launcher"
        self.setWindowTitle(self.title)

        for cmd in command_list:
            try:
                cmd['label']
            except KeyError:
                cmd['label'] = cmd['command']
            if isinstance(cmd['command'], str):
                cmd['command'] = cmd['command'].split()
            logging.debug("command: %s" % cmd)

        self.cmd_list = [(cmd, QPushButton(cmd['label'])) for cmd in command_list]
        logging.debug("cmd_list: ", self.cmd_list)

        vbox = QVBoxLayout()
        for cmd, button in self.cmd_list:
            vbox.addWidget(button)
            logging.debug("button: %s" % button)
            logging.debug("Connecting command: %(command)s for label: %(label)s" % cmd)
            # This should work somehow but then every command acts on the last
            # 'cmd' element, i.e. the value of 'cmd', which is the loop
            # iterator, after it's finished
            #button.clicked.connect(lambda: self.on_command(cmd))
            button.clicked.connect(partial(self.on_command_with_check, cmd))

        hbox = QHBoxLayout()
        hbox.addLayout(vbox)
        self.setLayout(hbox)
        self.resize(300, 150)

    def on_command_with_check(self, command):
        try:
            self.on_command(command)
        except OSError as e:
            logging.warn("Could not execute command: %s" % str(e))
            QtGui.QMessageBox.critical(self, self.title, self.tr("Could not execute command: %s" % str(e)))

    def on_command(self, command):
        logging.debug("Calling command: %(command)s for label: %(label)s" % command)
        if 'terminal' in command.keys() and command['terminal']:

            try:
                out = subprocess.check_output(command['command'])
            except AttributeError:
                # for python<2.7
                pipe = subprocess.Popen(command['command'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                out = pipe.stdout.read()
            if USE_KDIALOG:
                command_list = ['kdialog', '--msgbox', out]
                subprocess.call(command_list)
            else:
                if not 'silent' in command.keys() or not command['silent']:
                    self.InfoBox(out)
        elif 'xterm' in command.keys() and command['xterm']:
            cmd = "xterm -e \"" + ' '.join(command['command']) + " ; read\""
            import os
            os.system(cmd)
        else:
            if 'silent' in command.keys() and command['silent']:
                subprocess.call(command['command'])
            else:
                ret = True
                try:
                    subprocess.check_call(command['command'])
                except subprocess.CalledProcessError:
                    ret = False
                if 'test' in command.keys() and command['test']:
                    if ret:
                        self.SuccessBox()
                    else:
                        self.WarningBox("%s failed" % command['label'])
                else:
                    if ret:
                        self.InfoBox("%s succeeded" % command['label'])
                    else:
                        self.WarningBox("%s failed" % command['label'])

    def InfoBox(self, msg):
        return QtGui.QMessageBox.information(self, self.title, self.tr(msg))

    def WarningBox(self, msg):
        return QtGui.QMessageBox.warning(self, self.title, self.tr(msg))

    def SuccessBox(self):
        return QtGui.QMessageBox.information(self, self.title, success_mark)

    def FailureBox(self):
        return QtGui.QMessageBox.information(self, self.title, fail_mark)


def main():
    app = QtGui.QApplication(sys.argv)

    example_command_list = [
        {'command': "ls", 'terminal': True},
        {'label': "Show free diskspace", 'command': ["df", "-h"], 'terminal': True},
        {'label': "failing command", 'command': "false", 'silent': False},
        {'label': "true", 'command': "true", 'test': True},
        {'label': "xterm Hello World", 'command': "echo 'hello world'", 'xterm': True},
    ]

    cl = CommandLauncher(example_command_list)
    cl.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

