# -*- coding: utf-8 -*-
# Copyright (c) 2007-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 51037 2013-08-19 10:43:19Z sylvain $

import os
import zc.buildout, zc.recipe.egg


class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.mail_dir = self.options.get('mail_dir', None)
        if not self.mail_dir:
            self.mail_dir = os.path.join(
                self.buildout['buildout']['directory'], 'var', 'maildrop',)
        self.configuration = self.options.get('maildrophost.cfg', None)
        if not self.configuration:
            self.configuration = os.path.join(
                self.buildout['buildout']['directory'], 'maildrophost.cfg')
            options['configuration'] = self.configuration
        self.pid_file = self.options.get('pid_file', None)
        if not self.pid_file:
            self.pid_file = os.path.join(self.mail_dir, 'maildrop.pid')


    def install(self):
        """Install the maildrophost server
        """
        return self.update()

    def _build_config(self):
        """Create the config file for the maildrop server ; Create
        directory used by the maildrop server.
        """

        if not os.path.exists(self.mail_dir):
            os.makedirs(self.mail_dir)

        spool_dir = self.options.get(
            'spool_dir', None) or os.path.join(self.mail_dir, 'spool')
        if not os.path.exists(spool_dir):
            os.makedirs(spool_dir)

        config_option = dict(
            smtp_host=self.options.get('smtp_host', 'localhost'),
            smtp_port=self.options.get('smtp_port', '25'),
            maildrop_dir=self.mail_dir,
            spool_dir=spool_dir,
            pid_file=self.pid_file,
            executable=self.buildout['buildout']['executable'],
            login=self.options.get('login', ''),
            password=self.options.get('password', ''),
            poll_interval=self.options.get('poll_interval', '120'),
            wait_interval=self.options.get('wait_interval', '0.0'),
            add_messageid=self.options.get('add_messageid', '0'),
            supervised_daemon=self.options.get('supervised_daemon', '0'),
            batch=self.options.get('batch', '0'),
            tls=self.options.get('tls', '0'),)

        config = open(self.configuration, 'wb')
        config.write(maildrop_config_template % config_option)
        return [self.configuration]

    def _build_script(self):
        """Create the startup script in the bin directory.
        """
        requirements, ws = self.egg.working_set(['infrae.maildrophost',])

        return zc.buildout.easy_install.scripts(
            [(self.name, 'infrae.maildrophost.ctl', 'main')],
            ws, self.options['executable'],
            self.options['bin-directory'],
            arguments={'pidfile': self.pid_file,
                       'configuration': self.configuration})

    def update(self):
        """Update the maildrophost server
        """
        files = []
        files.extend(self._build_config())
        files.extend(self._build_script())
        return files


maildrop_config_template="""
PYTHON=r"%(executable)s"
MAILDROP_HOME=r"%(maildrop_dir)s"
MAILDROP_VAR=r"%(maildrop_dir)s"
MAILDROP_SPOOL=r"%(spool_dir)s"
MAILDROP_PID_FILE=r"%(pid_file)s"

SMTP_HOST="%(smtp_host)s"
SMTP_PORT=%(smtp_port)s

MAILDROP_INTERVAL=%(poll_interval)s
DEBUG=0
DEBUG_RECEIVER=""

MAILDROP_BATCH=%(batch)s
MAILDROP_TLS=%(tls)s

MAILDROP_LOGIN="%(login)s"
MAILDROP_PASSWORD="%(password)s"

WAIT_INTERVAL=%(wait_interval)s
ADD_MESSAGEID=%(add_messageid)s

SUPERVISED_DAEMON=%(supervised_daemon)s
"""
