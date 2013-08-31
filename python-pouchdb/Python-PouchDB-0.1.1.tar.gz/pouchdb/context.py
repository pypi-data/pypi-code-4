try:
	from PySide import QtCore, QtGui, QtWebKit
except ImportError:#pragma: no cover
	from PyQt4 import QtCore, QtGui, QtWebKit
import itertools
import sys
import os
import json

import utils

class Page(QtWebKit.QWebPage):
	def __init__(self, gate, *args, **kwargs):
		super(Page, self).__init__(*args, **kwargs)

		self._gate = gate

		self.mainFrame().javaScriptWindowObjectCleared.connect(self._setGate)
		self._setGate()

	def _setGate(self):
		self.mainFrame().addToJavaScriptWindowObject("gate", self._gate)

	def javaScriptConsoleMessage(self, message, lineNumber, sourceId):#pragma: no cover
		print "line %s: %s" % (lineNumber, message)

class Gate(QtCore.QObject):
	try:
		Signal = QtCore.Signal
	except AttributeError:#pragma: no cover
		Signal = QtCore.pyqtSignal
	callbackCalled = Signal([str, str])

with open(os.path.join(utils.dataDir, "bridge.html")) as f:
	bridgeHtml = f.read()

class JSContext(object):
	_functionsCounter = itertools.count()
	_functions = {}

	def __init__(self, js, className, storageDir, *args, **kwargs):
		super(JSContext, self).__init__(*args, **kwargs)

		self._js = js
		self._className = className

		self._app = QtGui.QApplication.instance()
		if not self._app:#pragma: no branch
			self._app = QtGui.QApplication(sys.argv)

		QtWebKit.QWebSettings.globalSettings().enablePersistentStorage(os.path.abspath(storageDir))
		#200 databases (1GB max) should be enough. Maybe -1 would work,
		#but since there's no documentation for that this is probably
		#the best solution.
		QtWebKit.QWebSettings.globalSettings().setOfflineStorageDefaultQuota(1024 * 1024 * 5 * 200)
		#Stop the same-origin policy for file URLs (which we use).
		QtWebKit.QWebSettings.globalSettings().setAttribute(QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls, True)

		self._view = QtWebKit.QWebView()
		self._gate = Gate()
		self._gate.callbackCalled.connect(self._callbackCalled)
		self._page = Page(self._gate)

		self._view.setPage(self._page)
		self._reload()

	def reset(self):
		QtWebKit.QWebDatabase.removeAllDatabases()
		self._reload()

	def _reload(self):
		html = bridgeHtml % self._js

		#Qt guarantees the html is loaded immeadiately, and since there
		#aren't any resources, we don't need to block until loaded.
		self._page.mainFrame().setHtml(html, QtCore.QUrl("file:///"))

	def _callbackCalled(self, id, args):
		def callFunc():
			func(*self._toPyArgs(args))
			func._called = True

		func = self._functions[unicode(id)]
		#calling a function from a slot called by the JS engine blocks
		#the JS engine itself, which we don't want, so execute somewhere
		#else in the event loop.
		QtCore.QTimer.singleShot(0, callFunc)

	def _toPyArgs(self, args):
		args = json.loads(unicode(args))
		return [self._toPyArg(a) for a in args]

	def _toPyArg(self, arg):
		#function conversion
		with utils.ignored(TypeError, KeyError):
			if arg["type"] == "_js-returned-function":
				return lambda *args: self._evalJs("functions[%s](%s)" % (
					arg["functionId"],
					", ".join(args),
				))
		#recursion
		with utils.ignored(AttributeError):
			newArg = {}
			for key, value in arg.iteritems():
				newArg[key] = self._toPyArg(value)
			return newArg
		#TODO: if context.py would ever be used for another project,
		#adding support for sequences here would be nice.

		#everything else
		return arg

	def newObject(self, id, *args):
		self._evalJs("""
			objects[{id}] = new {className}({args});
		""".format(
			className=self._className,
			id=id,
			args=self._toJSArgs(args),
		))

	def _toJSArgs(self, args):
		return ", ".join(self._toJSArg(a) for a in args)

	def _toJSArg(self, arg):
		#callables
		if callable(arg):
			id = self._functionId()
			self._functions[id] = arg
			return "createCallback(%s)" % id
		#mappings - handle recursively
		with utils.ignored(AttributeError):
			obj = "{"
			for k, v in arg.iteritems():
				obj += k + ":" + self._toJSArg(v) + ","
			return obj.strip(",") + "}"
		#TODO: if context.py would ever be used for another project,
		#adding support for sequences here would be nice.

		#the default
		return json.dumps(arg)

	def _functionId(self):
		return unicode(next(self._functionsCounter))

	def getStaticProperty(self, name):
		return self._evalJs("return %s.%s" % (self._className, name))

	def setStaticProperty(self, name, value):
		return self._evalJs("%s.%s = %s;" % (self._className, name, json.dumps(value)))

	def callStatic(self, funcName, *args):
		js = "return {className}.{funcName}({args});".format(
			className=self._className,
			args=self._toJSArgs(args),
			funcName=funcName,
			id=id,
		)
		return self._evalJs(js)

	def call(self, id, funcName, *args):
		js = "return objects[{id}].{funcName}({args});".format(
			args=self._toJSArgs(args),
			funcName=funcName,
			id=id,
		)
		return self._evalJs(js)

	def waitUntilCalled(self, callback):
		while not getattr(callback, "_called", False):
			self._app.processEvents()

	def _evalJs(self, userJs):
		returned = {}
		def callback(result=None):
			returned["result"] = result
		self._functions["_evalJs"] = callback
		js = """
			(function () {
				var result = (function () {
					%s
				}());
				createCallback('_evalJs')(result);
			}())
		""" % userJs
		self._page.mainFrame().evaluateJavaScript(js)
		self.waitUntilCalled(callback)
		return returned["result"]
