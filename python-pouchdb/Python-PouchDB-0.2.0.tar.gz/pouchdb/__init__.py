"""**Python-PouchDB** is a Python wrapper for the `PouchDB JavaScript
library <http://pouchdb.com/>`_. This module mostly mirrors `its API
<http://pouchdb.com/api.html>`_.

The most important difference is that when you don't specify a callback
function, you get the result of the function (that would normally be
send to the callback) returned instead. Because of that, you can use
PouchDB in a synchronously, which is a lot more Pythonic than the
default asynchronous api it offers in JavaScript (which is still
supported when required, though, using Qt's event loop).

An example of the synchronous API:

	>>> db = pouchdb.PouchDB('example')
	>>> doc = db.get('my_example_doc')

An example of the asynchronous API:

	>>> def callback(err, resp):
	...     print("inside callback:", resp)
	... 
	>>> db = pouchdb.PouchDB('example')
	>>> db.post({})
	>>> QtGui.QApplication.instance().processEvents()
	... a few more times... Alternatively, you could run the event loop
	... blocking using the `QtGui.QApplication.exec_` method.
	>>> QtGui.QApplication.instance().processEvents()
	('inside callback:', {u'ok': True, u'rev': u'1-a7ee7ce33fc13fcd4070fe30a2b19df2', u'id': u'79D24A39-C78A-4F6B-BDF3-AD0928B67D00'})

You can pass in functions and JSON primitives. This means it's
impossible to pass in PouchDB objects in the replicate functions.
Instead, pass in a string.

Another small difference is that the `destroy()` function, the
`allDbs()` function, the `replicate()` function and the `enableAllDbs`
configuration variable are defined at the module level instead of the
class level, to provide a more Pythonic API. There still are 
`db.replicate_to` and `db.replicate_from` methods, though.

Next to the default PouchDB api, Python-PouchDB also wraps the
pouchdb.validation.js plugin, the `pouchdb.gql.js plugin
<http://pouchdb.com/gql.html>`_ and the pouchdb.spatial.js plugin.

"""
__version__ = "0.2.0"
__author__ = "Marten de Vries"

from . import utils
from . import context

import itertools
import functools
import os
import base64
import glob

_IGNORED_ERRORS = [
	"ArrayBuffer values are deprecated in Blob Constructor.",
]
_context = None
def getContext():
	"""Offers access into the internals of the Python-PouchDB wrapper
	   logic. You shouldn't need this normally, but it's still exposed
	   for most importantly the tests.

	"""
	global _context
	if not _context:
		js = _collectJavaScript()
		_context = context.JSContext(js, "PouchDB", _IGNORED_ERRORS, storageDir, baseUrl)
		_context.setStaticProperty("enableAllDbs", enableAllDbs)
	return _context

def _collectJavaScript():
	jsPaths = _collectJSFiles()
	js = ""
	for path in jsPaths:
		with open(path) as f:
			js += f.read() + "\n\n"
	return js

def _collectJSFiles():
	#the pouchdb source tree
	startPaths = [
		os.path.join(utils.dataDir, "pouchdb-source/pouch.js"),
		os.path.join(utils.dataDir, "pouchdb-source/pouch.utils.js")
	]
	depsPaths = glob.glob(os.path.join(utils.dataDir, "pouchdb-source/deps/*.js"))
	srcPaths = glob.glob(os.path.join(utils.dataDir, "pouchdb-source/*.js"))
	adapterPaths = glob.glob(os.path.join(utils.dataDir, "pouchdb-source/adapters/*.js"))
	adapterPaths = [p for p in adapterPaths if not "leveldb" in p]
	pluginPaths = glob.glob(os.path.join(utils.dataDir, "pouchdb-source/plugins/*.js"))
	for path in startPaths:
		srcPaths.remove(path)
	jsPaths = depsPaths + startPaths + srcPaths + adapterPaths + pluginPaths

	#custom JS files (pouchdb.validation.js)
	jsPaths += glob.glob(os.path.join(utils.dataDir, "*.js"))

	return jsPaths

def _callReturningResultIfNoCallback(f, callback):
	hasUserCallback = True
	if not callback:
		hasUserCallback = False
		callbackResult = {}
		def callback(err=None, resp=None, *args):
			callbackResult["err"] = err
			callbackResult["resp"] = resp
	result = f(callback)
	if hasUserCallback:
		return result
	getContext().waitUntilCalled(callback)
	if callbackResult["err"]:
		raise PouchDBError(callbackResult["err"])
	return callbackResult["resp"]

def _callStatic(funcName, callback, *args):
	f = lambda realCallback: getContext().callStatic(funcName, *list(args) + [realCallback])
	return _callReturningResultIfNoCallback(f, callback)

def _call(objectId, funcName, callback, *args):
	f = lambda realCallback: getContext().call(objectId, funcName, *list(args) + [realCallback])
	return _callReturningResultIfNoCallback(f, callback)

#Public configuration variables
storageDir = "dbs"
"""Specifies the location where the data you put in your PouchDB is
stored. Can only be set *until* the first api method is called. After
that changing it doesn't do anything anymore."""

