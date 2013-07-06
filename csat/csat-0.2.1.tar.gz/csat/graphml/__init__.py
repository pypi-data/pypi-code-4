import os

from lxml import etree


namespace = ns = 'http://graphml.graphdrawing.org/xmlns'

nsmap = {
    None: namespace,
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}

xpath_nsmap = {
    'g': namespace,
}


def get_schemata_dir():
    return os.path.join(os.path.dirname(__file__), 'schemata')


def get_schema_path():
    return os.path.join(get_schemata_dir(), 'graphml.xsd')


def get_dtd_path():
    return os.path.join(get_schemata_dir(), 'graphml.dtd')


def get_schema():
    with open(get_schema_path()) as fh:
        return etree.XMLSchema(etree.parse(fh))


def get_dtd():
    with open(get_dtd_path()) as fh:
        return etree.DTD(fh)
