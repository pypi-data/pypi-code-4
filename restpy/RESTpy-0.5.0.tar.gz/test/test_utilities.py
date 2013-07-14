import pytest

from restpy.utilities import xml_load, xml_dump


def test_serialization_to_xml():

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

    assert expected_result == result


def test_deserialization_from_xml():

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

    assert isinstance(result, dict)

    assert "int" in result
    assert isinstance(result['int'], int)
    assert result['int'] == 123

    assert "bool" in result
    assert isinstance(result['bool'], bool)
    assert result['bool'] is True

    assert "string" in result
    assert isinstance(result['string'], basestring)
    assert result['string'] == "test"

    assert "list" in result
    assert isinstance(result['list'], list)
    assert len(result['list']) == 1

    assert isinstance(result['list'][0], dict)
    assert "dict" in result['list'][0]
    assert isinstance(result['list'][0]['dict'], dict)


# Deserialization fails when input is formatted due to the parser
# is picking up newlines and tabs as text nodes rather than ignoring them.
@pytest.mark.xfail
def test_deserialization_from_xml_formatted():

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

    assert isinstance(result, dict)

    assert "int" in result
    assert isinstance(result['int'], int)
    assert result['int'], 123

    assert "bool" in result
    assert isinstance(result['bool'], bool)
    assert result['bool'] is True

    assert "string" in result
    assert isinstance(result['string'], basestring)
    assert result['string'] == "test"

    assert "list" in result
    assert isinstance(result['list'], list)
    assert len(result['list']) == 1

    assert isinstance(result['list'][0], dict)
    assert "dict" in result['list'][0]
    assert isinstance(result['list'][0]['dict'], dict)
