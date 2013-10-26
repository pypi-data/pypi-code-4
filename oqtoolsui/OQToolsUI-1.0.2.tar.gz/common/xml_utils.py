from xml.etree import ElementTree
from xml.dom import minidom


def write_xml(tree, target_file):
    plain_str = ElementTree.tostring(tree.getroot(), encoding='UTF-8')
    parsed_str = minidom.parseString(plain_str)
    parsed_str = parsed_str.toprettyxml(indent='\t', encoding='UTF-8')

    with open(target_file, 'w') as writer:
        writer.write(parsed_str)