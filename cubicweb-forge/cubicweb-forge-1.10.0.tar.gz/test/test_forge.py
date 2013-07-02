"""forge test application"""

from cubicweb.devtools.testlib import AutomaticWebTest

from cubes.forge.testutils import MyValueGenerator


class AutomaticWebTest(AutomaticWebTest):
    no_auto_populate = ('TestInstance',)
    ignored_relations = set(('nosy_list',))

    def post_populate(self, cursor):
        self.commit()
        for version in cursor.execute('Version X').entities():
            version.cw_adapt_to('IWorkflowable').change_state('published')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