baseUrl = "file:///"
"""Can also be set only until the first api method is called.
Its default value is 'file:///', which allows you to circumvent the
same-origin policy in modern versions of Qt. For older versions (4.8.1
is confirmed 'old'), it doesn't, and it that case you want to specify an
html origin. For example http://localhost:5984/ if you want to replicate
with that database."""

enableAllDbs = False
"""This property can also be set only until the first api method is
called. See for more info about it `the PouchDB documentation
<http://pouchdb.com/api.html>`_."""

def destroy(name, callback=None, **options):
	"""Example:

	   >>> pouchdb.destroy('test')

	"""
	return _callStatic("destroy", callback, name, options)

def allDbs(callback=None):
	"""Example:

	   >>> pouchdb.enableAllDbs = True
	   >>> pouchdb.allDbs()
	   [u'test']

	"""
	return _callStatic("allDbs", callback)

def replicate(source, target, callback=None, **options):
	"""Example:

	   >>> pouchdb.replicate("a", "b")
	   {u'docs_written': 0, u'start_time': u'2013-10-10T14:16:13.990Z', u'ok': True, u'docs_read': 0, u'end_time': u'2013-10-10T14:16:14.119Z'}

	"""
	callback, options = _fillInReplicationOptions(callback, options)
	if _hasCallback(callback, options):
		return getContext().callStatic("replicate", source, target, options)
	return _callStatic("replicate", callback, source, target, options)

def _hasCallback(callback, options):
	return options.get("continuous", False) and not callback

def _fillInReplicationOptions(callback, options):
	if "onComplete" in options and not callback:
		callback = options["onComplete"]
		del options["onComplete"]
	return callback, options

class PouchDBError(Exception):
	"""The base class for all Python-PouchDB errors. You can use get
	   item syntax to access properties set on the error object. E.g.:

	   >>> try:
	   ...     ...
	   ... except pouchdb.PouchDBError as e:
	   ...    if e["status"] == 404:
	   ...        print "Not found"
	   ...    else:
	   ...        print "Unknown error"

	"""
	def __init__(self, message, *args, **kwargs):
		super(PouchDBError, self).__init__(*args, **kwargs)

		self.message = message

	def __getitem__(self, key):
		return self.message[key]

	def __contains__(self, key):
		return key in self.message

	def __str__(self):
		return str(self.message)

class Validation(object):
	"""Wraps the pouchdb.validation.js plugin.

	   This plugin offers methods named exactly the same as their native
	   PouchDB counteraprts. They function the same, except that they
	   check if a document is valid via validate_doc_update functions in
	   design documents in the database. (Like CouchDB does).

	   You don't need to instantiate this yourself normally, instead you
	   find an instance on every instance of a PouchDB object named
	   'validating' (matching the JavaScript API).

	   An example:

	   >>> db = pouchdb.PouchDB('example')
	   >>> db.validating.post({})
	   {u'ok': True, u'rev': u'1-ceb68338b003868f327224adf4295aa7', u'id': u'49A851F4-7282-4388-9EFF-BE78C6B9324F'}

	"""
	def __init__(self, dbId, *args, **kwargs):
		super(Validation, self).__init__(*args, **kwargs)

		self._id = dbId

	def put(self, doc, callback=None, **options):
		return _call(self._id, "validating.put", callback, doc, options)

	def post(self, doc, callback=None, **options):
		return _call(self._id, "validating.post", callback, doc, options)

	def delete(self, doc, callback=None, **options):
		return _call(self._id, "validating.delete", callback, doc, options)

	def bulkDocs(self, bulkDocs, callback=None, **options):
		return _call(self._id, "validating.bulkDocs", callback, bulkDocs, options)

