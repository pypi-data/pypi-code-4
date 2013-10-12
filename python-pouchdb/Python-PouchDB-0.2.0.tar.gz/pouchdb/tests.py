# coding=UTF-8

import pouchdb
import unittest
import requests
import json
import os

configPath = os.path.join(os.path.dirname(__file__), "testconfig.json")
try:
	with open(configPath) as f:#pragma: no branch
		data = json.load(f)
except IOError:#pragma: no cover
	data = {}
USERNAME = data.get("username")
PASSWORD = data.get("password")
BASE_URL = data.get("base_url", "http://localhost:5984")

pouchdb.baseUrl = BASE_URL
pouchdb.enableAllDbs = True

def cleanup():
	#reset the context
	pouchdb.getContext().reset()
	pouchdb.getContext().setStaticProperty("enableAllDbs", True)

class PouchDBTestCase(unittest.TestCase):
	def tearDown(self):
		cleanup()

class PouchDBTestCaseWithDB(PouchDBTestCase):
	def setUp(self):
		self._db = pouchdb.PouchDB("test")

class PouchDBTestCaseWithDBAndDoc(PouchDBTestCaseWithDB):
	def setUp(self):
		super(PouchDBTestCaseWithDBAndDoc, self).setUp()

		resp = self._db.put({"_id": "mytest", "test": True})
		self.rev = resp["rev"]

class PouchDBTestCaseWithDBAndAttachment(PouchDBTestCaseWithDB):
	def setUp(self):
		super(PouchDBTestCaseWithDBAndAttachment, self).setUp()

		resp = self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain")
		self.rev = resp["rev"]

class AllDbsTests(PouchDBTestCase):
	def testEmpty(self):
		self.assertTrue(pouchdb.enableAllDbs)
		self.assertEqual(pouchdb.allDbs(), [])

	def testWithDbAndAllDbsEnabled(self):
		db = pouchdb.PouchDB("test")
		self.assertEqual(pouchdb.allDbs(), ["test"])

class PutTests(PouchDBTestCaseWithDB):
	def testSimplePut(self):
		resp = self._db.put({"_id": "mytest", "test": True})
		self.assertEqual(resp["id"], "mytest")

	def testAsyncPut(self):
		result = {}
		def callback(err, resp=None):
			result["err"] = err
			result["resp"] = resp
		self.assertIsNone(self._db.put({"_id": "abcd", "something": 26}, callback))
		self.assertFalse(result)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertTrue(result["resp"]["ok"])

class PostTests(PouchDBTestCaseWithDB):
	def testSimplePost(self):
		self.assertTrue(self._db.post({"test": False})["ok"])

class GetTests(PouchDBTestCaseWithDBAndDoc):
	def testSimpleGet(self):
		doc = self._db.get("mytest")
		self.assertEqual(doc["_id"], "mytest")

	def testMissingDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.get("unexisting-doc")
		self.assertEqual(cm.exception["status"], 404)
		self.assertIn("404", str(cm.exception))

class RemoveTests(PouchDBTestCaseWithDBAndDoc):
	def testSimpleRemove(self):
		doc = self._db.get("mytest")
		self.assertTrue(self._db.remove(doc)["ok"])

class BulkDocsTests(PouchDBTestCaseWithDB):
	def testSimpleBulkDocs(self):
		resp = self._db.bulkDocs({
			"docs": [
				{
					"a": 1,
					"b": 2,
				},
				{
					
					"c": 3,
					"d": 4,
				},
			],
		})
		self.assertEqual(len(resp), 2)

class AllDocsTests(PouchDBTestCaseWithDB):
	def setUp(self):
		super(AllDocsTests, self).setUp()

	def testAllDocsWithEmptyDB(self):
		resp = self._db.allDocs(include_docs=True)
		self.assertEqual(len(resp["rows"]), 0)

	def testAllDocsWithNonEmptyDB(self):
		self._db.post({})

		resp = self._db.allDocs(include_docs=True)
		self.assertEqual(len(resp["rows"]), 1)

class QueryTests(PouchDBTestCaseWithDB):
	def setUp(self):
		super(QueryTests, self).setUp()

	@property
	def _func(self):
		return {
			"map": """function (doc) {
				emit(null, doc._rev);
			}""",
		}

	def testQueryWithEmptyDB(self):
		resp = self._db.query(self._func)
		self.assertEqual(len(resp["rows"]), 0)

	def testAllDocsWithNonEmptyDB(self):
		self._db.post({})

		resp = self._db.query(self._func)
		self.assertEqual(len(resp["rows"]), 1)

class InfoTests(PouchDBTestCaseWithDB):
	def testSimpleInfo(self):
		self.assertIn("update_seq", self._db.info())

class CompactTests(PouchDBTestCaseWithDB):
	def testCompactOnEmptyDB(self):
		self.assertIsNone(self._db.compact())

	def testCompactOnNonEmptyDB(self):
		self._db.post({})
		self.assertIsNone(self._db.compact())

