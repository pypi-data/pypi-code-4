#!/usr/bin/env python
# coding=utf-8

"""the cloudns cli REPL. see also the main module.

"""

import sys
import cmd
import shlex

from cloudns.zone import Zone
from cloudns.cli_utils import out, err
from cloudns.cli_logic import run_search, run_create, run_delete


class CloudnsREPL(cmd.Cmd):
    prompt = u'cloudns> '
    intro = u"""\
This is Cloudns REPL, an interactive shell for using cloudns.
Type help or ? for usage
"""
    def preloop(self):
        """this is like an init function in normal class.

        """
        for field in ('passport', 'token', 'zone'):
            if not hasattr(self, field):
                setattr(self, field, None)

        # cached_zones is a dict that cache cloudns.Zone objects.
        # the key is (passport, token, zone), value is a Zone object.
        self._cached_zones = {}

    def postcmd(self, stop, line):
        if stop:
            sys.exit(0)
        else:
            out(u"\n")

    def get_zone(self):
        """return a Zone object for current session.

        return None if authentication not set or zone not set.

        """
        if self.passport and self.token and self.zone:
            key = (self.passport, self.token, self.zone)
            if key not in self._cached_zones:
                self._cached_zones[key] = Zone.create_zone(
                    self.passport, self.token, self.zone)
            return self._cached_zones[key]
        else:
            out(u"Error: You need to set passport, token and zone first.\n\
run `info' to show what is missing.")

    # =====================================================================
    #  about do_* callback method.
    #    * to support command `foo', you should define `do_foo' method
    #    * it accepts one param, which is the line after the command
    #    * it should return True if REPL should stop after that command
    # =====================================================================

    def do_exit(self, _):
        """exit repl"""
        return True

    def do_quit(self, _):
        """quit repl"""
        return True

    def do_EOF(self, _):  # pylint: disable=C0103
        out(u"exit\n")
        return True

    def do_clear_cache(self, _):
        """clear Zone object cache.

        This is designed for long running daemons. Interactively, you rarely
        need to run this.

        """
        self._cached_zones.clear()
        out(u"cache cleared\n")

    def do_set_passport(self, line):
        """set passport"""
        self.passport = line
        out(u"passport set to %s\n", line)

    def do_set_token(self, line):
        """set token"""
        self.token = line
        out(u"token set to %s\n", line)

    def do_set_zone(self, line):
        """set current zone

        Usage: set_zone zone

        """
        self.zone = line
        out(u"current zone set to %s\n", line)

    def do_info(self, _):
        """show session info"""
        def v(value, hide_value=False):  # pylint: disable=C0103
            """format a value for print.

            if a value is None, show "<not set>" instead.
            otherwise, show value as a string.

            if hide_value is True, if value is not None, show "<set>".

            """
            if value:
                if hide_value:
                    return u"<set>"
                else:
                    return value
            else:
                return u"<not set>"

        out(u"""\
current session info:
=======================
passport: %s
token: %s
current zone: %s\n""",
            v(self.passport), v(self.token, hide_value=True), v(self.zone))

    def do_create(self, line):
        """create a record in current zone.

        Usage: create label value (tel|uni) [type [ttl]]

        you can set current zone using `set_zone' command.
        """
        zone = self.get_zone()
        if not zone:
            return
        try:
            run_create(zone, shlex.split(line))
        except SystemExit:
            pass

    def do_search(self, line):
        """search records by keyword."""
        zone = self.get_zone()
        if not zone:
            return
        try:
            run_search(zone, shlex.split(line))
        except SystemExit:
            pass

    def do_delete(self, line):
        """delete records by name."""
        zone = self.get_zone()
        if not zone:
            return
        try:
            run_delete(zone, shlex.split(line))
        except SystemExit:
            pass