class PouchDB(object):
	"""The main PouchDB object representing a database.

	   This object has a class level property, like in the original
	   JavaScript API: enableAllDbs.

	"""
	#for the enableAllDbs class level property
	_idCounter = itertools.count()

	def __init__(self, name, **options):
		super(PouchDB, self).__init__()

		self._name = name
		self._id = next(self._idCounter)

		self.validating = Validation(self._id)

		callback = lambda *args: None
		getContext().newObject(self._id, name, options, callback)
		getContext().waitUntilCalled(callback)

	def put(self, doc, callback=None, **options):
		"""Example:

		   >>> db.put({"_id": "test"})
		   {u'ok': True, u'rev': u'1-b490828a5834c6e2d714c733f4f5a1a4', u'id': u'test'}

		"""
		return _call(self._id, "put", callback, doc, options)

	def post(self, doc, callback=None, **options):
		"""Example:

		   >>> db.post({"Hello": "world!"})
		   {u'ok': True, u'rev': u'1-300d88ee2a4d36b18a9ae11c8c2074db', u'id': u'BC1E7D48-0D92-4599-86F3-12F52E6FED36'}

		"""
		return _call(self._id, "post", callback, doc, options)

	def get(self, docid, callback=None, **options):
		"""Example:

		   >>> db.get("test")
		   {u'_rev': u'1-b490828a5834c6e2d714c733f4f5a1a4', u'_id': u'test'}

		"""
		return _call(self._id, "get", callback, docid, options)

	def remove(self, doc, callback=None, **options):
		"""Example:

			>>> db.remove({'_rev': '1-b490828a5834c6e2d714c733f4f5a1a4', '_id': u'test'})
			{u'ok': True, u'rev': u'2-2281a6d04e8c0aa3a5ba6ae733469cea', u'id': u'test'}

		"""
		return _call(self._id, "remove", callback, doc, options)

	def bulkDocs(self, docs, callback=None, **options):
		"""Example:

		   >>> db.bulkDocs({"docs": [{}, {}]})
		   [{u'rev': u'1-267beee068e37c4157c3d94e59f316e6', u'ok': True, u'id': u'BE1CE0E6-D4A8-473F-B1A3-D6497F7AD636'}, {u'rev': u'1-ddec8e427df68dd212b772002dc5723d', u'ok': True, u'id': u'321F5839-E077-451E-AFCA-8A52B54DACC4'}]

		"""
		return _call(self._id, "bulkDocs", callback, docs, options)

	def allDocs(self, callback=None, **options):
		"""Example:

		   >>> db.allDocs()
		   {u'rows': [{u'value': {u'rev': u'1-37c165ae6b958891006b95c75e8001a5'}, u'id': u'test', u'key': u'test'}], u'total_rows': 1, u'offset': 0}

		"""
		return _call(self._id, "allDocs", callback, options)

	def query(self, func, callback=None, **options):
		return _call(self._id, "query", callback, func, options)

	def info(self, callback=None):
		"""Example:

		   >>> db.info()
		   {u'update_seq': 1, u'db_name': u'_pouch_test2', u'doc_count': 1}

		"""
		return _call(self._id, "info", callback)

	def compact(self, callback=None, **options):
		"""Example:

		   >>> db.compact()

		"""
		return _call(self._id, "compact", callback, options)

	def revsDiff(self, diff, callback=None):
		return _call(self._id, "revsDiff", callback, diff)

	def putAttachment(self, docId, attachmentId, attachmentBytes, type, rev=None, callback=None):
		def getCallback(err, resp=None):
			doc = resp
			if err:
				doc = {"_id": docId}
			if not "_attachments" in doc:
				doc["_attachments"] = {}
			doc["_attachments"][attachmentId] = {
				"content_type": type,
				"data": base64.b64encode(attachmentBytes).decode("ascii"),
			}
			return self.put(doc, callback)

		if callback:
			self.get(docId, getCallback, rev=rev)
		else:
			try:
				resp = self.get(docId, rev=rev)
			except PouchDBError as e:
				resp = None
				err = e
			else:
				err = None
			return getCallback(err, resp)

	def getAttachment(self, docId, attachmentId, callback=None, **options):
		def modifyAttachment(attachment):
			attachment["data"] = base64.b64decode(attachment["data"].encode("ascii"))
			return attachment

		def getAttachmentCallback(err, attachment=None):
			if err:
				self._callCallback(callback, err, None)
			else:
				self._callCallback(callback, None, modifyAttachment(attachment))

		if callback:
			_call(self._id, "getAttachment", getAttachmentCallback, docId, attachmentId, options)
		else:
			attachment = _call(self._id, "getAttachment", None, docId, attachmentId, options)
			return modifyAttachment(attachment)

	def _callCallback(self, callback, *args):
		callback(*args)
		#emulate JS callbacks
		callback._called = True

	@property
	def _Errors(self):
		return getContext().getStaticProperty("Errors")

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

	def changes(self, **options):
		return getContext().call(self._id, "changes", options)

	def replicate_from(self, source, callback=None, **options):
		callback, options = _fillInReplicationOptions(callback, options)
		if _hasCallback(callback, options):
			return getContext().call(self._id, "replicate.from", source, options, callback)
		return _call(self._id, "replicate.from", callback, source, options)

	def replicate_to(self, target, callback=None, **options):
		callback, options = _fillInReplicationOptions(callback, options)
		if _hasCallback(callback, options):
			return getContext().call(self._id, "replicate.to", target, options, callback)
		return _call(self._id, "replicate.to", callback, target, options)

	def gql(self, query, callback=None, **options):
		"""Example:

		   >>> db.gql({"select": "*", "where": "test=true"})
		   {u'rows': [{u'test': True, u'_rev': u'1-cc9758ad917693b82d8d30860f99c3c7', u'_id': u'mytest'}]}

		   Check out the the `JavaScript documentation
		   <http://pouchdb.com/gql.html>`_ for this function for more
		   details on how to call it.

		"""		
		return _call(self._id, "gql", callback, query, options)

	def spatial(self, fun, callback=None, **options):
		"""Example:

		   >>> db.spatial('foo/test', start_range=[None], end_range=[None])
		   {u'rows': [{u'geometry': None, u'value': {u'_rev': u'1-05e1e004ee4da9e5278a4b177d18a70f', u'foo': u'bar', u'key': [1], u'_id': u'7B1FA329-0522-48B0-A709-75F8F8403B87'}, u'id': u'7B1FA329-0522-48B0-A709-75F8F8403B87', u'key': [[1, 1]]}]}

		"""
		return _call(self._id, "spatial", callback, fun, options)
