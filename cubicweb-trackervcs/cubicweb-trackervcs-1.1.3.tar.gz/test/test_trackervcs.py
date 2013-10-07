"""trackervcs automatic tests"""

from cubicweb.devtools.fill import ValueGenerator
from cubicweb.devtools.testlib import AutomaticWebTest

class MyValueGenerator(ValueGenerator):
    def generate_Repository_path(self, entity, index):
        return u'/' + self.generate_string(entity, 'path', index)

    def generate_Project_icon(self, entity, index, **kwargs):
        return None

class AutomaticWebTest(AutomaticWebTest):
    '''provides `to_test_etypes` and/or `list_startup_views` implementation
    to limit test scope
    '''
    no_auto_populate = ('VersionContent', 'DeletedVersionContent',
                        'Revision', 'InsertionPoint', 'Patch', 'VersionedFile')
    ignored_relations = set(('nosy_list', 'subproject_of'))

    def to_test_etypes(self):
        '''only test views for entities of the returned types'''
        return set()

    def list_startup_views(self):
        '''only test startup views of the returned identifiers'''
        return ('vcreview.allactivepatches', 'vcreview.patches.worklist')

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
