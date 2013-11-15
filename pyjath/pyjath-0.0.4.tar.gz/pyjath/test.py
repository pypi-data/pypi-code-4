from lxml import etree
from pyjath import PyJath
from io import StringIO
import unittest

class TestPyPath(unittest.TestCase):

	def test_nominal(self):
		self.assertTrue(True)

	def test_jath(self):
		pp = PyJath()
		xml = u"""
			<statuses userid="djn">
				<status id="1">
					<message>Hello</message>
				</status>
				<status id="3">
					<message>Goodbye</message>
				</status>
			</statuses>
		"""
		sio = StringIO(xml)
		tree = etree.parse(sio)

		expected = [ 
			{ "id": "1", "message": "Hello" }, 
			{ "id": "3", "message": "Goodbye" } 
		]


		template = [ "//status", { "id": "@id", "message": "message" } ]
		actual = pp.parse(template, tree)
		self.assertEqual(actual, expected)

	def test_literal(self):
		pp = PyJath()
		xml = u"""
			<statuses userid="djn">
				<status id="1">
					<message>Hello</message>
				</status>
				<status id="3">
					<message>Goodbye</message>
				</status>
			</statuses>
		"""
		sio = StringIO(xml)
		tree = etree.parse(sio)

		expected = [ 
			{ "id": "1", "message": "Hello", "literal": "jath" }, 
			{ "id": "3", "message": "Goodbye", "literal": "jath" } 
		]


		template = [ "//status", { "id": "@id", "message": "message", "literal": ":jath" } ]
		actual = pp.parse(template, tree)
		self.assertEqual(actual, expected)

	def test_jath_recursive(self):
		pp = PyJath()
		xml = u""" 
		<item name="foo">
			<status code="1" />
			<item name="bar">
				'<status code="2" />
			</item>
			<item name="baz">
				<status code="3" />
				<item name="biff">
					<status code="4" />
				</item>
			</item>
		</item>"""
		sio = StringIO(xml)
		tree = etree.parse(sio)
			
		template = [ 'item', { 'name': '@name', 'status': 'status/@code', 'items': None } ]
		template[1]['items'] = template;

		expected = [
			{"name":"foo","status":"1","items":[
				{"name":"bar","status":"2","items":[]},
				{"name":"baz","status":"3","items":[
					{ "name":"biff","status":"4","items":[]}]}]}
		]

		actual = pp.parse(template, tree)
		print actual
		print expected
		#self.assertEqual(actual, expected)
		#self.assertFail()

	def test_jath_arraylike(self):
		pp = PyJath()

		xml = u"""
			<root>
				<a>
					<b>123</b>
					<b>456</b>
					<b>789</b>
				</a>
				<a>
					<b>foo</b>
					<b>bar</b>
				</a>
			</root>"""

		sio = StringIO(xml)
		tree = etree.parse(sio)

		template = [ '//a', [ 'b', 'text()' ] ]

		actual = pp.parse(template, tree)

		expected = [ ["123","456","789"], ["foo","bar"] ]
		self.assertEqual(actual, expected)


	def template_jath_test(self):
		""" use this as a template for tests """
		pp = PyJath()

		xml = u"""
		"""
		sio = StringIO(xml)
		tree = etree.parse(sio)
		template = []

		actual = pp.parse(template, tree)
		expected = []
		self.assertEqual(actual, expected)



	def test_jath_nested_array(self):
		pp = PyJath()

		xml = u"""
		<labels> 
			<label id="ep" added="2003-06-10"> 
				<name>Ezra Pound</name> 
				<address> 
				  <street>45 Usura Place</street> 
				  <city>Hailey</city> 
				  <province>ID</province> 
				</address> 
			  </label> 
			  <label id="ep2" added="2003-06-20"> 
				<name>Siju</name> 
				<address> 
				  <street>3 Prufrock Lane</street> 
				  <city>Stamford</city> 
				  <province>ID</province> 
				</address> 
				<address> 
				  <street>2nd address</street> 
				  <city>2nd city</city> 
				  <province>2nd id</province> 
				</address> 
				<address> 
				  <street>3rd address</street> 
				  <city>3rd city</city> 
				  <province>3rd id</province> 
				</address> 
			  </label> 
		  </labels>
		"""
		sio = StringIO(xml)
		tree = etree.parse(sio)
		template = [ 
			'//label', { 'id': '@id', 'added': '@added', 
				'address': [ 'address', { 'street': 'street', 'city': 'city' } ] 
		} ]

		actual = pp.parse(template, tree)
		expected = [{"id":"ep","added":"2003-06-10","address":[{"street":"45 Usura Place","city":"Hailey"}]},{"id":"ep2","added":"2003-06-20","address":[{"street":"3 Prufrock Lane","city":"Stamford"},{"street":"2nd address","city":"2nd city"},{"street":"3rd address","city":"3rd city"}]}]
		self.assertEqual(actual, expected)

		
	def test_jath_namespace(self):
		f = open('pyjath/labels-ns.xml')
		""" use this as a template for tests """
		pp = PyJath()
		pp.namespaces = {"empty": "http://example.com", "lbl": "http://example.com/labelns"}

		tree = etree.parse(f)
		template = [ "//lbl:label", { "id": "@id", "added": "@added" } ];

		actual = pp.parse(template, tree)

		expected = [
		  {
			"id": "ep",
			"added": "2003-06-10"
		  },
		  {
			"id": "tse",
			"added": "2003-06-20"
		  },
		  {
			"id": "lh",
			"added": "2004-11-01"
		  },
		  {
			"id": "co",
			"added": "2004-11-15"
		  }
		];

		self.assertEqual(actual, expected)
