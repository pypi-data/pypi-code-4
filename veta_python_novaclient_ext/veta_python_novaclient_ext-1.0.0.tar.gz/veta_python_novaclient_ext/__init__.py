# Copyright 2011 Gridcentric Inc.
# All Rights Reserved.
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

"""
An extension module for novaclient that allows the `nova` application access to
the veta backup API extensions.
"""
import json
import re

from novaclient import utils
from novaclient import base
from novaclient.v1_1 import servers

# Add new client capabilities here. Each key is a capability name and its value
# is the list of API capabilities upon which it depends.

def _find_server(cs, server):
    """ Returns a sever by name or ID. """
    return utils.find_resource(cs.veta, server)

def _print_instance_list(servers):
    columns = ['ID', 'Name', 'Status']
    sortby_index = 1
    utils.print_list(servers, columns, sortby_index=sortby_index)

def _print_backup_list(backups):
    class Backup:
        def __init__(self, id, ts, schedules):
            self.id = id
            self.timestamp = ts
            self.schedules = schedules

    columns = ['ID', 'Timestamp', 'Schedules']
    objs = map(lambda b: \
        Backup(b['uuid'], b['veta_backup_at'], b['veta_backup_ids']),
            backups)
    utils.print_list(objs, columns, sortby_index=1)

def _epoch_to_seconds(e):
    e = e.lower()
    units = { '^(\d+)w$' : (60 * 60 * 24 * 7),
              '^(\d+)d$' : (60 * 60 * 24),
              '^(\d+)h$' : (60 * 60),
              '^(\d+)m$' : (60),
              '^(\d+)s$' : 1,
              '^(\d+)$' : 1 }
    for (pattern, factor) in units.items():
        m = re.match(pattern, e)
        if m is not None:
            val = long(m.group(1))
            seconds = val * factor
            return seconds
    raise ValueError('Invalid epoch %s.' % e)

def _seconds_to_epoch(s):
    factors = [
        ((60 * 60 * 24 * 7), "week"),
        ((60 * 60 * 24), "day"),
        ((60 * 60), "hour"),
        ((60), "minute"),
        ((1), "second") # Catch-all
    ]

    for (factor, epoch) in factors:
        if s % factor == 0:
            count = s / factor
            if count > 1:
                return "%d %ss" % (count, epoch)
            else:
                return "%s" % (epoch)

def _print_backup_schedule(schedule, raw=False):
    class ScheduleRule:
        def __init__(self, id, frequency, retention, active):
            self.id = id
            self.frequency = frequency
            self.retention = retention
            self.active = active

    columns = ['ID', 'Frequency', 'Retention', 'Active']
    if raw:
        formatters = {}
    else:
        formatters = {
            'Frequency' : lambda s: "Every %s" % _seconds_to_epoch(s.frequency),
            'Retention' : lambda s: "For the last %s" % \
                                        _seconds_to_epoch(s.retention),
            'Active' : lambda s: s.active == True and "True" or "False"
        }
    objs = map(lambda r: \
        ScheduleRule(r['i'], r['f'], r['r'], r['a']),
            schedule)
    utils.print_list(objs, columns, formatters=formatters, sortby_index=None)

#### ACTIONS ####
@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('--raw', dest='raw', action='store_true', default=False,
           help='Print raw backup schedules')
def do_backup_schedule_list(cs, args):
    """List the backup schedule of this instance."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_list(server)
    _print_backup_schedule(result, args.raw)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('frequency', metavar='<frequency>',
           help="Frequency with which to perform backups (e.g. 10m, 1h, 1d")
@utils.arg('retention', metavar='<retention>',
           help="Number of backups to retain (e.g. 1h, 1d, 1w)")
def do_backup_schedule_add(cs, args):
    """Add a backup schedule rule to this instance."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_add(server,
        _epoch_to_seconds(args.frequency), _epoch_to_seconds(args.retention))
    _print_backup_schedule(result)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('schedule_id', metavar='<schedule-id>',
           help="ID of schedule item to update")
