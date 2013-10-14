#!/usr/bin/python
# Copyright 2013 Rackspace
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Created September 4, 2012

@author: Justin Hammond, Rackspace Hosting
"""

from cement.core import backend, foundation

import aiclib

INVALID_VALUE = "N/A"
defaults = backend.defaults('queries')
defaults['queries']['debug'] = False
app = foundation.CementApp('queries', config_defaults=defaults)


def invalid_switch_ports(json=False, username="admin", password="admin",
                         uri="https://nvp"):
    nvp = aiclib.nvp.Connection(uri, username=username, password=password)
    query = nvp.lswitch_port('*').query().length(1000)
    results = query.relations(['LogicalQueueConfig',
                               'LogicalSwitchConfig']).results()
    output = {} if json else ""
    msg = "Port:\t%s\nType:\t%s\nQRate:\t%s\nIP:\t%s\nMAC:\t%s\n\n"
    while results:
        if len(results['results']) == 0:
            break
        for lport in results['results']:
            logicalconfig = lport['_relations']['LogicalSwitchConfig']
            allowedaddr = lport['allowed_address_pairs']
            lport_name = lport['display_name']
            lport_type = logicalconfig['display_name']
            if not 'max_bandwidth_rate' in logicalconfig:
                lport_rate = INVALID_VALUE
            else:
                lport_rate = logicalconfig['max_bandwidth_rate']
            if len(allowedaddr) <= 0 or not 'ip_address' in allowedaddr[0]:
                lport_ipv4 = INVALID_VALUE
            else:
                lport_ipv4 = allowedaddr[0]['ip_address']
            if len(allowedaddr) <= 0 or not 'mac_address' in allowedaddr[0]:
                lport_mac = INVALID_VALUE
            else:
                lport_mac = allowedaddr[0]['mac_address']
            if lport_rate == INVALID_VALUE:
                if json:
                    if not 'results' in output:
                        output['results'] = []
                    obj = {'name': lport_name, 'type': lport_type,
                           'rate': lport_rate, 'ip': lport_ipv4,
                           'mac': lport_mac}
                    output['results'].append(obj)
                else:
                    output += msg % (lport_name, lport_type, lport_rate,
                                     lport_ipv4, lport_mac)
        results = query.next()
    print output


def main():
    try:
        app.setup()
        app.args.add_argument('-j', '--jsonformat', action="store_true",
                              help="Output in JSON format", default=False)
        app.args.add_argument('-l', '--location', action="store",
                              help="Address (URI) for NVP controller",
                              default="https://nvp")
        app.args.add_argument('-u', '--username', action="store",
                              help="Username for NVP controller",
                              default="admin")
        app.args.add_argument('-p', '--password', action="store",
                              help="Password for NVP controller",
                              default="admin")
        app.run()
        username = app.pargs.username
        password = app.pargs.password
        location = app.pargs.location
        jsonformat = app.pargs.jsonformat
        #TODO: Can't figure out why it isn't working if you double dash
        if jsonformat is None:
            jsonformat = False
        invalid_switch_ports(json=jsonformat, username=username,
                             password=password, uri=location)
    finally:
        app.close()


if __name__ == "__main__":
    main()
