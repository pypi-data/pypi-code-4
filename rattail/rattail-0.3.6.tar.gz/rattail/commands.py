#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.commands`` -- Commands
"""

import sys
import platform

import edbob
from edbob import commands
from edbob.commands import Subcommand

import rattail


class Command(commands.Command):
    """
    The primary command for Rattail.
    """
    
    name = 'rattail'
    version = rattail.__version__
    description = "Retail Software Framework"
    long_description = """
Rattail is a retail software framework.

Copyright (c) 2010-2012 Lance Edgar <lance@edbob.org>

This program comes with ABSOLUTELY NO WARRANTY.  This is free software,
and you are welcome to redistribute it under certain conditions.
See the file COPYING.txt for more information.
"""


class AddUser(Subcommand):
    """
    Adds a user to the database.
    """

    name = 'adduser'
    description = "Add a user to the database."

    def add_parser_args(self, parser):
        parser.add_argument('url', metavar='URL',
                            help="Database engine URL")
        parser.add_argument('username',
                            help="Username for the new account.")
        parser.add_argument('-A', '--administrator',
                            action='store_true',
                            help="Add the new user to the Administrator role.")

    def run(self, args):
        from sqlalchemy import create_engine
        from .db import Session
        from .db.model import User
        from getpass import getpass
        from .db.auth import set_user_password, administrator_role

        engine = create_engine(args.url)
        session = Session(bind=engine)
        if session.query(User).filter_by(username=args.username).count():
            session.close()
            print("User '{0}' already exists.".format(args.username))
            return

        passwd = ''
        while not passwd:
            try:
                passwd = getpass("Enter a password for user '{0}': ".format(args.username))
            except KeyboardInterrupt:
                print("\nOperation was canceled.")
                return

        user = User(username=args.username)
        set_user_password(user, passwd)
        if args.administrator:
            user.roles.append(administrator_role(session))
        session.add(user)
        session.commit()
        session.close()
        print("Created user: {0}".format(args.username))


class DatabaseSyncCommand(Subcommand):
    """
    Controls the database synchronization service.
    """

    name = 'dbsync'
    description = "Manage the database synchronization service"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform == 'linux2':
            parser.add_argument('-p', '--pidfile',
                                help="Path to PID file", metavar='PATH')
            parser.add_argument('-D', '--do-not-daemonize',
                                action='store_true',
                                help="Do not daemonize when starting.")

    def run(self, args):
        from rattail.db.sync import linux as dbsync

        if args.subcommand == 'start':
            dbsync.start_daemon(args.pidfile, not args.do_not_daemonize)

        elif args.subcommand == 'stop':
            dbsync.stop_daemon(args.pidfile)


class Dump(Subcommand):
    """
    Do a simple data dump.
    """

    name = 'dump'
    description = "Dump data to file."

    def add_parser_args(self, parser):
        parser.add_argument(
            '--output', '-o', metavar='FILE',
            help="Optional path to output file.  If none is specified, "
            "data will be written to standard output.")
        parser.add_argument(
            'model', help="Model whose data will be dumped.")

    def run(self, args):
        from .db import Session
        from .db.dump import dump_data
        from .console import Progress

        if hasattr(edbob, args.model):
            model = getattr(edbob, args.model)
        else:
            sys.stderr.write("Unknown model: {0}\n".format(args.model))
            sys.exit(1)

        progress = None
        if self.show_progress:
            progress = Progress

        if args.output:
            output = open(args.output, 'wb')
        else:
            output = sys.stdout

        session = Session()
        dump_data(session, model, output, progress=progress)
        session.close()

        if output is not sys.stdout:
            output.close()


class FileMonitorCommand(Subcommand):
    """
    Interacts with the file monitor service; called as ``rattail filemon``.
    This command expects a subcommand; one of the following:

    * ``rattail filemon start``
    * ``rattail filemon stop``

    On Windows platforms, the following additional subcommands are available:

    * ``rattail filemon install``
    * ``rattail filemon uninstall`` (or ``rattail filemon remove``)

    .. note::
       The Windows Vista family of operating systems requires you to launch
       ``cmd.exe`` as an Administrator in order to have sufficient rights to
       run the above commands.

    .. See :doc:`howto.use_filemon` for more information.
    """

    name = 'filemon'
    description = "Manage the file monitor service"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        start = subparsers.add_parser('start', help="Start service")
        start.set_defaults(subcommand='start')
        stop = subparsers.add_parser('stop', help="Stop service")
        stop.set_defaults(subcommand='stop')

        if sys.platform == 'linux2':
            parser.add_argument('-p', '--pidfile',
                                help="Path to PID file.", metavar='PATH')
            parser.add_argument('-D', '--do-not-daemonize',
                                action='store_true',
                                help="Do not daemonize when starting.")

        elif sys.platform == 'win32':
            install = subparsers.add_parser('install', help="Install service")
            install.set_defaults(subcommand='install')
            install.add_argument('-a', '--auto-start', action='store_true',
                                 help="Configure service to start automatically")
            remove = subparsers.add_parser('remove', help="Uninstall (remove) service")
            remove.set_defaults(subcommand='remove')
            uninstall = subparsers.add_parser('uninstall', help="Uninstall (remove) service")
            uninstall.set_defaults(subcommand='remove')

    def run(self, args):
        if sys.platform == 'linux2':
            from rattail.filemon import linux as filemon

            if args.subcommand == 'start':
                filemon.start_daemon(args.pidfile, not args.do_not_daemonize)

            elif args.subcommand == 'stop':
                filemon.stop_daemon(args.pidfile)

        elif sys.platform == 'win32':
            from edbob import win32
            from rattail.filemon import win32 as filemon
            from rattail.win32 import require_elevation

            require_elevation()

            # Execute typical service command.
            options = []
            if args.subcommand == 'install' and args.auto_start:
                options = ['--startup', 'auto']
            win32.execute_service_command(filemon, args.subcommand, *options)

            # If installing auto-start service on Windows 7, we should update
            # its startup type to be "Automatic (Delayed Start)".
            # TODO: Improve this check to include Vista?
            if args.subcommand == 'install' and args.auto_start:
                if platform.release() == '7':
                    name = filemon.RattailFileMonitor._svc_name_
                    win32.delayed_auto_start_service(name)

        else:
            sys.stderr.write("File monitor is not supported on platform: {0}\n".format(sys.platform))
            sys.exit(1)


class InitializeDatabase(Subcommand):
    """
    Creates the initial Rattail tables within a database.
    """

    name = 'initdb'
    description = "Create initial tables in a database."

    def add_parser_args(self, parser):
        parser.add_argument('url', metavar='URL',
                            help="Database engine URL")

    def run(self, args):
        from sqlalchemy import create_engine
        from .db.model import Base
        from alembic.util import obfuscate_url_pw
        
        engine = create_engine(args.url)
        Base.metadata.create_all(engine)
        print("Created initial tables for database:")
        print("  {0}".format(obfuscate_url_pw(engine.url)))


class LoadHostDataCommand(Subcommand):
    """
    Loads data from the Rattail host database, if one is configured.
    """

    name = 'load-host-data'
    description = "Load data from host database"

    def run(self, args):
        from edbob.console import Progress
        from rattail.db import load

        edbob.init_modules(['edbob.db'])

        if 'host' not in edbob.engines:
            print "Host engine URL not configured."
            return

        proc = load.LoadProcessor()
        proc.load_all_data(edbob.engines['host'], Progress)


class MakeConfigCommand(Subcommand):
    """
    Creates a sample configuration file.
    """

    name = 'make-config'
    description = "Create a configuration file"

    def add_parser_args(self, parser):
        parser.add_argument('path', default='rattail.conf', metavar='PATH',
                            help="Path to the new file")
        parser.add_argument('-f', '--force', action='store_true',
                            help="Overwrite an existing file")


    def run(self, args):
        import os
        import os.path
        import shutil
        from rattail.files import resource_path

        dest = os.path.abspath(args.path)
        if os.path.exists(dest):
            if os.path.isdir(dest):
                sys.stderr.write("Path must include the filename; "
                                 "you gave a directory:\n  {0}\n".format(dest))
                sys.exit(1)
            if not args.force:
                sys.stderr.write("File already exists "
                                 "(use --force to overwrite):\n  "
                                 "{0}\n".format(dest))
                sys.exit(1)
            os.remove(dest)

        src = resource_path('rattail:data/rattail.conf.sample')
        shutil.copyfile(src, dest)


class MakeUserCommand(Subcommand):
    """
    Creates a system user for Rattail.
    """

    name = 'make-user'
    description = "Create a system user account for Rattail"

    def run(self, args):
        from getpass import getpass
        from rattail.win32 import users

        if users.user_exists('rattail'):
            sys.stderr.write("User already exists: rattail\n")
            sys.exit(1)

        try:
            password = None
            while not password:
                password = getpass("Enter a password: ").strip()
        except KeyboardInterrupt:
            sys.stderr.write("Operation canceled by user.")
            sys.exit(2)

        users.create_rattail_user(password)
        sys.stdout.write("Created user: rattail\n")


class PalmCommand(Subcommand):
    """
    Manages registration for the HotSync Manager conduit; called as::

       rattail palm
    """

    name = 'palm'
    description = "Manage the HotSync Manager conduit registration"

    def add_parser_args(self, parser):
        subparsers = parser.add_subparsers(title='subcommands')

        register = subparsers.add_parser('register', help="Register Rattail conduit")
        register.set_defaults(subcommand='register')

        unregister = subparsers.add_parser('unregister', help="Unregister Rattail conduit")
        unregister.set_defaults(subcommand='unregister')

    def run(self, args):
        from rattail import palm
        from rattail.win32 import require_elevation
        from rattail.exceptions import PalmError

        require_elevation()

        if args.subcommand == 'register':
            try:
                palm.register_conduit()
            except PalmError, error:
                sys.stderr.write(str(error) + '\n')

        elif args.subcommand == 'unregister':
            try:
                palm.unregister_conduit()
            except PalmError, error:
                sys.stderr.write(str(error) + '\n')
                

class PurgeBatchesCommand(Subcommand):
    """
    .. highlight:: sh

    Purges stale batches from the database; called as::

      rattail purge-batches
    """

    name = 'purge-batches'
    description = "Purge stale batches from the database"

    def add_parser_args(self, parser):
        parser.add_argument('-A', '--all', action='store_true',
                            help="Purge ALL batches regardless of purge date")

    def run(self, args):
        from rattail.db.batches.util import purge_batches

        edbob.init_modules(['edbob.db', 'rattail.db'])

        print "Purging batches from database:"
        print "    %s" % edbob.engine.url

        session = edbob.Session()
        purged = purge_batches(session, purge_everything=args.all)
        session.commit()
        session.close()

        print "\nPurged %d batches" % purged


def main(*args):
    """
    The primary entry point for the Rattail command system.
    """

    if args:
        args = list(args)
    else:
        args = sys.argv[1:]

    cmd = Command()
    cmd.run(*args)