class RevsDiffTests(PouchDBTestCaseWithDB):
	def testSimpleRevsDiff(self):
		resp = self._db.revsDiff({
			"myDoc1": [
				"1-b2e54331db828310f3c772d6e042ac9c",
				"2-3a24009a9525bde9e4bfa8a99046b00d",
			],
		})
		#the doc isn't in the db
		self.assertEqual(len(resp["myDoc1"]["missing"]), 2)

class PutAttachmentTests(PouchDBTestCaseWithDB):
	def testSimplePutAttachment(self):
		resp = self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain")
		self.assertTrue(resp["ok"])

	def testPutTwoAttachmentsInSameDoc(self):
		resp = self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain")
		rev = resp["rev"]
		resp2 = self._db.putAttachment("attachment_test", "text2", u"éfgh".encode("UTF-8"), "text/plain", rev)
		self.assertTrue(resp2["ok"])

	def testPutAttachmentAsync(self):
		result = {}
		def putAttachmentCallback(err, resp):
			result["err"] = err
			result["resp"] = resp

		self._db.putAttachment("attachment_test", "text", b"abcd", "text/plain", callback=putAttachmentCallback)
		pouchdb.getContext().waitUntilCalled(putAttachmentCallback)
		self.assertTrue(result["resp"]["ok"])

