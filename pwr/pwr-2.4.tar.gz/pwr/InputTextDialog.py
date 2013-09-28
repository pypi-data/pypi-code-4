#!/usr/bin/env python2
# coding=utf-8
"""
Copyright (c) by Filipp Kucheryavy aka Frizzy <filipp.s.frizzy@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted 
provided that the following conditions are met:

a. Redistributions of source code must retain the above copyright notice, this list of 
conditions and the following disclaimer. 

b. Redistributions in binary form must reproduce the above copyright notice, this list of 
conditions and the following disclaimer in the documentation and/or other materials provided 
with the distribution. 

c. Neither the name of the nor the names of its contributors may be used to endorse or promote 
products derived from this software without specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS 
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY 
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
from InputTextDialogUi import Ui_Dialog

try:
	from PySide import QtGui
except:
	try:
		from PyQt4 import QtGui
	except:
		print >> sys.stderr, "Error: can't load PySide or PyQT"
		sys.exit()
 
class InputTextDialog(QtGui.QDialog, Ui_Dialog):
	def __init__(self, title="Input Dialog", message="Input your text here", text="hello world!", parent=None):
		QtGui.QDialog.__init__(self,parent)
		self.setupUi(self)
		self.setWindowTitle(title)
		self.label.setText(message)
		self.setPlainText(text)

	def setLabel(self, text):
		self.label.setText(text)

	def setPlainText(self, text):
		self.textEdit.setPlainText(text)

	def setHtml(self, text):
		self.textEdit.setHtml(text)

	def getPlainText(self):
		if self.textEdit.toPlainText():
			return (self.textEdit.toPlainText(), True)
		else:
			return ("", False)

	def getHtml(self):
		if self.textEdit.toHtml():
			return (self.textEdit.toHtml(), True)
		else:
			return ("", False)

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	dlg = InputTextDialog()
	if dlg.exec_():
		print dlg.getPlainText()
		print dlg.getHtml()