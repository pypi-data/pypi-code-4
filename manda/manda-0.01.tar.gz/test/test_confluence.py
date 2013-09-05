# Author: Jeff Vogelsang <jeffvogelsang@gmail.com>
#
# Copyright 2013 Jeff Vogelsang.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from manda import connect_confluence
import os
from pprint import pprint
import base64
import random
import string
import tempfile
import unittest
from random import randrange

# See: https://developer.atlassian.com/display/CONFDEV/Remote+Confluence+Methods


def rand_string(count=12):
    """Return random string of length count with letters and numbers, mixed case. Uses Python randomness."""

    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(count))

# Ensure that live tests only run if MANDA_TEST_LIVE variable is present in the environment and set to 'True'

# Note: Live tests are designed to reasonably safely create and destroy Atlassian inventory without affecting
#       existing configuration.
enable_live_tests = os.environ.get('MANDA_TEST_LIVE')
if enable_live_tests is not None and enable_live_tests == 'True':
    enable_live_tests = True

@unittest.skipIf(not enable_live_tests, 'Live connection tests skipped.')
class TestConfluenceLive(unittest.TestCase):
    """Live tests. Prove code works against live API."""

    def setUp(self):

        self.conn = connect_confluence()

        self.test_space = 'TEST'
        self.test_page = 'Log'  # The Title of a page we can attach test pages to.
        self.test_page_id = 18677764  # The ID of page we can attach test pages to.

    def tearDown(self):

        pass

    def testAddPage(self):

        # Add page, get its ID.
        rand_content = rand_string()
        page_id = self.conn.add_page(
            'Test', "Test_%s" % rand_content, "<h1>Test_%s</h1>" % rand_content, self.test_page_id)['id']

        # Get the page by ID, make sure the title and content match.
        page = self.conn.get_page_by_id(page_id)
        self.assertEqual("Test_%s" % rand_content, page['title'])
        self.assertEqual("<h1>Test_%s</h1>" % rand_content, page['content'])

    def testUpdatePage(self):

        # Add a page
        rand_content = rand_string()
        page_id = self.conn.add_page(
            'Test', "Test_%s" % rand_content, "<h1>Test_%s</h1>" % rand_content, self.test_page_id)['id']

        # Update the page content.
        content = "<p>PURPLE_%s</p>" % rand_string()
        self.conn.update_page_content(page_id, content=content)

        # Get the page, and check the content.
        page = self.conn.get_page_by_id(page_id)
        self.assertEqual(content, page['content'])

    def testRemovePageById(self):
        # void removePage(String token, String pageId) - removes a page
        # removePage returns either an error packet 'error', or a result item 'result' with True.

        # Add a page
        rand_content = rand_string()
        page_id = self.conn.add_page(
            'Test', "Test_%s" % rand_content, "<h1>Test_%s</h1>" % rand_content, self.test_page_id)['id']

        # Then delete it.
        self.assertTrue(self.conn.remove_page_by_id(page_id))

    def testRemovePageBySpaceAndTitle(self):
        # void removePage(String token, String pageId) - removes a page
        # removePage returns either an error packet 'error', or a result item 'result' with True.

        # Add a page
        rand_content = rand_string()
        title = "Test_%s" % rand_content
        content = "<h1>Test_%s</h1>" % rand_content
        page_id = self.conn.add_page(
            self.test_space, title, content, self.test_page_id)['id']

        # Then delete it.
        self.assertTrue(self.conn.remove_page_by_space_and_title(self.test_space, title))

    def testGetPageById(self):

        # Add a page
        rand_content = rand_string()
        page_id = self.conn.add_page(
            'Test', "Test_%s" % rand_content, "<h1>Test_%s</h1>" % rand_content, self.test_page_id)['id']

        # Get the page, compare the IDs, title, and content.
        page = self.conn.get_page_by_id(page_id)
        self.assertEqual(page_id, page['id'])
        self.assertEqual("Test_%s" % rand_content, page['title'])
        self.assertEqual("<h1>Test_%s</h1>" % rand_content, page['content'])

        # Then delete it.
        self.assertTrue(self.conn.remove_page_by_id(page_id))

    def testGetPageBySpaceAndTitle(self):

        # Add a page
        rand_content = rand_string()
        title = "Test_%s" % rand_content
        content = "<h1>Test_%s</h1>" % rand_content
        page_id = self.conn.add_page(
            self.test_space, title, content, self.test_page_id)['id']

        # Get the page by space and title, compare IDs, title, and content.
        page = self.conn.get_page_by_space_and_title(self.test_space, title)
        self.assertEqual(page_id, page['id'])
        self.assertEqual("Test_%s" % rand_content, page['title'])
        self.assertEqual("<h1>Test_%s</h1>" % rand_content, page['content'])

        # Then delete it.
        self.assertTrue(self.conn.remove_page_by_id(page_id))

    def testAddAttachment(self):

        # Attachment addAttachment(String token, long contentId, Attachment attachment, byte[] attachmentData)

        rand_content = rand_string()
        file_name = "file_%s.jpg" % rand_content

        attachment1 = self.conn.add_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg')
        self.conn.remove_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg')

        attachment2 = self.conn.add_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg', file_name=file_name)
        self.conn.remove_attachment(self.test_page_id, file_name=file_name)

    def testRemoveAttachment(self):

        # Create a new attachment.
        rand_content = rand_string()
        file_name = "file_%s.jpg" % rand_content
        attachment = self.conn.add_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg', file_name=file_name)

        # Then remove it.
        self.assertTrue(self.conn.remove_attachment(self.test_page_id, file_name))

    def testGetAttachmentInfo(self):

        # Create a new attachment.
        rand_content = rand_string()
        file_name = "file_%s.jpg" % rand_content
        attachment = self.conn.add_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg', file_name=file_name)
        attachment_test = self.conn.get_attachment_info(self.test_page_id, file_name)

        self.assertEqual(attachment['id'], attachment_test['id'])
        self.assertEqual(attachment['title'], attachment_test['title'])
        self.assertEqual(attachment['fileName'], attachment_test['fileName'])

        self.conn.remove_attachment(self.test_page_id, file_name)

    def testGetAttachmentData(self):

        # Create a new attachment.
        rand_content = rand_string()
        file_name = "file_%s.jpg" % rand_content
        attachment = self.conn.add_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg', file_name=file_name)

        # Read in file and get encoded version.
        with open('300px-Manda_the_kaiju.jpg') as attachment_file:
            attachment_file_data = base64.b64encode(attachment_file.read())

        # Get encoded version from Confluence, and check against locally read file.
        attachment_file_test_data = self.conn.get_attachment_data(self.test_page_id, file_name)
        self.assertEqual(attachment_file_data, attachment_file_test_data)

        self.conn.remove_attachment(self.test_page_id, file_name)

    def testSaveAttachmentData(self):

        # Create a new attachment.
        rand_content = rand_string()
        file_name = "file_%s.jpg" % rand_content
        attachment = self.conn.add_attachment(self.test_page_id, '300px-Manda_the_kaiju.jpg', file_name=file_name)

        # Read in local file and get encoded version.
        with open('300px-Manda_the_kaiju.jpg') as attachment_file:
            attachment_file_data = base64.b64encode(attachment_file.read())

        # Get a temp file name we can use.
        attachment_file_test_name = rand_string(32)

        # Save out the remote attachment.
        self.conn.save_attachment_data(attachment_file_test_name, self.test_page_id, file_name)

        # Read saved remote version, encode, then delete.
        with open(attachment_file_test_name) as attachment_file_test:
            attachment_file_test_data = base64.b64encode(attachment_file_test.read())
        os.remove(attachment_file_test_name)

        # Make sure they are the same.
        self.assertEqual(attachment_file_data, attachment_file_test_data)

        self.conn.remove_attachment(self.test_page_id, file_name)

    def testGetPageChildren(self):

        # self.conn.get_page_children(self.test_page_id)
        pass

    def testGetPageDescendants(self):

        # self.conn.get_page_descendants(self.test_page_id)
        pass

        # Delete all the descendants of the current page.
        # for page in pages:
        #     self.conn.remove_page_by_id(page['id'])

if __name__ == '__main__':

    unittest.main(verbosity=2)