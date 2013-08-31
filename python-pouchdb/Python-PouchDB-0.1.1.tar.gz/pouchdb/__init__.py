"""
This is the main module of Python-PouchDB, a Python wrapper for the
PouchDB (http://pouchdb.com/) JavaScript library.

This module mostly mirrors its API. (See: http://pouchdb.com/api.html)

The most important difference is that when you don't specify a callback
function, you get the result of the function (that would normally be
send to the callback) returned instead. Because of that, you can use
PouchDB in a synchronously, which is a lot more Pythonic than the
default asynchronous api it offers in JavaScript (which is still
supported when required, though, using Qt's event loop).

An example of the synchronous API:
db = PouchDB('example')
doc = db.get('my_example_doc')

You can pass in functions and JSON primitives. This means it's
impossible to pass in PouchDB objects in the replicate functions.
Instead, pass in a string.

Configuration variables:
- storageDir: This property can be set *until* the first api method is
called. After that changing it doesn't do anything anymore.

"""

import utils
import context

import itertools
import functools
import os

storageDir = "dbs"

_context = None
def getContext():
	"""Offers access into the internals of the Python-PouchDB wrapper
	   logic. You shouldn't need this normally, but it's still exposed
	   for most importantly the tests.

	"""
	global _context
	if not _context:
		with open(os.path.join(utils.dataDir, "pouchdb-nightly.js")) as f:
			js = f.read()
		_context = context.JSContext(js, "PouchDB", storageDir)
	return _context

class PouchDBError(Exception):
	"""The base class for all Python-PouchDB errors. You can use get
	   item syntax to access properties set on the error object. E.g.

	   try:
	       ...
	   except pouchdb.PouchDBError, e:
	       if e["status"] == 404:
	           print "Not found"
	       else:
	           print "Unknown error"

	"""

	def __getitem__(self, key):
		return self.message[key]

class _PouchDBMetaClass(type):
	@property
	def enableAllDbs(self):
		return getContext().getStaticProperty("enableAllDbs")

	@enableAllDbs.setter
	def enableAllDbs(self, value):
		return getContext().setStaticProperty("enableAllDbs", value)

def _returningCallbackResultIfNoCallbackIsSpecified(f):
	@functools.wraps(f)
	def wrapper(clsOrSelf, funcName, callback=None, *args):
		hasUserCallback = True
		if not callback:
			hasUserCallback = False
			callbackResult = {}
			def callback(err=None, resp=None, *args):
				callbackResult["err"] = err
				callbackResult["resp"] = resp
		result = f(clsOrSelf, funcName, callback, *args)
		if hasUserCallback:
			return result
		getContext().waitUntilCalled(callback)
		if callbackResult["err"]:
			raise PouchDBError(callbackResult["err"])
		return callbackResult["resp"]
	return wrapper

