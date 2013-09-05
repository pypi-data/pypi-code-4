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

import base64
import json
import os
import random
import requests
import string


def rand_string(count=12):
    """Return random string of length count with letters and numbers, mixed case. Uses Python randomness."""

    return ''.join(random.choice(string.ascii_letters + string.digits) for x in range(count))


class ConfluenceConnection(object):

    def __init__(self, username=None, password=None, domain=None, context=None, protocol="https", port=None):

        # Note: ConfluenceConnection assumes HTTPS.
        self.protocol = protocol

        # Use environment variables for credentials if set.
        if None not in (os.environ.get('MANDA_DOMAIN'),
                        os.environ.get('MANDA_CONTEXT'),
                        os.environ.get('MANDA_USERNAME'),
                        os.environ.get('MANDA_PASSWORD')):

            self.domain = os.environ.get('MANDA_DOMAIN')
            self.context = os.environ.get('MANDA_CONTEXT')
            self.username = os.environ.get('MANDA_USERNAME')
            self.password = os.environ.get('MANDA_PASSWORD')

            # Protocol is optional. If we're using the system environment, pull it in.
            if os.environ.get('MANDA_PROTOCOL') is not None:
                self.protocol = os.environ.get('MANDA_PROTOCOL')

            # Port is optional. If we're using the system environment, pull it in.
            if os.environ.get('MANDA_PORT') is not None:
                self.port = os.environ.get('MANDA_PORT')

        # Use credentials passed to constructor over environment credentials.
        if None not in (username, password, domain, context):
            self.username = username
            self.password = password
            self.domain = domain
            self.context = context

        # Raise error if we haven't managed to set the credentials at this point.
        if None in (getattr(self, 'username', None),
                    getattr(self, 'password', None),
                    getattr(self, 'domain', None),
                    getattr(self, 'context', None)):
            raise AttributeError("Manda credentials and settings not provided or found in environment.")

        #TODO Handle incoming port in base_url

        # Now set the base_url used for operations.
        self.base_url = '%s://%s/%s' % (self.protocol, self.domain, self.context)

        # Authentication tuple for requests
        self.auth = (self.username, self.password)

        # Default headers
        self.headers = headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

        # API URL
        self.api_url = self.base_url + '/rpc/json-rpc/confluenceservice-v2'

    def __repr__(self):
        return "Confluence Connection:%s@%s" % (self.username, self.base_url)

    #### Request/Post / JSON Methods ####

    def _confluence_post(self, data):
        """Posts an XMLRPC JSON packet to Confluence."""

        response = requests.post(self.api_url, data=json.dumps(data), headers=self.headers, auth=self.auth)

        return ConfluenceResponse(response)

    def _get_jsonrpc_packet(self, json_rpc_method, json_rpc_params=None, json_rpc_id=None):
        """Returns a properly constructed XMLRPC JSON packet."""

        return {
            'jsonrpc': '2.0',
            'method': json_rpc_method,
            'params': json_rpc_params,
            'id': json_rpc_id
        }

    #### Pages ####

    def add_page(self, space, title, content, parent_id=None):
        """Returns a response object page as a dict constructed from the JSON response."""

        page = {'space': space, 'title': title, 'content': content, 'parentId': parent_id}
        jsonrpc_packet = self._get_jsonrpc_packet('storePage', [page])

        return self._confluence_post(jsonrpc_packet).result

    def update_page_content(self, page_id, content):
        """Returns a response object with info on whether the update was successful."""

        current_page = self.get_page_by_id(page_id)

        updated_page = {}
        update_fields = ["id", "space", "title", "content", "version"]
        for field in update_fields:
            updated_page[field] = current_page[field]

        updated_page['content'] = content

        jsonrpc_packet = self._get_jsonrpc_packet('storePage', [updated_page])

        return self._confluence_post(jsonrpc_packet).result

    def get_page_by_id(self, page_id):
        """Get a Confluence page given its page ID.
        Returns a result containing a Confluence Page object as dict."""

        params = [page_id]
        jsonrpc_packet = self._get_jsonrpc_packet('getPage', params)

        return self._confluence_post(jsonrpc_packet).result

    def get_page_by_space_and_title(self, space_name, page_title):
        """Get a Confluence page given its Space and Title.
        Returns a result containing a Confluence Page object as dict."""

        params = [space_name, page_title]
        jsonrpc_packet = self._get_jsonrpc_packet('getPage', params)

        return self._confluence_post(jsonrpc_packet).result

    def get_page_id_by_space_and_title(self, space_name, page_title):
        """Get a Confluence page ID given its Space and Title."""

        return self.get_page_by_space_and_title(space_name, page_title)['id']

    def remove_page_by_id(self, page_id):
        """Returns a response object with info on whether the removal was successful."""

        jsonrpc_packet = self._get_jsonrpc_packet('removePage', [page_id])

        return self._confluence_post(jsonrpc_packet).result

    def remove_page_by_space_and_title(self, space_name, page_title):
        """Returns a response object with info on whether the removal was successful."""

        page_id = self.get_page_id_by_space_and_title(space_name, page_title)

        return self.remove_page_by_id(page_id)

    #### Attachments ####

    def add_attachment(self, page_id, file_path, file_content_type="Content-Type: text/plain", file_name=None):
        """ Attach the supplied file to the Confluence page specified by page_id.

         page_id -- Confluence page ID to which the file will be attached.
         file_path -- Full path to the file to be attached.
         file_name -- Desired name of the file to be attached in Confluence. If none supplied, os.path.basename is used.
         file_content_type -- MIME type of file to be attached; defaults to 'text/plain'
        """

        if file_name is None:
            file_name = os.path.basename(file_path)

        # addAttachment() takes a de minimus Attachment as a parameter, so build one.
        attachment = {
            'contentType': file_content_type,
            'fileName': file_name
        }

        with open(file_path) as attachment_file:
            attachment_file_data = base64.b64encode(attachment_file.read())

        params = [page_id, attachment, attachment_file_data]

        jsonrpc_packet = self._get_jsonrpc_packet('addAttachment', params)

        return self._confluence_post(jsonrpc_packet).result

    def remove_attachment(self, page_id, file_name):

        params = [page_id, file_name]

        jsonrpc_packet = self._get_jsonrpc_packet('removeAttachment', params)

        return self._confluence_post(jsonrpc_packet).result

    def get_attachment_info(self, page_id, file_name, version_number=0):

        params = [page_id, file_name, version_number]

        jsonrpc_packet = self._get_jsonrpc_packet('getAttachment', params)

        return self._confluence_post(jsonrpc_packet).result

    def get_attachment_data(self, page_id, file_name, version_number=0):

        params = [page_id, file_name, version_number]
        jsonrpc_packet = self._get_jsonrpc_packet('getAttachmentData', params)

        return self._confluence_post(jsonrpc_packet).result

    def save_attachment_data(self, file_path, page_id, file_name, version_number=0):

        file_data = self.get_attachment_data(page_id, file_name, version_number)
        with open(file_path, 'w+b') as attachment_file:
            attachment_file.write(base64.b64decode(file_data))

    #### Descendents ###

    def get_page_children(self, page_id):

        jsonrpc_packet = self._get_jsonrpc_packet('getChildren', [page_id])

        return self._confluence_post(jsonrpc_packet).result

    def get_page_descendants(self, page_id):

        jsonrpc_packet = self._get_jsonrpc_packet('getDescendents', [page_id])

        return self._confluence_post(jsonrpc_packet).result


class ConfluenceResponse(object):
    """Wrapper for the requests package HTTP response object, with logic for handling returned JSON RPC responses."""

    def __init__(self, obj):
        self._wrapped_obj = obj

        json_rpc_response = self.json()

        if 'error' in json_rpc_response:
            raise ConfluenceException("JSON RPC error: %s, %s"
                                      % (json_rpc_response['error']['code'],
                                         json_rpc_response['error']['message']))

        self.id = json_rpc_response['id']
        self.result = json_rpc_response['result']

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._wrapped_obj, attr)

    def __repr__(self):
        # Add Confluence-specific information to representation.
        # TODO Add some JSON info
        return "ConfluenceResponse: %s/%s (%s)" % (self.status_code, self.reason, self.url)


class ConfluenceException(Exception):
    """Provide a ConfluenceException we can raise when the API returns status_codes indicating an error state."""

    pass

