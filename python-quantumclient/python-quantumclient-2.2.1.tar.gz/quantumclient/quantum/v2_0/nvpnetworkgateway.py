# Copyright 2013 OpenStack LLC.
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

import argparse
import logging

from quantumclient.common import utils
from quantumclient.quantum import v2_0 as quantumv20

RESOURCE = 'network_gateway'


class ListNetworkGateway(quantumv20.ListCommand):
    """List network gateways for a given tenant."""

    resource = RESOURCE
    _formatters = {}
    log = logging.getLogger(__name__ + '.ListNetworkGateway')
    list_columns = ['id', 'name']


class ShowNetworkGateway(quantumv20.ShowCommand):
    """Show information of a given network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.ShowNetworkGateway')


class CreateNetworkGateway(quantumv20.CreateCommand):
    """Create a network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.CreateNetworkGateway')

    def add_known_arguments(self, parser):
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of network gateway to create')
        parser.add_argument(
            '--device',
            action='append',
            help='device info for this gateway '
            'device_id=<device identifier>,'
            'interface_name=<name_or_identifier> '
            'It can be repeated for multiple devices for HA gateways')

    def args2body(self, parsed_args):
        body = {self.resource: {
            'name': parsed_args.name}}
        devices = []
        if parsed_args.device:
            for device in parsed_args.device:
                devices.append(utils.str2dict(device))
        if devices:
            body[self.resource].update({'devices': devices})
        if parsed_args.tenant_id:
            body[self.resource].update({'tenant_id': parsed_args.tenant_id})
        return body


class DeleteNetworkGateway(quantumv20.DeleteCommand):
    """Delete a given network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.DeleteNetworkGateway')


class UpdateNetworkGateway(quantumv20.UpdateCommand):
    """Update the name for a network gateway."""

    resource = RESOURCE
    log = logging.getLogger(__name__ + '.UpdateNetworkGateway')


class NetworkGatewayInterfaceCommand(quantumv20.QuantumCommand):
    """Base class for connecting/disconnecting networks to/from a gateway."""

    resource = RESOURCE

    def get_parser(self, prog_name):
        parser = super(NetworkGatewayInterfaceCommand,
                       self).get_parser(prog_name)
        parser.add_argument(
            'net_gateway_id', metavar='NET-GATEWAY-ID',
            help='ID of the network gateway')
        parser.add_argument(
            'network_id', metavar='NETWORK-ID',
            help='ID of the internal network to connect on the gateway')
        parser.add_argument(
            '--segmentation-type',
            help=('L2 segmentation strategy on the external side of '
                  'the gateway (e.g.: VLAN, FLAT)'))
        parser.add_argument(
            '--segmentation-id',
            help=('Identifier for the L2 segment on the external side '
                  'of the gateway'))
        return parser

    def retrieve_ids(self, client, args):
        gateway_id = quantumv20.find_resourceid_by_name_or_id(
            client, self.resource, args.net_gateway_id)
        network_id = quantumv20.find_resourceid_by_name_or_id(
            client, 'network', args.network_id)
        return (gateway_id, network_id)


class ConnectNetworkGateway(NetworkGatewayInterfaceCommand):
    """Add an internal network interface to a router."""

    log = logging.getLogger(__name__ + '.ConnectNetworkGateway')

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        (gateway_id, network_id) = self.retrieve_ids(quantum_client,
                                                     parsed_args)
        quantum_client.connect_network_gateway(
            gateway_id, {'network_id': network_id,
                         'segmentation_type': parsed_args.segmentation_type,
                         'segmentation_id': parsed_args.segmentation_id})
        # TODO(Salvatore-Orlando): Do output formatting as
        # any other command
        print >>self.app.stdout, (
            _('Connected network to gateway %s') % gateway_id)


class DisconnectNetworkGateway(NetworkGatewayInterfaceCommand):
    """Remove a network from a network gateway."""

    log = logging.getLogger(__name__ + '.DisconnectNetworkGateway')

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        quantum_client = self.get_client()
        quantum_client.format = parsed_args.request_format
        (gateway_id, network_id) = self.retrieve_ids(quantum_client,
                                                     parsed_args)
        quantum_client.disconnect_network_gateway(
            gateway_id, {'network_id': network_id,
                         'segmentation_type': parsed_args.segmentation_type,
                         'segmentation_id': parsed_args.segmentation_id})
        # TODO(Salvatore-Orlando): Do output formatting as
        # any other command
        print >>self.app.stdout, (
            _('Disconnected network from gateway %s') % gateway_id)
