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

import os
import sys
import codecs
import shutil
import urllib2
from configobj import ConfigObj
from InputTextDialog import InputTextDialog

try:
	from pygments import highlight
	from pygments.lexers import get_lexer_by_name
	from pygments.formatters import HtmlFormatter
except:
	print >> sys.stderr, "Warning: can't load pygments, highlighter not available"

try:
	from PySide import QtCore, QtGui, QtWebKit, QtNetwork
except:
	try:
		from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
	except:
		print >> sys.stderr, "Error: can't load PySide or PyQT"
		sys.exit()

class WYSIWYG(QtGui.QMainWindow):
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)

		self.loadConfig()

		self.setWindowTitle(self.title)
		self.webView = QtWebKit.QWebView()
		self.webView.settings().setAttribute(
		  QtWebKit.QWebSettings.JavascriptEnabled, False)
		self.webView.settings().setAttribute(
		  QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
		self.webView.page().linkHovered.connect(self.showLink)
		self.currentUrl = QtGui.QLineEdit("")
		self.currentUrl.returnPressed.connect(self.urlChanged)
		self.textEdit = QtGui.QTextEdit()
		self.textEdit.textChanged.connect(self.updateWebView)
		self.tabs = QtGui.QTabWidget()
		self.tabs.addTab(self.webView, "Document")
		self.tabs.addTab(self.textEdit, "Source")
		self.tabs.currentChanged.connect(self.updateTextEdit)
		self.new()
		self.setCentralWidget(self.tabs)
		self.menubar = self.menuBar()
		self.toolbarMenu = self.addToolBar('New')
		self.toolbarMenuW = self.addToolBar('WYSIWYG')
		self.statusBar()
		
		self.printer = QtGui.QPrinter()

		# main actions
		self.createNewAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					      "document-new"), '&New', self)
		self.createNewAction.setShortcut('Ctrl+N')
		self.createNewAction.setStatusTip('Create File')
		self.createNewAction.triggered.connect(self.new)

		self.loadAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					"document-open"), '&Open', self)
		self.loadAction.setShortcut('Ctrl+O')
		self.loadAction.setStatusTip('Open file')
		self.loadAction.triggered.connect(self.open)

		self.saveAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					"document-save"), '&Save', self)
		self.saveAction.setShortcut('Ctrl+S')
		self.saveAction.setStatusTip('Save file')
		self.saveAction.triggered.connect(self.save)

		self.saveAsAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				    "document-save-as"), '&Save as', self)
		self.saveAction.setStatusTip('Save file as')
		self.saveAsAction.triggered.connect(self.saveAs)

		self.printItAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				      "document-print"), '&Print it', self)
		self.printItAction.setStatusTip('Print this page')
		self.printItAction.triggered.connect(self.printIt)

		self.aboutAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					  "help-about"), '&About', self)
		self.aboutAction.triggered.connect(self.about)

		self.quitAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				    "application-exit"), '&Quit', self)
		self.quitAction.setShortcut('Ctrl+Q')
		self.quitAction.setStatusTip('Exit application')
		self.quitAction.triggered.connect(self.close)

		# main menu & toolbar
		self.fileMenu = self.menubar.addMenu('&File')
		self.fileMenu.addAction(self.createNewAction)
		self.fileMenu.addAction(self.loadAction)
		self.fileMenu.addAction(self.saveAction)
		self.fileMenu.addAction(self.saveAsAction)
		self.fileMenu.addAction(self.printItAction)
		self.fileMenu.addAction(self.aboutAction)
		self.fileMenu.addAction(self.quitAction)

		self.toolbarMenu.addAction(self.createNewAction)
		self.toolbarMenu.addAction(self.loadAction)
		self.toolbarMenu.addAction(self.saveAction)
		self.toolbarMenu.addSeparator ()

		self.undoAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					    "edit-undo"), 'Undo', self)
		self.undoAction.setShortcut('Ctrl+Z')
		self.undoAction.setStatusTip('Undo')
		self.undoAction.triggered.connect(self.undo)
		self.toolbarMenu.addAction(self.undoAction)

		self.redoAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					    "edit-redo"), 'Redo', self)
		self.redoAction.setShortcut('Ctrl++Shift+Z')
		self.redoAction.setStatusTip('Redo')
		self.redoAction.triggered.connect(self.redo)
		self.toolbarMenu.addAction(self.redoAction)
		self.toolbarMenu.addSeparator ()

		# font
		self.fontMenu = self.menubar.addMenu(QtGui.QIcon.fromTheme(
					"preferences-desktop-font"),'&Font')

		self.comboFont = QtGui.QComboBox(self)
		for font in sorted(self.fonts):
			self.comboFont.addItem(font)
		self.comboFont.setEditable(True)
		self.comboFont.activated['QString'].connect(self.font)
		self.comboFontAction = QtGui.QWidgetAction(self)
		self.comboFontAction.setDefaultWidget(self.comboFont)
		self.fontMenu.addAction(self.comboFontAction)

		self.spinSize = QtGui.QSpinBox(self)
		self.spinSize.setRange(1,7)
		self.spinSize.setValue(3)
		self.spinSize.valueChanged.connect(self.size)
		self.spinSizeAction = QtGui.QWidgetAction(self)
		self.spinSizeAction.setDefaultWidget(self.spinSize)
		self.fontMenu.addAction(self.spinSizeAction)

		# insert
		self.insertMenu = self.menubar.addMenu('&Insert')

		self.insertHtmlAction = QtGui.QAction('HTML', self)
		self.insertHtmlAction.setStatusTip('insert HTML')
		self.insertHtmlAction.triggered.connect(self.insertHtml)
		self.insertMenu.addAction(self.insertHtmlAction)

		self.insertTextAction = QtGui.QAction('Text', self)
		self.insertTextAction.setStatusTip('insert Text')
		self.insertTextAction.triggered.connect(self.insertText)
		self.insertMenu.addAction(self.insertTextAction)

		self.insertTagAction = QtGui.QAction('Tag', self)
		self.insertTagAction.setStatusTip('insert Tag')
		self.insertTagAction.triggered.connect(self.insertTag)
		self.insertMenu.addAction(self.insertTagAction)

		# view
		self.viewMenu = self.menubar.addMenu('&View')

		self.jsRadioButton = QtGui.QRadioButton("Javascript enabled", self)
		self.jsRadioButton.setChecked(False)
		self.jsRadioButton.clicked.connect(self.enableJs)
		self.jsAction = QtGui.QWidgetAction(self)
		self.jsAction.setDefaultWidget(self.jsRadioButton)
		self.viewMenu.addAction(self.jsAction)

		# navigation
		self.navigationMenu = self.menubar.addMenu('&Navigation')
		self.backAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					    "go-previous"),'&Back', self)
		self.backAction.setStatusTip('Back')
		self.backAction.triggered.connect(self.back)
		self.navigationMenu.addAction(self.backAction)

		self.forwardAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					      "go-next"),'&Forward', self)
		self.forwardAction.setStatusTip('Forward')
		self.forwardAction.triggered.connect(self.forward)
		self.navigationMenu.addAction(self.forwardAction)

		self.stopAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					  "process-stop"),'&Stop', self)
		self.stopAction.setStatusTip('Stop')
		self.stopAction.triggered.connect(self.stop)
		self.navigationMenu.addAction(self.stopAction)

		self.reloadAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					    "view-refresh"),'&Reload', self)
		self.reloadAction.setStatusTip('Reload')
		self.reloadAction.triggered.connect(self.reload)
		self.navigationMenu.addAction(self.reloadAction)

		self.urlAction = QtGui.QWidgetAction(self)
		self.urlAction.setDefaultWidget(self.currentUrl)
		self.navigationMenu.addAction(self.urlAction)
		
		self.runAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					    "system-run"),'&Run', self)
		self.runAction.setStatusTip('Run')
		self.runAction.triggered.connect(self.urlChanged)
		self.navigationMenu.addAction(self.runAction)

		# WYSIWYG toolbar and actions
		self.comboHeader = QtGui.QComboBox(self)
		for key in sorted(self.headers.keys()):
			self.comboHeader.addItem(key)
		self.comboHeader.activated['QString'].connect(self.header)
		self.toolbarMenuW.addWidget(self.comboHeader)

		self.boldAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				      "format-text-bold"), 'Bold', self)
		self.boldAction.setStatusTip('Bold')
		self.boldAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.boldAction)
		self.fontMenu.addAction(self.boldAction)

		self.italicAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				    "format-text-italic"), 'Italic', self)
		self.italicAction.setStatusTip('Italic')
		self.italicAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.italicAction)
		self.fontMenu.addAction(self.italicAction)

		self.underlineAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				"format-text-underline"), 'Underline', self)
		self.underlineAction.setStatusTip('Underline')
		self.underlineAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.underlineAction)
		self.fontMenu.addAction(self.underlineAction)

		self.strikethroughAction = QtGui.QAction(QtGui.QIcon.fromTheme(
			    "format-text-strikethrough"), 'Strikethrough', self)
		self.strikethroughAction.setStatusTip('Strikethrough')
		self.strikethroughAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.strikethroughAction)
		self.fontMenu.addAction(self.strikethroughAction)

		self.outdentAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-indent-less"), 'outdent', self)
		self.outdentAction.setStatusTip('outdent')
		self.outdentAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.outdentAction)

		self.indentAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-indent-more"), 'indent', self)
		self.indentAction.setStatusTip('indent')
		self.indentAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.indentAction)

		self.insertOrderedListAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-list-ordered"), 'insertOrderedList', self)
		self.insertOrderedListAction.setStatusTip('Insert Ordered List')
		self.insertOrderedListAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.insertOrderedListAction)
		self.insertMenu.addAction(self.insertOrderedListAction)

		self.insertUnorderedListAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-list-unordered"), 'insertUnorderedList', self)
		self.insertUnorderedListAction.setStatusTip('Insert Unordered List')
		self.insertUnorderedListAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.insertUnorderedListAction)
		self.insertMenu.addAction(self.insertUnorderedListAction)

		self.justifyleftAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-justify-left"), 'Justifyleft', self)
		self.justifyleftAction.setStatusTip('Justify left')
		self.justifyleftAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.justifyleftAction)
		self.fontMenu.addAction(self.justifyleftAction)

		self.justifycenterAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				"format-justify-center"), 'Justifycenter', self)
		self.justifycenterAction.setStatusTip('Justify center')
		self.justifycenterAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.justifycenterAction)
		self.fontMenu.addAction(self.justifycenterAction)

		self.justifyrightAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-justify-right"), 'Justifyright', self)
		self.justifyrightAction.setStatusTip('Justify right')
		self.justifyrightAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.justifyrightAction)
		self.fontMenu.addAction(self.justifyrightAction)

		self.justifyfullAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-justify-fill"), 'Justifyfull', self)
		self.justifyfullAction.setStatusTip('Justify full')
		self.justifyfullAction.triggered.connect(self.executeJs)
		self.toolbarMenuW.addAction(self.justifyfullAction)
		self.fontMenu.addAction(self.justifyfullAction)

		self.colorAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-text-color"),'Color', self)
		self.colorAction.setStatusTip('Color')
		self.colorAction.triggered.connect(self.color)
		self.toolbarMenuW.addAction(self.colorAction)

		self.bColorAction = QtGui.QAction(QtGui.QIcon.fromTheme(
				  "format-fill-color"),'Background Color', self)
		self.bColorAction.setStatusTip('Background Color')
		self.bColorAction.triggered.connect(self.backgroundColor)
		self.toolbarMenuW.addAction(self.bColorAction)

		self.insertlinkAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					  "insert-link"), 'Insertlink', self)
		self.insertlinkAction.setStatusTip('Insert link')
		self.insertlinkAction.triggered.connect(self.insertLink)
		self.toolbarMenuW.addAction(self.insertlinkAction)
		self.insertMenu.addAction(self.insertlinkAction)

		self.insertimageAction = QtGui.QAction(QtGui.QIcon.fromTheme(
					  "insert-image"), 'Insertimage', self)
		self.insertimageAction.setStatusTip('Insert image')
		self.insertimageAction.triggered.connect(self.insertImage)
		self.toolbarMenuW.addAction(self.insertimageAction)
		self.insertMenu.addAction(self.insertimageAction)

	def loadConfig(self):
		self.homeDirectory = os.path.join(os.path.expanduser("~"), "pwr")
		self.homeConfig = os.path.join(self.homeDirectory, "pwr.conf")
		self.defaultDirectory = os.path.join(os.path.abspath(
						      os.path.dirname(
				sys.modules[self.__module__].__file__)),
								"config")
		self.defaultConfig = os.path.join(self.defaultDirectory, "pwr.conf")
		if not os.path.isdir(self.homeDirectory):
			try:
				shutil.copytree(self.defaultDirectory, self.homeDirectory)
			except:
				print 1
		if not os.path.isfile(self.homeConfig):
			try:
				shutil.copy(self.defaultConfig, self.homeConfig)
			except:
				print 2
		try:
			self.config = ConfigObj(self.defaultConfig)
			self.userConfig = ConfigObj(self.homeConfig)
		except:
			print 3

		def setConfigField(field, default):
			if not field and default:
				print "can not set empty field to self"
				return 1
			if self.userConfig[field]:
				self.title = self.userConfig[field]
			elif self.config[field]:
				self.title = self.config[field]
			else:
				self.__dict__[field] = default

		setConfigField('title', 'python WYSIWYG redactor')
		self.lastDirectory = self.homeDirectory
		self.saveFilters = ";;".join(("Web pages (*.html *.htm)",
					      "Images (*.png *.xpm *.jpg)",
					      "Text files (*.txt)",
					      "XML files (*.xml)",
					      "All files (*.*)",))
		self.fonts = ["Arial Black", 
			      "Arial", 
			      "Comic Sans MS", 
			      "Courier New", 
			      "Georgia", 
			      "Impact", 
			      "Lucida Console", 
			      "Lucida Sans Unicode", 
			      "Palatino Linotype", 
			      "Tahoma", 
			      "Times New Roman", 
			      "Trebuchet MS", 
			      "Verdana",]
		self.headers = {"Title 1": "h1",
				"Title 2": "h2",
				"Title 3": "h3",
				"Title 4": "h4",
				"Title 5": "h5",
				"Subtitle": "h6",
				"Paragraph": "p",
				"Preformatted": "pre",}
		# highlighter
		try:
			self.lexer = get_lexer_by_name('html')
		except:
			self.lexer = False

	def saveConfig(self):
		pass

	def new(self):
		if self.savePageBeforeClose() == -1:
			return 0
		self.webView.load(QtCore.QUrl(""))
		self.webView.page().setContentEditable(True)

	def urlChanged(self):
		self.open(self.currentUrl.text())


	def open(self, file=None):
		if self.savePageBeforeClose() == -1:
			return 0
		if not file:
			file = self.showFileOpenDialog(self.lastDirectory,
							self.saveFilters)[0]
		if file is not None and file != "":
			self.webView.setUrl(QtCore.QUrl("file://" + file))
			self.currentUrl.setText(file)
			self.lastDirectory = os.path.dirname(file)
			

	def savePageBeforeClose(self):
		if self.webView.page().isModified() or self.textEdit.document().isModified():
			choice = self.showChoice("The document has been modified",
					      "Do you want to save your changes?")
			if choice == -1:
				return -1
			elif choice:
				self.save()
			return 1

	def save(self):
		if self.currentUrl.text():
			self.saveHtml(self.currentUrl.text())
		else:
			self.saveAs()

	def saveAs(self):
		title = self.webView.title()
		if title == "":
			title = "Untitled"
		filename = self.showFileSaveDialog(os.path.join(self.lastDirectory, title),
									  self.saveFilters)[0]
		if filename is not None and filename != "":
			self.currentUrl.setText(filename)
			self.lastDirectory = os.path.dirname(filename)
			self.saveHtml(filename)

	def saveHtml(self, filename):
		if filename is not None and filename != "":
			data = self.webView.page().mainFrame().toHtml()
			if "!DOCTYPE" not in data:
				data = "<!DOCTYPE html>\n" + data
			try:
				with codecs.open(filename, encoding="utf-8", mode="w") as f:
					f.write(data)
			except (IOError,
				ValueError,
				UnicodeDecodeError,
				UnicodeEncodeError) as err:
				self.showCritical("Can not save " + filename, err)

	def undo(self):
		currentWidget = self.tabs.currentWidget()
		if isinstance(currentWidget, QtWebKit.QWebView):
			self.executeJs("Undo")
		elif isinstance(currentWidget, QtGui.QTextEdit):
			currentWidget.undo()

	def redo(self):
		currentWidget = self.tabs.currentWidget()
		if isinstance(currentWidget, QtWebKit.QWebView):
			self.executeJs("Redo")
		elif isinstance(currentWidget, QtGui.QTextEdit):
			currentWidget.redo()

	def printIt(self):
		if QtGui.QPrintDialog(self.printer,
		     self).exec_() == QtGui.QDialog.Accepted:
			self.webView.print_(self.printer)

	def about(self):
		about = "\n".join(("Simple WYSIWYG redactor.",
				  "Explore more on https://github.com/Friz-zy/WYSIWYG"))
		self.showMessage("About WYSIWYG", about)

	def executeJs(self, action="", defaultUI="false", 
				    valueArgument="false"):
		if not action:
			action = self.sender().text()
		jScript = "document.execCommand('%s', %s, %s);" % (
				    action, defaultUI, valueArgument)
		self.webView.settings().setAttribute(
		  QtWebKit.QWebSettings.JavascriptEnabled, True)
		self.webView.page().mainFrame().evaluateJavaScript(jScript)
		if not self.jsRadioButton.isChecked():
			self.webView.settings().setAttribute(
			  QtWebKit.QWebSettings.JavascriptEnabled, False)

	def font(self, font):
		font = '"%s"' % font
		self.executeJs("fontName", valueArgument=font)

	def size(self, size):
		self.executeJs("fontSize", valueArgument=size)

	def insertHtml(self, html=""):
		if not html:
			if self.webView.selectedText():
				text = self.webView.selectedHtml()
			else:
				text = "<h1>hello world!</h1>"
			html, ok = self.getTextInput(message="Input your html here",
								      text=text)
		if html:
			self.executeJs("insertHTML", valueArgument='"%s"' % html)

	def insertText(self, text=""):
		if not text:
			txt= self.webView.selectedText()
			print txt
			if not txt:
				txt = "hello world!"
			text, ok = self.getTextInput(text=txt)
		if text:
			self.executeJs("insertText", valueArgument='"%s"' % text)

	def insertTag(self, tag=""):
		if not tag:
			tag, ok = self.getLineInput("Enter your tag")
		if tag:
			if tag.strip("</ >") not in ["img", "br", "input", "hr"]:
				tag = tag.strip("</ >")
				html = "<%s>%s</%s>" % (tag,
							self.webView.selectedText(),
							tag)
			else:
				if "<" != tag.strip(" ")[0]:
					tag = "<%s>" % tag
				html = tag
		if html:
			self.executeJs("insertHTML", valueArgument='"%s"' % html)

	def enableJs(self):
		if self.jsRadioButton.isChecked():
			self.webView.settings().setAttribute(
			  QtWebKit.QWebSettings.JavascriptEnabled, True)
		else:
			self.webView.settings().setAttribute(
			  QtWebKit.QWebSettings.JavascriptEnabled, False)

	def back(self):
		self.webView.back()

	def forward(self):
		self.webView.forward()

	def stop(self):
		self.webView.stop()

	def reload(self):
		self.webView.reload()

	def header(self, header):
		self.executeJs("formatBlock",
				valueArgument='"%s"' % 
				    self.headers[header])

	def color(self):
		color = QtGui.QColorDialog.getColor()
		if color.isValid():
			self.executeJs(action="foreColor",
			valueArgument='"%s"' % color.name())

	def backgroundColor(self):
		color = QtGui.QColorDialog.getColor()
		if color.isValid():
			self.executeJs(action="backColor",
			valueArgument='"%s"' % color.name())

	def insertLink(self):
		text, ok = self.getLineInput('Enter link url')
		if ok:
			self.executeJs(action="createLink",
				valueArgument='"%s"' % text)

	def insertImage(self):
		text, ok = self.getLineInput('Enter image url')
		if ok:
			self.executeJs(action="insertImage",
				valueArgument='"%s"' % text)

	def updateWebView(self, html=""):
		if not html:
			html = self.textEdit.toPlainText()
		if html != self.webView.page().mainFrame().toHtml():
			self.webView.setHtml(html,
			  QtCore.QUrl().fromLocalFile(self.currentUrl.text()))

	def updateTextEdit(self):
		currentWidget = self.tabs.currentWidget()
		text = self.webView.page().mainFrame().toHtml()
		if isinstance(currentWidget, QtGui.QTextEdit) \
		  and text != currentWidget.toPlainText():
			if self.lexer:
				text = highlight(text, self.lexer, HtmlFormatter())
				#print text
				css = HtmlFormatter().get_style_defs('.highlight')
				self.textEdit.document().setDefaultStyleSheet(css)
				currentWidget.setHtml(text)
			else:
				currentWidget.setPlainText(text)

	def showLink(self, link, title, textContent):
		self.statusBar().showMessage(link)

	def showFileOpenDialog(self, path='.', filer=""):
		return QtGui.QFileDialog.getOpenFileName(self,
				      'Open file', path, filer)

	def showFileSaveDialog(self, path='.', filer=""):
		return QtGui.QFileDialog.getSaveFileName(self,
				    'Save file as:', path, filer)

	def showMessage(self, title, text):
		QtGui.QMessageBox.information(self,
		      '%s' % (title), '%s' % (text))

	def showCritical(self, title, text):
		QtGui.QMessageBox.critical(self,
		    '%s' % (title), '%s' % (text))

	def showChoice(self, title, text):
		q = QtGui.QMessageBox.question(self, 
				  title,
				  text,
				  QtGui.QMessageBox.No |
				  QtGui.QMessageBox.Cancel |
				  QtGui.QMessageBox.Yes,)
		if q == QtGui.QMessageBox.Yes:
			return True
		elif q == QtGui.QMessageBox.No:
			return False
		return -1

	def getLineInput(self, message):
		return QtGui.QInputDialog.getText(self,
			'Input Dialog', '%s' % (message))

	def getTextInput(self,title="Input Dialog", message="Input your text here",
								text="hello world!"):
		dlg = InputTextDialog(title,
				      message,
				      text,
				      self)
		if dlg.exec_():
			return dlg.getPlainText()

	def closeEvent(self, e):
		if self.savePageBeforeClose() != -1:
			self.saveConfig()
			print "bye!"
			self.close()
		else:
			e.ignore()

def main():
	app = QtGui.QApplication(sys.argv)
	myapp = WYSIWYG()
	myapp.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
