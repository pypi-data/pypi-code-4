import os
import unittest
import json

from json_patch import Patch, PatchError


class JSONPatchTestcase(object):
    def _test(self, test):
        print test

        patch = Patch(test['patch'])
        if 'error' in test:
            self.assertRaises(
                PatchError,
                patch.apply,
                test['doc']
            )
        else:
            document = patch.apply(test['doc'])
            
            if 'expected' in test:
                self.assertEqual(document, test['expected'], test.get('comment'))

    def test(self):
        with open(
            os.path.join(
                os.path.dirname(__file__),
                'tests/%s' % self.filename
            ),
            'r'
        ) as json_file:
            tests = json.loads(json_file.read())
            
            for test in [test for test in tests if 'disabled' not in test]:
                self._test(test)
    

class TestJSONPatch(JSONPatchTestcase, unittest.TestCase):
    filename = 'tests.json'


class TestJSONPatchSpec(JSONPatchTestcase, unittest.TestCase):
    filename = 'spec_tests.json'

