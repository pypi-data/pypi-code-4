# -*- coding: utf-8 -*-
# Copyright (c) 2007-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: __init__.py 33526 2009-02-13 11:11:59Z sylvain $

import os, shutil, tempfile, urllib2, urlparse
import zc.buildout, zc.recipe.egg
import setuptools

URL = ('http://www.dataflake.org/software/maildrophost/'
       'maildrophost_%s/MaildropHost-%s.tgz')

class Recipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.location = options.get(
            'target',
            os.path.join(
                self.buildout['buildout']['parts-directory'],
                self.name))
        options['location'] = self.location
        self.product_location = os.path.join(self.location, 'MaildropHost')
        self.url = options.get('url', None)
        if self.url is None:
            version = options.get('version')
            self.url = URL % (version, version)

        self.dont_create_directories = options.get(
            'dont_create_directories',
            'no').lower() in set(['yes', 'on' , 'true'])
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        self.mail_dir = self.options.get('mail_dir', None)
        if not self.mail_dir:
            self.mail_dir = os.path.join(
                self.buildout['buildout']['directory'], 'var', 'maildrop',)

    def install(self):
        """Install the maildrophost server
        """
        download_dir = self.buildout['buildout'].get(
            'download-cache',
            os.path.join(self.buildout['buildout']['directory'], 'downloads'))

        if not os.path.isdir(download_dir):
            os.mkdir(download_dir)

        _, _, urlpath, _, _, _ = urlparse.urlparse(self.url)
        tmp = tempfile.mkdtemp('buildout-'+self.name)
        try:
            fname = os.path.join(download_dir, urlpath.split('/')[-1])
            if not os.path.exists(fname):
                f = open(fname, 'wb')
                try:
                    f.write(urllib2.urlopen(self.url).read())
                except:
                    os.remove(fname)
                    raise zc.buildout.UserError(
                        "Failed to download URL %s: %s" % (self.url, str(e)))
                f.close()

            setuptools.archive_util.unpack_archive(fname, tmp)
            files = os.listdir(tmp)
            if not os.path.isdir(self.location):
                os.mkdir(self.location)
            shutil.move(os.path.join(tmp, files[0]), self.product_location)
        finally:
            shutil.rmtree(tmp)

        return self.update()

    def _build_config(self):
        """Create the config file for the maildrop server ; Create
        directory used by the maildrop server.
        """

        spool_dir = self.options.get(
            'spool_dir', None) or os.path.join(self.mail_dir, 'spool')
        pid_file = self.options.get(
            'pid_file', None) or os.path.join(self.mail_dir, 'maildrop.pid')
        if not self.dont_create_directories:
            if not os.path.exists(self.mail_dir):
                os.makedirs(self.mail_dir)
            if not os.path.exists(spool_dir):
                os.makedirs(spool_dir)

        config_option = dict(
            smtp_host=self.options.get('smtp_host', 'localhost'),
            smtp_port=self.options.get('smtp_port', '25'),
            maildrop_dir=self.mail_dir,
            spool_dir=spool_dir,
            pid_file=pid_file,
            executable=self.buildout['buildout']['executable'],
            login=self.options.get('login', ''),
            password=self.options.get('password', ''),
            poll_interval=self.options.get('poll_interval', '120'),
            wait_interval=self.options.get('wait_interval', '0.0'),
            add_messageid=self.options.get('add_messageid', '0'),
            supervised_daemon=self.options.get('supervised_daemon', '0'),
            batch=self.options.get('batch', '0'),
            tls=self.options.get('tls', '0'),)

        version = self.options.get('version', '0.00')
        major, minor = version.split('.')
        if int(major) < 2 and int(minor) < 22:
            config_filename = os.path.join(self.product_location, 'config.py')
        else:
            config_filename = os.path.join(self.product_location, 'config')
        config = open(config_filename, 'wb')
        config.write(maildrop_config_template % config_option)

    def _build_script(self):
        """Create the startup script in the bin directory.
        """
        requirements, ws = self.egg.working_set(['infrae.maildrophost'])
        pidfile=self.options.get(
            'pid_file', None) or os.path.join(self.mail_dir, 'maildrop.pid')
        config = dict(base=self.product_location,
                      pidfile=pidfile)

        zc.buildout.easy_install.scripts(
            [(self.name, 'infrae.maildrophost.ctl', 'main')],
            ws, self.options['executable'], self.options['bin-directory'],
            arguments=('%r, sys.argv[1:]' % config))

    def update(self):
        """Update the maildrophost server
        """
        try:
            self._build_config()
            self._build_script()
        except:
            shutil.rmtree(self.location)
            raise

        return self.location

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
