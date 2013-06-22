"""This module contains general utility methods used in other modules."""

from xml.dom.minidom import Document
from defusedxml import minidom

import logging
logger = logging.getLogger(__name__)


def xml_dump(obj):
    """This method generates an XML document from a python dict or list.

    XML does not support data types. As a result, there is no equivalent of
    a python dictionary or list in XML. This method accounts for this by using
    a standard language for describing lists and dictionaries.

    The term `resource` denotes a dictionary.

    The term `resources` denotes a list.

    For example::

        {
            "name": "Juan Perez",
            "age": 36,
            "friends": [
                {
                    "name": "John Doe",
                    "age": 29
                }
            ]
        }

    would be serialized as::

        <resource>
            <name>Juan Perez</name>
            <age>36</age>
            <friends>
                <resources>
                    <resource>
                        <name>John Doe</name>
                        <age>29</age>
                    </resource>
                </resources>
            </friends>
        </resource>
    """

    document = Document()

    logger.info("Beginning XML serialization of object.")

    def _serialize_obj(obj):

        if type(obj) is dict:

            element = document.createElement('resource')

            for key, value in obj.iteritems():

                node = document.createElement(key)
                node.appendChild(_serialize_obj(value))

                element.appendChild(node)

            return element

        elif type(obj) in [list, tuple]:

            element = document.createElement('resources')

            for item in obj:

                element.appendChild(_serialize_obj(item))

            return element

        else:

            return document.createTextNode(str(obj))

    document.appendChild(_serialize_obj(obj))

    logger.info("Ending XML serialization of object.")

    return document.toprettyxml()


def xml_load(text):
    """This method generates a python dict or list from an XML document.

    XML does not support data types. As a result, there is no equivalent of
    a python dictionary or list in XML. This method accounts for this by using
    a standard language for describing lists and dictionaries.

    The term `resource` denotes a dictionary.

    The term `resources` denotes a list.

    For example::

        <resource>
            <name>Juan Perez</name>
            <age>36</age>
            <friends>
                <resources>
                    <resource>
                        <name>John Doe</name>
                        <age>29</age>
                    </resource>
                </resources>
            </friends>
        </resource>

    would be serialized as::

        {
            "name": "Juan Perez",
            "age": 36,
            "friends": [
                {
                    "name": "John Doe",
                    "age": 29
                }
            ]
        }

    In order to account for types in the XML, the following logic is applied:

    -   Try convert to int
    -   Try convert to float
    -   Try convert to bool
    -   Fallback to str

    """

    document = minidom.parseString(text)
    root = document.childNodes[0]

    logger.info("Beginning XML deserialization of object.")

    def _deserialize_node(node):

        if node.nodeName == '#text':

            try:
                return int(node.nodeValue)
            except:
                pass

            try:
                return float(node.nodeValue)
            except:
                pass

            if node.nodeValue.upper() == 'TRUE':
                return True

            if node.nodeValue.upper() == 'FALSE':
                return False

            return node.nodeValue

        elif node.nodeName == 'resource':

            element = {}

            for child in node.childNodes:

                k, v = _deserialize_node(child)

                element[k] = v

            return element

        elif node.nodeName == 'resources':

            return [_deserialize_node(child) for child in node.childNodes]

        else:

            return node.nodeName, _deserialize_node(node.childNodes[0])

    deserialized_obj = _deserialize_node(root)

    logger.info("Ending XML deserialization of object.")

    return deserialized_obj