class PouchDB(object):
	"""The main PouchDB object representing a database.

	   This object has a class level property, like in the original
	   JavaScript API: enableAllDbs.

	"""
	#for the enableAllDbs class level property
	__metaclass__ = _PouchDBMetaClass
	_idCounter = itertools.count()

	def __init__(self, name, **options):
		super(PouchDB, self).__init__()

		self._name = name
		self._id = next(self._idCounter)
		callback = lambda *args: None
		getContext().newObject(self._id, name, options, callback)
		getContext().waitUntilCalled(callback)

	@classmethod
	def allDbs(cls, callback=None):
		return cls._callStatic("allDbs", callback)

	@classmethod
	def replicate(cls, source, target, callback=None, **options):
		callback, options = cls._fillInReplicationOptions(callback, options)
		if cls._hasCallback(callback, options):
			return getContext().callStatic("replicate", source, target, options)
		return cls._callStatic("replicate", callback, source, target, options)

	@staticmethod
	def _fillInReplicationOptions(callback, options):
		if "onComplete" in options and not callback:
			callback = options["onComplete"]
			del options["onComplete"]
		return callback, options

	@staticmethod
	def _hasCallback(callback, options):
		return options.get("continuous", False) and not callback

	@classmethod
	def destroy(cls, name, callback=None):
		return cls._callStatic("destroy", callback, name)

	def put(self, doc, callback=None, **options):
		return self._call("put", callback, doc, options)

	def post(self, doc, callback=None, **options):
		return self._call("post", callback, doc, options)

	def get(self, docid, callback=None, **options):
		return self._call("get", callback, docid, options)

	def remove(self, doc, callback=None, **options):
		return self._call("remove", callback, doc, options)

	def bulkDocs(self, docs, callback=None, **options):
		return self._call("bulkDocs", callback, docs, options)

	def allDocs(self, callback=None, **options):
		return self._call("allDocs", callback, options)

	def query(self, func, callback=None, **options):
		return self._call("query", callback, func, options)

	def info(self, callback=None):
		return self._call("info", callback)

	def compact(self, callback=None, **options):
		return self._call("compact", callback, options)

	def revsDiff(self, diff, callback=None):
		return self._call("revsDiff", callback, diff)

	def putAttachment(self, docId, attachmentId, attachmentBytes, type, rev=None, callback=None):
		def getCallback(err, resp=None):
			doc = resp
			if err:
				doc = {"_id": docId}
			if not "_attachments" in doc:
				doc["_attachments"] = {}
			doc["_attachments"][attachmentId] = {
				"content_type": type,
				"data": attachmentBytes.encode("base64").strip(),
			}
			return self.put(doc, callback)

		if callback:
			self.get(docId, getCallback, rev=rev)
		else:
			try:
				resp = self.get(docId, rev=rev)
			except PouchDBError, e:
				resp = None
				err = e.message
			else:
				err = None
			return getCallback(err, resp)

	def getAttachment(self, docId, attachmentId, callback=None, **options):
		def modifyAttachment(attachment):
			attachment["data"] = str(attachment["data"]).decode("base64")
			return attachment

		def getAttachmentCallback(err, attachment=None):
			if err:
				self._callCallback(callback, err, None)
			else:
				self._callCallback(callback, None, modifyAttachment(attachment))

		if callback:
			self._call("getAttachment", getAttachmentCallback, docId, attachmentId, options)
		else:
			attachment = self._call("getAttachment", None, docId, attachmentId, options)
			return modifyAttachment(attachment)

	def _callCallback(self, callback, *args):
		callback(*args)
		#emulate JS callbacks
		callback._called = True

	def removeAttachment(self, docId, attachmentId, rev, callback=None):
		def getCallback(err, doc=None):
			if err:
				self._callCallback(callback, err, None)
				return
			try:
				del doc["_attachments"][attachmentId]
			except KeyError:
				err = self._Errors["MISSING_DOC"]
				if callback:
					self._callCallback(callback, err, None)
				else:
					raise PouchDBError(err)
			else:
				return self.put(doc, callback)

		if callback:
			self.get(docId, getCallback, rev=rev)
		else:
			doc = self.get(docId, rev=rev)
			return getCallback(None, doc)

	@property
	def _Errors(self):
		return getContext().getStaticProperty("Errors")

	def replicate_from(self, source, callback=None, **options):
		callback, options = self._fillInReplicationOptions(callback, options)
		if self._hasCallback(callback, options):
			return getContext().call(self._id, "replicate.from", source, options, callback)
		return self._call("replicate.from", callback, source, options)

	def replicate_to(self, target, callback=None, **options):
		callback, options = self._fillInReplicationOptions(callback, options)
		if self._hasCallback(callback, options):
			return getContext().call(self._id, "replicate.to", target, options, callback)
		return self._call("replicate.to", callback, target, options)

	def changes(self, **options):
		return getContext().call(self._id, "changes", options)

	@classmethod
	@_returningCallbackResultIfNoCallbackIsSpecified
	def _callStatic(cls, funcName, callback, *args):
		return getContext().callStatic(funcName, *list(args) + [callback])

	@_returningCallbackResultIfNoCallbackIsSpecified
	def _call(self, funcName, callback, *args):
		return getContext().call(self._id, funcName, *list(args) + [callback])
