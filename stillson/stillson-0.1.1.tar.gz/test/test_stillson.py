#
# Copyright 2013 Mortar Data Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest2 as unittest
import os
import tempfile
from stillson import stillson

class TestStillson(unittest.TestCase):

    def setUp(self):
        os.environ.clear()
        self.assertEqual(0,len(os.environ))
        self.example_config = '../examples/client.cfg.template'
        self.template_file = tempfile.NamedTemporaryFile(suffix='.template')
        self.output_file = tempfile.NamedTemporaryFile()

    def tearDown(self):
        self.template_file.close()
        self.output_file.close()

    def test_happy_path(self):
        os.environ['foo']='bar'
        self.assertEqual('bar',os.environ['foo'])
        self.template_file.write('[test]\nfoo:${foo}')
        self.template_file.flush()
        stillson.render(self.template_file.name,self.output_file)
        self.output_file.seek(0)
        self.assertEqual('[test]\nfoo:bar',self.output_file.read())

    def test_missing_template(self):
        template_path = os.path.join(tempfile.mkdtemp(),'missing.txt')
        self.assertRaises(IOError,stillson.render,template_path,self.output_file)

    def test_missing_variable(self):
        os.environ['foo']='bar'
        self.assertEqual('bar',os.environ['foo'])
        self.template_file.write('[test]\nfoo:${not_here}')
        self.template_file.flush()
        try:
            stillson.render(self.template_file.name,self.output_file)
            self.fail('missing variable to throw an exception')
        except stillson.StillsonMissingEnvVariable as e:
            self.assertIn('not_here',str(e)) #Todo expect line number

    def test_permission_template(self):
        broken_template_file = \
            tempfile.NamedTemporaryFile(suffix='.template',delete=False)
        broken_template_file.write('stuff')
        broken_template_file.close()
        os.chmod(broken_template_file.name,0100)
        self.assertRaises(IOError,stillson.render,
                          broken_template_file.name,self.output_file)

    def test_permission_output(self):
        broken_output_file = \
            tempfile.NamedTemporaryFile(mode='r')
        self.assertRaises(IOError,stillson.render,
                          self.template_file.name,broken_output_file)
