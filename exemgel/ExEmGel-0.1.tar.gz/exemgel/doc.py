import xml.etree.ElementTree as ET

import node


class Doc(node.Node):
    def __init__(self, file_name):
        self._file_name = file_name
        self._tree = ET.parse(file_name)
        self._root = self._tree.getroot()
        super(Doc, self).__init__(self._root)
