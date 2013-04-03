"""
This file defines what is required for swftp-sftp to work with twistd.

See COPYING for license information.
"""
from twisted.application import internet, service
from twisted.python import usage, log
from twisted.internet import reactor

import ConfigParser
import signal
import os
import sys
import time


def run():
    options = Options()
    try:
        options.parseOptions(sys.argv[1:])
    except usage.UsageError, errortext:
        print '%s: %s' % (sys.argv[0], errortext)
        print '%s: Try --help for usage details.' % (sys.argv[0])
        sys.exit(1)
    log.startLogging(sys.stdout)
    s = makeService(options)
    s.startService()
    reactor.run()


def get_config(config_path, overrides):
    defaults = {
        'auth_url': 'http://127.0.0.1:8080/auth/v1.0',
        'host': '0.0.0.0',
        'port': '5022',
        'priv_key': '/etc/swftp/id_rsa',
        'pub_key': '/etc/swftp/id_rsa.pub',
        'num_persistent_connections': '4',
        'connection_timeout': '240',
        'log_statsd_host': '',
        'log_statsd_port': '8125',
        'log_statsd_sample_rate': '10.0',
        'log_statsd_metric_prefix': 'swftp.sftp',
    }
    c = ConfigParser.ConfigParser(defaults)
    c.add_section('sftp')
    if config_path:
        log.msg('Reading configuration from path: %s' % config_path)
        c.read(config_path)
    else:
        config_paths = [
            '/etc/swftp/swftp.conf',
            os.path.expanduser('~/.swftp.cfg')
        ]
        log.msg('Reading configuration from paths: %s' % config_paths)
        c.read(config_paths)
    for k, v in overrides.iteritems():
        if v:
            c.set('sftp', k, v)
    return c


class Options(usage.Options):
    "Defines Command-line options for the swftp-sftp service"
    optFlags = []
    optParameters = [
        ["config_file", "c", None, "Location of the swftp config file."],
        ["auth_url", "a", None,
            "Auth Url to use. Defaults to the config file value if it exists."
            "[default: http://127.0.0.1:8080/auth/v1.0]"],
        ["port", "p", None, "Port to bind to."],
        ["host", "h", None, "IP to bind to."],
        ["priv_key", "priv-key", None, "Private Key Location."],
        ["pub_key", "pub-key", None, "Public Key Location."],
    ]


def makeService(options):
    """
    Makes a new swftp-sftp service. The only option is the config file
    location. The config file has the following options:
     - host
     - port
     - auth_url
     - num_persistent_connections
     - connection_timeout
     - pub_key
     - priv_key
    """
    from twisted.conch.ssh.factory import SSHFactory
    from twisted.conch.ssh.keys import Key
    from twisted.web.client import HTTPConnectionPool
    from twisted.cred.portal import Portal

    from swftp.sftp.server import SwiftSFTPRealm, SwiftSSHServerTransport
    from swftp.sftp.connection import SwiftConnection
    from swftp.auth import SwiftBasedAuthDB
    from swftp.utils import print_runtime_info

    c = get_config(options['config_file'], options)
    pool = HTTPConnectionPool(reactor, persistent=True)
    pool.maxPersistentPerHost = c.getint('sftp', 'num_persistent_connections')
    pool.cachedConnectionTimeout = c.getint('sftp', 'connection_timeout')

    sftp_service = service.MultiService()

    # ensure timezone is GMT
    os.environ['TZ'] = 'GMT'
    time.tzset()

    # Add statsd service
    if c.get('sftp', 'log_statsd_host'):
        try:
            from swftp.statsd import makeService as makeStatsdService
            makeStatsdService(
                c.get('sftp', 'log_statsd_host'),
                c.getint('sftp', 'log_statsd_port'),
                sample_rate=c.getfloat('sftp', 'log_statsd_sample_rate'),
                prefix=c.get('sftp', 'log_statsd_metric_prefix')
            ).setServiceParent(sftp_service)
        except ImportError:
            log.err('Missing Statsd Module. Requires "txstatsd"')

    authdb = SwiftBasedAuthDB(auth_url=c.get('sftp', 'auth_url'))

    sftpportal = Portal(SwiftSFTPRealm())
    sftpportal.registerChecker(authdb)

    sshfactory = SSHFactory()
    sshfactory.protocol = SwiftSSHServerTransport
    sshfactory.noisy = False
    sshfactory.portal = sftpportal
    sshfactory.services['ssh-connection'] = SwiftConnection

    pub_key_string = file(c.get('sftp', 'pub_key')).read()
    priv_key_string = file(c.get('sftp', 'priv_key')).read()
    sshfactory.publicKeys = {
        'ssh-rsa': Key.fromString(data=pub_key_string)}
    sshfactory.privateKeys = {
        'ssh-rsa': Key.fromString(data=priv_key_string)}

    signal.signal(signal.SIGUSR1, print_runtime_info)
    signal.signal(signal.SIGUSR2, print_runtime_info)

    internet.TCPServer(
        c.getint('sftp', 'port'),
        sshfactory,
        interface=c.get('sftp', 'host')).setServiceParent(sftp_service)

    return sftp_service