class GetAttachmentTests(PouchDBTestCaseWithDBAndAttachment):
	def testSimpleGetAttachment(self):
		resp = self._db.getAttachment("attachment_test", "text")
		self.assertEqual(resp["data"], b"abcd")

	def testGetAttachmentAsync(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.getAttachment("attachment_test", "text", callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertEqual(result["resp"]["data"], b"abcd")

	def testMissingDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.getAttachment("unexisting_doc", "text")
		self.assertEqual(cm.exception["status"], 404)

	def testMissingAttachment(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.getAttachment("attachment_test", "unexisting_attachment")
		self.assertEqual(cm.exception["status"], 404)

	def testMissingAttachmentAsync(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.getAttachment("attachment_test", "unexisting_attachment", callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertEqual(result["err"]["status"], 404)

class RemoveAttachmentTests(PouchDBTestCaseWithDBAndAttachment):
	def testSimpleRemoveAttachment(self):
		resp = self._db.removeAttachment("attachment_test", "text", self.rev)
		self.assertTrue(resp["ok"])

	def testRemoveAttachmentAsync(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.removeAttachment("attachment_test", "text", self.rev, callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertTrue(result["resp"]["ok"])

	def testRemoveUnexistingAttachment(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.removeAttachment("attachment_test", "unexisting-attachment", self.rev)
		self.assertEqual(cm.exception["status"], 404)

	def testRemoveUnexistingAttachmentAsync(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.removeAttachment("attachment_test", "unexisting-attachment", self.rev, callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertTrue(result["err"]["status"], 404)

	def testRemoveAttachmentFromUnexistingDoc(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.removeAttachment("unexisting-doc", "text", self.rev)
		self.assertEqual(cm.exception["status"], 404)

	def testRemoveAttachmentFromUnexistingDocAsync(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp
		self._db.removeAttachment("unexisting-doc", "text", self.rev, callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertTrue(result["err"]["status"], 404)

class ReplicateTests(PouchDBTestCaseWithDBAndDoc):
	def testSimpleReplicate(self):
		resp = pouchdb.replicate("test", "testb")
		self.assertTrue(resp["ok"])

	def testReplicateWithOnComplete(self):
		result = {}
		def onComplete(err, resp):
			result["err"] = err
			result["resp"] = resp

		promise = pouchdb.replicate("test", "testb", onComplete=onComplete)
		self.assertFalse(promise["cancelled"])
		pouchdb.getContext().waitUntilCalled(onComplete)
		self.assertEqual(result["resp"]["docs_written"], 1)

	def testSimpleReplicateTo(self):
		self.assertTrue(self._db.replicate_to("testb")["ok"])
		db = pouchdb.PouchDB("testb")
		#this should not throw a PouchDBError
		db.get("mytest")

	def testSimpleReplicateFrom(self):
		self.assertTrue(self._db.replicate_from("testb")["ok"])

	def testContinuous(self):
		resp = self._db.replicate_to("testb", continuous=True)
		self.assertIsNone(resp["cancel"]())

		resp2 = self._db.replicate_from("testb", continuous=True)
		self.assertIsNone(resp2["cancel"]())

		resp3 = pouchdb.replicate("test", "testb", continuous=True)
		self.assertIsNone(resp3["cancel"]())

	def testReplicateFromWithCallback(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp

		self._db.replicate_from("testb", callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertEqual(result["resp"]["docs_written"], 0)

	def testReplicateToWithCallback(self):
		result = {}
		def callback(err, resp):
			result["err"] = err
			result["resp"] = resp

		self._db.replicate_to("testb", callback)
		pouchdb.getContext().waitUntilCalled(callback)
		self.assertEqual(result["resp"]["docs_written"], 1)

class ChangesTests(PouchDBTestCaseWithDBAndDoc):
	def testSimpleChanges(self):
		self.assertIsNone(self._db.changes())

	def testContinuous(self):
		resp = self._db.changes(continuous=True)
		self.assertIsNone(resp["cancel"]())

	def testAsync(self):
		data = {}
		def onComplete(err, resp):
			data["err"] = err
			data["resp"] = resp
		self.assertIsNone(self._db.changes(complete=onComplete))
		pouchdb.getContext().waitUntilCalled(onComplete)
		self.assertIn("last_seq", data["resp"])

class DestroyTests(PouchDBTestCaseWithDBAndDoc):
	def testSimpleDestroy(self):
		self.assertIsNone(pouchdb.destroy("test"))
		db = pouchdb.PouchDB("test")
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			db.get("mytest")
		self.assertEqual(cm.exception["status"], 404)

class HttpTests(unittest.TestCase):
	@property
	def _auth(self):
		if USERNAME:#pragma: no branch
			return {
				"username": USERNAME,
				"password": PASSWORD,
			}

	def setUp(self):
		self._db = pouchdb.PouchDB(BASE_URL + "/test", auth=self._auth)

	def testSomeSimpleMethods(self):
		id = self._db.post({"test": True})["id"]
		self.assertTrue(self._db.get(id)["test"])
		self.assertIn(id, str(self._db.allDocs()))

		self.assertIn("db_name", self._db.info())

	def testAttachment(self):
		rev = self._db.putAttachment("attachment-doc", "attachment", b"<h1>Hello World!</h1>", "text/html")["rev"]

		resp = requests.get(BASE_URL + "/test/attachment-doc/attachment")
		self.assertEqual(resp.content, b"<h1>Hello World!</h1>")
		self.assertEqual(resp.headers["Content-Type"], "text/html")

		a = self._db.getAttachment("attachment-doc", "attachment")
		self.assertEqual(a["data"], b"<h1>Hello World!</h1>")
		self.assertEqual(a["type"], "text/html")

		self._db.removeAttachment("attachment-doc", "attachment", rev)

	def testReplication(self):
		rev = self._db.put({"_id": "mytest"})["rev"]
		self._db.replicate_to("local")

		localDb = pouchdb.PouchDB("local")
		self.assertEqual(localDb.get("mytest")["_rev"], rev)

	def tearDown(self):
		pouchdb.destroy(BASE_URL + "/test", auth=self._auth)

class ContextTests(unittest.TestCase):
	def testException(self):
		ctx = pouchdb.getContext()
		with self.assertRaises(Exception) as cm:
			ctx._evalJs("throw new Error('Hello World!')");
		self.assertIn("Hello World!", str(cm.exception))

class ValidationTests(PouchDBTestCaseWithDBAndDoc):
	def setUp(self):
		super(ValidationTests, self).setUp()

		self._db.put({
			"_id": "_design/test",
			"validate_doc_update": """function (newDoc, oldDoc, userCtx, secObj) {
				if (newDoc._id !== "test") {
					throw({forbidden: "only a document named 'test' is allowed."});
				}
			}""",
		})

	def testSuccesfulPut(self):
		doc = self._db.validating.put({"_id": "test"})
		self.assertTrue(doc["ok"])

	def testInvalidPut(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validating.put({"_id": "test_invalid"})
		self.assertIn("forbidden", cm.exception)

	def testInvalidPost(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validating.post({})
		self.assertIn("forbidden", cm.exception)

	def testInvalidDelete(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validating.delete({
				"_id": "mytest",
				"_rev": self.rev,
			})
		self.assertIn("forbidden", cm.exception)

	def testInvalidBulkDocs(self):
		with self.assertRaises(pouchdb.PouchDBError) as cm:
			self._db.validating.bulkDocs({
				"docs": [
					{
						"_id": "test_invalid",
					},
				],
			})
		self.assertIn("forbidden", cm.exception.message[0])

class GQLTests(PouchDBTestCaseWithDBAndDoc):
	def testSelectWhereGql(self):
		resp = self._db.gql({"select": "*", "where": "test=true"})
		self.assertEqual(len(resp["rows"]), 1)

class SpatialTests(PouchDBTestCaseWithDB):
	def testSpatial(self):
		"""Based on the first test in test.spatial.js in the PouchDB
		   test suite.

		"""
		designDoc = {
			'_id': '_design/foo',
			'spatial': {
				'test': 'function(doc) {if (doc.key) {emit(doc.key, doc); }}',
			},
		}
		docs = [
			designDoc,
			{'foo': 'bar', 'key': [1]},
			{'_id': 'volatile', 'foo': 'baz', 'key': [2]},
		]
		self._db.bulkDocs({"docs": docs})
		doc = self._db.get("volatile")
		self._db.remove(doc)

		resp = self._db.spatial('foo/test', start_range=[None], end_range=[None])
		self.assertEqual(len(resp["rows"]), 1, msg='Dont include deleted documents')
		for row in resp["rows"]:
			self.assertIn("key", row, msg='view row has a key')
			self.assertIn("_rev", row["value"], msg='emitted doc has rev')
			self.assertIn("_id", row["value"], msg='emitted doc has id')
