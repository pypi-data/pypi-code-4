# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from heat.engine import scheduler
from heat.engine.resources import nova_utils
import heat.engine.resources.instance

from heat.common import exception

from heat.openstack.common.gettextutils import _
from heat.openstack.common import log as logging

from novaclient.exceptions import NotFound as ServerNotFound

logger = logging.getLogger(__name__)


class Instance(heat.engine.resources.instance.Instance):
    tags_schema = {'Key': {'Type': 'String',
                           'Required': True},
                   'Value': {'Type': 'String',
                             'Required': True}}

    properties_schema = {'ImageId': {'Type': 'String',
                                     'Required': True},
                         'GuestParams': {'Type': 'List',
                                         'Schema': {'Type': 'Map',
                                                    'Schema': tags_schema}},
                         'KeyName': {'Type': 'String'},
                         'AvailabilityZone': {'Type': 'String'},
                         'DisableApiTermination': {'Type': 'String',
                                                   'Implemented': False},
                         'KernelId': {'Type': 'String',
                                      'Implemented': False},
                         'Monitoring': {'Type': 'Boolean',
                                        'Implemented': False},
                         'PlacementGroupName': {'Type': 'String',
                                                'Implemented': False},
                         'PrivateIpAddress': {'Type': 'String',
                                              'Implemented': False},
                         'RamDiskId': {'Type': 'String',
                                       'Implemented': False},
                         'SecurityGroups': {'Type': 'List'},
                         'SecurityGroupIds': {'Type': 'List'},
                         'SourceDestCheck': {'Type': 'Boolean',
                                             'Implemented': False},
                         'NovaSchedulerHints': {'Type': 'List',
                                                'Schema': {
                                                    'Type': 'Map',
                                                    'Schema': tags_schema
                                                }},
                         'Tenancy': {'Type': 'String',
                                     'AllowedValues': ['dedicated', 'default'],
                                     'Implemented': False},
                         'UserData': {'Type': 'String'}}

    attributes_schema = {'AvailabilityZone': ('The Availability Zone where the'
                                              ' specified instance is '
                                              'launched.'),
                         'PrivateDnsName': ('Private DNS name of the specified'
                                            ' instance.'),
                         'PublicDnsName': ('Public DNS name of the specified '
                                           'instance.'),
                         'PrivateIp': ('Private IP address of the specified '
                                       'instance.'),
                         'PublicIp': ('Public IP address of the specified '
                                      'instance.')}

    update_allowed_keys = ('Metadata', 'Properties')
    update_allowed_properties = None

    def __init__(self, name, json_snippet, stack):
        super(Instance, self).__init__(name, json_snippet, stack)

    def _lookup_live_image(self, name):
        # First, try looking up by ID
        try:
            return self.nova().cobalt.get(name)
        except ServerNotFound:
            pass

        # Next, try looking up by name
        servers = self.nova().cobalt.list(search_opts={ "name" : name})
        for server in servers:
            if server.name == name and server.status == 'BLESSED':
                return server

        return None

    def handle_create(self):
        security_groups = self._get_security_groups()

        userdata = self.properties['UserData'] or ''
        availability_zone = self.properties['AvailabilityZone']

        key_name = self.properties['KeyName']
        if key_name:
            # confirm keypair exists
            nova_utils.get_keypair(self.nova(), key_name)

        image_name = self.properties['ImageId']

        live_image = self._lookup_live_image(image_name)

        guest_params = {}
        if self.properties['GuestParams']:
            for tm in self.properties['GuestParams']:
                guest_params[tm['Key']] = tm['Value']
        else:
            guest_params = None

        scheduler_hints = {}
        if self.properties['NovaSchedulerHints']:
            for tm in self.properties['NovaSchedulerHints']:
                scheduler_hints[tm['Key']] = tm['Value']
        else:
            scheduler_hints = None

        server = None
        try:
            server = live_image.start_live_image(
                name=self.physical_resource_name(),
                guest_params=guest_params,
                key_name=key_name,
                security_groups=security_groups,
                user_data=self.get_mime_string(userdata),
                availability_zone=availability_zone,
                scheduler_hints=scheduler_hints)[0]
        finally:
            # Avoid a race condition where the thread could be cancelled
            # before the ID is stored
            if server is not None:
                self.resource_id_set(server.id)

        return server

    def check_create_complete(self, cookie):
        server = cookie

        # Reload server status
        if server.status != 'ACTIVE':
            server.get()

        # Some clouds append extra (STATUS) strings to the status
        short_server_status = server.status.split('(')[0]
        if short_server_status in nova_utils.deferred_server_statuses:
            return False
        elif server.status == 'ACTIVE':
            self._set_ipaddress(server.networks)
            return True
        elif server.status == 'ERROR':
            fault = server.fault or {}
            message = fault.get('message', 'Unknown')
            code = fault.get('code', 500)
            delete = scheduler.TaskRunner(
                nova_utils.delete_server, server)
            delete(wait_time=0.2)
            exc = exception.Error(_("Build of server %(server)s failed: "
                                    "%(message)s (%(code)s)") %
                                  dict(server=server.name,
                                       message=message,
                                       code=code))
            raise exc
        else:
            exc = exception.Error(_('Nova reported unexpected '
                                    'instance[%(name)s] '
                                    'status[%(status)s]') %
                                  dict(name=self.name,
                                       status=server.status))
            raise exc

    def handle_update(self, json_snippet, tmpl_diff, prop_diff):
        if 'Metadata' in tmpl_diff:
            self.metadata = tmpl_diff['Metadata']

    def validate(self):
        '''
        Validate any of the provided params
        '''
        # check validity of key
        key_name = self.properties.get('KeyName', None)
        if key_name:
            nova_utils.get_keypair(self.nova(), key_name)

        # make sure the image exists.
        image_name = self.properties['ImageId']
        live_image = self._lookup_live_image(image_name)
        if not live_image:
            return "Live-Image not found: %s" % image_name

    def _detach_volumes_task(self):
        '''
        No-op task, needed to use superclass implementations
        of handle_delete and handle_suspend.
        '''
        return scheduler.PollingTaskGroup([])

def resource_mapping():
    return {
        'OS::Cobalt::Instance': Instance,
    }
