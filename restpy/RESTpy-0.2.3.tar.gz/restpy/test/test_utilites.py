import unittest

from restpy.utilities import xml_load, xml_dump


class TestXML(unittest.TestCase):

    def setUp(self, *args, **kwargs):

        super(TestXML, self).setUp(*args, **kwargs)

    def test_serialization_to_xml(self):

        data = {
            "int": 123,
            "bool": True,
            "string": "test",
            "list": [
                {
                    "dict": {}
                }
            ]
        }

        expected_result = ('<?xml version="1.0" ?>\n<resource>\n'
                           '\t<int>123</int>\n'
                           '\t<list>\n'
                           '\t\t<resources>\n'
                           '\t\t\t<resource>\n'
                           '\t\t\t\t<dict>\n'
                           '\t\t\t\t\t<resource/>\n'
                           '\t\t\t\t</dict>\n'
                           '\t\t\t</resource>\n'
                           '\t\t</resources>\n'
                           '\t</list>\n'
                           '\t<bool>True</bool>\n'
                           '\t<string>test</string>\n'
                           '</resource>\n')

        result = xml_dump(data)

        self.assertEqual(expected_result, result)

    def test_deserialization_from_xml(self):

        data = ('<?xml version="1.0" ?><resource>'
                '<int>123</int>'
                '<list>'
                '<resources>'
                '<resource>'
                '<dict>'
                '<resource/>'
                '</dict>'
                '</resource>'
                '</resources>'
                '</list>'
                '<bool>True</bool>'
                '<string>test</string>'
                '</resource>')

        result = xml_load(data)

        self.assertTrue(isinstance(result, dict))

        self.assertTrue("int" in result)
        self.assertTrue(isinstance(result['int'], int))
        self.assertEqual(result['int'], 123)

        self.assertTrue("bool" in result)
        self.assertTrue(isinstance(result['bool'], bool))
        self.assertEqual(result['bool'], True)

        self.assertTrue("string" in result)
        self.assertTrue(isinstance(result['string'], basestring))
        self.assertEqual(result['string'], "test")

        self.assertTrue("list" in result)
        self.assertTrue(isinstance(result['list'], list))
        self.assertEqual(len(result['list']), 1)

        self.assertTrue(isinstance(result['list'][0], dict))
        self.assertTrue("dict" in result['list'][0])
        self.assertTrue(isinstance(result['list'][0]['dict'], dict))

    # Deserialization fails when input is formatted due to the parser
    # is picking up newlines and tabs as text nodes rather than ignoring them.
    @unittest.expectedFailure
    def test_deserialization_from_xml_formatted(self):

        data = ('<?xml version="1.0" ?>\n<resource>\n'
                '\t<int>123</int>\n'
                '\t<list>\n'
                '\t\t<resources>\n'
                '\t\t\t<resource>\n'
                '\t\t\t\t<dict>\n'
                '\t\t\t\t\t<resource/>\n'
                '\t\t\t\t</dict>\n'
                '\t\t\t</resource>\n'
                '\t\t</resources>\n'
                '\t</list>\n'
                '\t<bool>True</bool>\n'
                '\t<string>test</string>\n'
                '</resource>\n')

        result = xml_load(data)

        self.assertTrue(isinstance(result, dict))

        self.assertTrue("int" in result)
        self.assertTrue(isinstance(result['int'], int))
        self.assertEqual(result['int'], 123)

        self.assertTrue("bool" in result)
        self.assertTrue(isinstance(result['bool'], bool))
        self.assertEqual(result['bool'], True)

        self.assertTrue("string" in result)
        self.assertTrue(isinstance(result['string'], basestring))
        self.assertEqual(result['string'], "test")

        self.assertTrue("list" in result)
        self.assertTrue(isinstance(result['list'], list))
        self.assertEqual(len(result['list']), 1)

        self.assertTrue(isinstance(result['list'][0], dict))
        self.assertTrue("dict" in result['list'][0])
        self.assertTrue(isinstance(result['list'][0]['dict'], dict))