@utils.arg('frequency', metavar='<frequency>',
           help="Frequency with which to perform backups (e.g. 10m, 1h, 1d")
@utils.arg('retention', metavar='<retention>',
           help="Number of backups to retain (e.g. 1h, 1d, 1w)")
def do_backup_schedule_update(cs, args):
    """Add a backup schedule rule to this instance."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_update(server,
        args.schedule_id, _epoch_to_seconds(args.frequency),
        _epoch_to_seconds(args.retention))
    _print_backup_schedule(result)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('schedule_id', metavar='<schedule-id>',
           help="ID of schedule item to delete")
def do_backup_schedule_delete(cs, args):
    """Delete a backup schedule rule and all associated backups."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_delete(server, args.schedule_id)
    _print_backup_schedule(result)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('schedule_id', metavar='<schedule-id>',
           help="ID of schedule item to enable")
def do_backup_schedule_enable(cs, args):
    """Enable a backup schedule rule."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_enable(server, args.schedule_id)
    _print_backup_schedule(result)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('schedule_id', metavar='<schedule-id>',
           help="ID of schedule item to disable")
def do_backup_schedule_disable(cs, args):
    """Disable a backup schedule rule."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_disable(server, args.schedule_id)
    _print_backup_schedule(result)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
def do_backup_schedule_clear(cs, args):
    """Clear the backup schedule of this instance."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_clear(server)
    _print_backup_schedule(result)

@utils.arg('server', metavar='<server>', help="ID or name of the instance")
@utils.arg('--schedule-id', metavar='<schedule-id>',
           help="Filter results by a schedule ID")
def do_backup_schedule_list_backups(cs, args):
    """Display backups for this server."""
    server = _find_server(cs, args.server)
    result = cs.veta.backup_schedule_list_backups(server,
        args.schedule_id)
    _print_backup_list(result)

class VetaServer(servers.Server):
    """
    A server object extended to provide veta backup capabilities
    """
    def list_backup_schedule(self):
        return self.manager.list_backup_schedule(self)

class VetaServerManager(servers.ServerManager):
    resource_class = VetaServer

    def __init__(self, client, *args, **kwargs):
        servers.ServerManager.__init__(self, client, *args, **kwargs)

        # Make sure this instance is available as veta.
        if not(hasattr(client, 'veta')):
            setattr(client, 'veta', self)

    def backup_schedule_list(self, server):
        header, info = self._action("backup_schedule_list", base.getid(server))
        return info

    def backup_schedule_add(self, server, frequency, retention):
        params = { 'frequency' : frequency, 'retention' : retention }
        header, info = self._action("backup_schedule_add",
                                    base.getid(server), params)
        return info

    def backup_schedule_update(self, server, schedule_id, frequency,
                               retention):
        params = { 'schedule_id' : schedule_id,
                   'frequency' : frequency, 'retention' : retention }
        header, info = self._action("backup_schedule_update",
                                    base.getid(server), params)
        return info

    def backup_schedule_delete(self, server, schedule_id):
        params = { 'schedule_id' : schedule_id }
        header, info = self._action("backup_schedule_delete",
                                    base.getid(server), params)
        return info

    def backup_schedule_enable(self, server, schedule_id):
        params = { 'schedule_id' : schedule_id }
        header, info = self._action("backup_schedule_enable",
                                    base.getid(server), params)
        return info

    def backup_schedule_disable(self, server, schedule_id):
        params = { 'schedule_id' : schedule_id }
        header, info = self._action("backup_schedule_disable",
                                    base.getid(server), params)
        return info

    def backup_schedule_clear(self, server):
        header, info = self._action("backup_schedule_clear", base.getid(server))
        return info

    def backup_schedule_list_backups(self, server, schedule_id):
        if schedule_id:
            params = { 'schedule_id' : schedule_id }
        else:
            params = {}
        header, info = self._action("backup_schedule_list_backups",
                                    base.getid(server), params)
        return info
