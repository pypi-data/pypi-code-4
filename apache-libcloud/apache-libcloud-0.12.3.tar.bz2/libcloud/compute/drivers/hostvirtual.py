# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
libcloud driver for the Host Virtual Inc. (VR) API
Home page http://www.vr.org/
"""

try:
    import simplejson as json
except ImportError:
    import json


from libcloud.utils.py3 import httplib

from libcloud.common.hostvirtual import HostVirtualResponse
from libcloud.common.hostvirtual import HostVirtualConnection
from libcloud.common.hostvirtual import HostVirtualException
from libcloud.compute.providers import Provider
from libcloud.compute.types import NodeState
from libcloud.compute.base import Node, NodeDriver
from libcloud.compute.base import NodeImage, NodeSize, NodeLocation
from libcloud.compute.base import NodeAuthSSHKey, NodeAuthPassword

API_ROOT = '/vapi'

#API_VERSION = '0.1'
NODE_STATE_MAP = {
    'BUILDING': NodeState.PENDING,
    'PENDING': NodeState.PENDING,
    'RUNNING': NodeState.RUNNING,  # server is powered up
    'STOPPING': NodeState.REBOOTING,
    'REBOOTING': NodeState.REBOOTING,
    'STARTING': NodeState.REBOOTING,
    'TERMINATED': NodeState.TERMINATED  # server is powered down
}


class HostVirtualComputeResponse(HostVirtualResponse):
    pass


class HostVirtualComputeConnection(HostVirtualConnection):
    responseCls = HostVirtualComputeResponse


class HostVirtualNodeDriver(NodeDriver):
    type = Provider.HOSTVIRTUAL
    name = 'HostVirtual'
    website = 'http://www.vr.org'
    connectionCls = HostVirtualComputeConnection

    def __init__(self, key):
        self.location = None
        NodeDriver.__init__(self, key)

    def _to_node(self, data):
        state = NODE_STATE_MAP[data['status']]
        public_ips = []
        private_ips = []
        extra = {}

        if 'plan_id' in data:
            extra['size'] = data['plan_id']
        if 'os_id' in data:
            extra['image'] = data['os_id']
        if 'location_id' in data:
            extra['location'] = data['location_id']

        public_ips.append(data['ip'])

        node = Node(id=data['mbpkgid'], name=data['fqdn'], state=state,
                    public_ips=public_ips, private_ips=private_ips,
                    driver=self.connection.driver, extra=extra)
        return node

    def list_locations(self):
        result = self.connection.request(API_ROOT + '/cloud/locations/').object
        locations = []
        for dc in result:
            locations.append(NodeLocation(
                dc["id"],
                dc["name"],
                dc["name"].split(',')[1].replace(" ", ""),  # country
                self))
        return locations

    def list_sizes(self, location=None):
        params = {}
        if location:
            params = {'location': location.id}
        result = self.connection.request(
            API_ROOT + '/cloud/sizes/',
            data=json.dumps(params)).object
        sizes = []
        for size in result:
            n = NodeSize(id=size['plan_id'],
                         name=size['plan'],
                         ram=size['ram'],
                         disk=size['disk'],
                         bandwidth=size['transfer'],
                         price=size['price'],
                         driver=self.connection.driver)
            sizes.append(n)
        return sizes

    def list_images(self):
        result = self.connection.request(API_ROOT + '/cloud/images/').object
        images = []
        for image in result:
            i = NodeImage(id=image["id"],
                          name=image["os"],
                          driver=self.connection.driver,
                          extra=image)
            del i.extra['id']
            del i.extra['os']
            images.append(i)
        return images

    def list_nodes(self):
        result = self.connection.request(API_ROOT + '/cloud/servers/').object
        nodes = []
        for value in result:
            node = self._to_node(value)
            nodes.append(node)
        return nodes

    def create_node(self, **kwargs):
        name = kwargs['name']  # expects fqdn ex: test.com
        size = kwargs['size']
        image = kwargs['image']
        auth = kwargs['auth']
        dc = None

        if "location" in kwargs:
            dc = kwargs["location"].id
        else:
            dc = '3'

        params = {'fqdn': name,
                  'plan': size.name,
                  'image': image.id,
                  'location': dc
                  }

        ssh_key = None
        password = None
        if isinstance(auth, NodeAuthSSHKey):
            ssh_key = auth.pubkey
            params['ssh_key'] = ssh_key
        elif isinstance(auth, NodeAuthPassword):
            password = auth.password
            params['password'] = password

        if not ssh_key and not password:
            raise HostVirtualException(500, "Need SSH key or Root password")

        result = self.connection.request(API_ROOT + '/cloud/buy_build',
                                         data=json.dumps(params),
                                         method='POST').object
        return self._to_node(result)

    def reboot_node(self, node):
        params = {'force': 0, 'mbpkgid': node.id}
        result = self.connection.request(
            API_ROOT + '/cloud/server/reboot',
            data=json.dumps(params),
            method='POST').object

        return bool(result)

    def destroy_node(self, node):
        params = {'mbpkgid': node.id}
        result = self.connection.request(
            API_ROOT + '/cloud/cancel', data=json.dumps(params),
            method='POST').object

        return bool(result)

    def ex_get_node(self, node_id):
        """
        Get a single node.

        @param      node_id: id of the node that we need the node object for
        @type       node_id: C{str}

        @rtype: L{Node}
        """

        params = {'mbpkgid': node_id}
        result = self.connection.request(
            API_ROOT + '/cloud/server', params=params).object
        node = self._to_node(result)
        return node

    def ex_stop_node(self, node):
        """
        Stop a node.

        @param      node: Node which should be used
        @type       node: L{Node}

        @rtype: C{bool}
        """
        params = {'force': 0, 'mbpkgid': node.id}
        result = self.connection.request(
            API_ROOT + '/cloud/server/stop',
            data=json.dumps(params),
            method='POST').object

        return bool(result)

    def ex_start_node(self, node):
        """
        Start a node.

        @param      node: Node which should be used
        @type       node: L{Node}

        @rtype: C{bool}
        """
        params = {'mbpkgid': node.id}
        result = self.connection.request(
            API_ROOT + '/cloud/server/start',
            data=json.dumps(params),
            method='POST').object

        return bool(result)

    def ex_build_node(self, **kwargs):
        """
        Build a server on a VR package and get it booted

        @keyword node: node which should be used
        @type    node: L{Node}

        @keyword image: The distribution to deploy on your server (mandatory)
        @type    image: L{NodeImage}

        @keyword auth: an SSH key or root password (mandatory)
        @type    auth: L{NodeAuthSSHKey} or L{NodeAuthPassword}

        @keyword location: which datacenter to create the server in
        @type    location: L{NodeLocation}

        @rtype: C{bool}
        """

        node = kwargs['node']

        if 'image' in kwargs:
            image = kwargs['image']
        else:
            image = node.extra['image']

        params = {
            'mbpkgid': node.id,
            'image': image,
            'fqdn': node.name,
            'location': node.extra['location'],
        }

        auth = kwargs['auth']

        ssh_key = None
        password = None
        if isinstance(auth, NodeAuthSSHKey):
            ssh_key = auth.pubkey
            params['ssh_key'] = ssh_key
        elif isinstance(auth, NodeAuthPassword):
            password = auth.password
            params['password'] = password

        if not ssh_key and not password:
            raise HostVirtualException(500, "Need SSH key or Root password")

        result = self.connection.request(API_ROOT + '/cloud/server/build',
                                         data=json.dumps(params),
                                         method='POST').object
        return bool(result)

    def ex_delete_node(self, node):
        """
        Delete a node.

        @param      node: Node which should be used
        @type       node: L{Node}

        @rtype: C{bool}
        """

        params = {'mbpkgid': node.id}
        result = self.connection.request(
            API_ROOT + '/cloud/server/delete', data=json.dumps(params),
            method='POST').object

        return bool(result)
