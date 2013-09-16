from __future__ import absolute_import
import logging
from pyprotobuf.codegenerator import CodeGenerator


class NameCollector(CodeGenerator):
    """ Collects global names into the Frame so the NameResolver doesnt depend on order.
    """

    logger = logging.getLogger('pyprotobuf.NameCollector')

    def visit_EnumNode(self, node):
        self.logger.debug('Adding enum %s', node.get_full_name())

        # add the enumerations to the global scope
        for child in node.children:
            self.frame.add_to_globals(child.get_full_name(), child)


    def visit_MessageNode(self, node):
        self.logger.debug('Adding message %s', node.get_full_name())
        self.frame.add_node(node)