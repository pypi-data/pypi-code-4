# Copyright 2012 Nicira, Inc
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import sys

from quantumclient.common import exceptions
from quantumclient.quantum.v2_0 import nvpnetworkgateway
from quantumclient.tests.unit.test_cli20 import CLITestV20Base
from quantumclient.tests.unit.test_cli20 import MyApp


class CLITestV20NetworkGateway(CLITestV20Base):

    resource = "network_gateway"

    def test_create_gateway(self):
        cmd = nvpnetworkgateway.CreateNetworkGateway(MyApp(sys.stdout), None)
        name = 'gw-test'
        myid = 'myid'
        args = [name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(self.resource, cmd, name, myid, args,
                                          position_names, position_values)

    def test_create_gateway_with_tenant(self):
        cmd = nvpnetworkgateway.CreateNetworkGateway(MyApp(sys.stdout), None)
        name = 'gw-test'
        myid = 'myid'
        args = ['--tenant_id', 'tenantid', name]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(self.resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          tenant_id='tenantid')

    def test_create_gateway_with_device(self):
        cmd = nvpnetworkgateway.CreateNetworkGateway(MyApp(sys.stdout), None)
        name = 'gw-test'
        myid = 'myid'
        args = ['--device', 'device_id=test', name, ]
        position_names = ['name', ]
        position_values = [name, ]
        _str = self._test_create_resource(self.resource, cmd, name, myid, args,
                                          position_names, position_values,
                                          devices=[{'device_id': 'test'}])

    def test_list_gateways(self):
        resources = '%ss' % self.resource
        cmd = nvpnetworkgateway.ListNetworkGateway(MyApp(sys.stdout), None)
        self._test_list_resources(resources, cmd, True)

    def test_update_gateway(self):
        cmd = nvpnetworkgateway.UpdateNetworkGateway(MyApp(sys.stdout), None)
        self._test_update_resource(self.resource, cmd, 'myid',
                                   ['myid', '--name', 'cavani'],
                                   {'name': 'cavani'})

    def test_delete_gateway(self):
        cmd = nvpnetworkgateway.DeleteNetworkGateway(MyApp(sys.stdout), None)
        myid = 'myid'
        args = [myid]
        self._test_delete_resource(self.resource, cmd, myid, args)

    def test_show_gateway(self):
        cmd = nvpnetworkgateway.ShowNetworkGateway(MyApp(sys.stdout), None)
        args = ['--fields', 'id', '--fields', 'name', self.test_id]
        self._test_show_resource(self.resource, cmd, self.test_id, args,
                                 ['id', 'name'])

    def test_connect_network_to_gateway(self):
        cmd = nvpnetworkgateway.ConnectNetworkGateway(MyApp(sys.stdout), None)
        args = ['gw_id', 'net_id',
                '--segmentation-type', 'edi',
                '--segmentation-id', '7']
        self._test_update_resource_action(self.resource, cmd, 'gw_id',
                                          'connect_network',
                                          args,
                                          {'network_id': 'net_id',
                                           'segmentation_type': 'edi',
                                           'segmentation_id': '7'})

    def test_disconnect_network_from_gateway(self):
        cmd = nvpnetworkgateway.DisconnectNetworkGateway(MyApp(sys.stdout),
                                                         None)
        args = ['gw_id', 'net_id',
                '--segmentation-type', 'edi',
                '--segmentation-id', '7']
        self._test_update_resource_action(self.resource, cmd, 'gw_id',
                                          'disconnect_network',
                                          args,
                                          {'network_id': 'net_id',
                                           'segmentation_type': 'edi',
                                           'segmentation_id': '7'})
