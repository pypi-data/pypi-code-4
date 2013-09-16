# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Test server fixtures for RabbitMQ."""

__metaclass__ = type

__all__ = [
    "RabbitServer",
    "RabbitServerResources",
    ]

import os
import re
import signal
import socket
import subprocess
import time

from amqplib import client_0_8 as amqp
from fixtures import (
    EnvironmentVariableFixture,
    Fixture,
    TempDir,
    )
from testtools.content import (
    Content,
    content_from_file,
    )
from testtools.content_type import UTF8_TEXT

# The default binaries have a check that the running use is uid 0 or uname
# 'rabbitmq', neither of which are needed to operate correctly. So we run the
# actual erlang binaries.
RABBITBIN = "/usr/lib/rabbitmq/bin"


def preexec_fn():
    # Revert Python's handling of SIGPIPE. See
    # http://bugs.python.org/issue1652 for more info.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def get_port(socket):
    """Return the port to which a socket is bound."""
    addr, port = socket.getsockname()
    return port


def allocate_ports(*addrs):
    """Allocate `len(addrs)` unused ports.

    A port is allocated for each element in `addrs`.

    There is a small race condition here (between the time we allocate the
    port, and the time it actually gets used), but for the purposes for which
    this function gets used it isn't a problem in practice.
    """
    sockets = [socket.socket() for addr in addrs]
    try:
        for addr, sock in zip(addrs, sockets):
            sock.bind((addr, 0))
        return [get_port(sock) for sock in sockets]
    finally:
        for sock in sockets:
            sock.close()


# Pattern to parse rabbitctl status output to find the nodename of a running
# node. New rabbitmq-servers don't have a running_nodes section, so we can't
# just look for that. Check that the node's status block reports rabbit.
status_regex = re.compile(r"""
    Status\ of\ node\ '?
      (?P<nodename>        # begin capture group
        [^@]+@[^@']+       # a node is name@hostname
      )'?\ \.\.\.\n        # end capture group
    \[(\{pid,\d+\},\n\ )?  # old versions don't show the pid.
    \{running_applications,.*
        \{rabbit,"RabbitMQ"
    """, re.VERBOSE | re.DOTALL)


def get_nodename_from_status(status_text):
    match = status_regex.search(status_text)
    return None if match is None else match.group("nodename")


class RabbitServerResources(Fixture):
    """Allocate the resources a RabbitMQ server needs.

    :ivar hostname: The host the RabbitMQ is on (always localhost for
        `RabbitServerResources`).
    :ivar port: A port that was free at the time setUp() was called.
    :ivar homedir: A directory to put the RabbitMQ logs in.
    :ivar mnesiadir: A directory for the RabbitMQ db.
    :ivar logfile: The logfile allocated for the server.
    :ivar nodename: The name of the node.
    """

    def __init__(self, hostname=None, port=None, homedir=None,
                 mnesiadir=None, logfile=None, nodename=None):
        super(RabbitServerResources, self).__init__()
        self._defaults = dict(
            hostname=hostname,
            port=port,
            homedir=homedir,
            mnesiadir=mnesiadir,
            logfile=logfile,
            nodename=nodename,
            )

    def setUp(self):
        super(RabbitServerResources, self).setUp()
        self.__dict__.update(self._defaults)
        if self.hostname is None:
            self.hostname = 'localhost'
        if self.port is None:
            [self.port] = allocate_ports(self.hostname)
        if self.homedir is None:
            self.homedir = self.useFixture(TempDir()).path
        if self.mnesiadir is None:
            self.mnesiadir = self.useFixture(TempDir()).path
        if self.logfile is None:
            self.logfile = os.path.join(self.homedir, 'server.log')
        if self.nodename is None:
            self.nodename = os.path.basename(self.useFixture(TempDir()).path)
        self.pluginsdir = self.useFixture(TempDir()).path

    @property
    def fq_nodename(self):
        """The node of the RabbitMQ that is being exported."""
        return "%s@%s" % (self.nodename, self.hostname)


class RabbitServerEnvironment(Fixture):
    """Export the environment variables needed to talk to a RabbitMQ instance.

    When setup this exports the key RabbitMQ variables:

    - ``RABBITMQ_MNESIA_BASE``
    - ``RABBITMQ_LOG_BASE``
    - ``RABBITMQ_NODE_IP_ADDRESS``
    - ``RABBITMQ_NODE_PORT``
    - ``RABBITMQ_NODENAME``
    - ``RABBITMQ_PLUGINS_DIR``

    """

    def __init__(self, config):
        """Create a `RabbitServerEnvironment` instance.

        :param config: An object exporting the variables
            `RabbitServerResources` exports.
        """
        super(RabbitServerEnvironment, self).__init__()
        self.config = config

    def setUp(self):
        super(RabbitServerEnvironment, self).setUp()
        self.useFixture(EnvironmentVariableFixture(
            "RABBITMQ_MNESIA_BASE", self.config.mnesiadir))
        self.useFixture(EnvironmentVariableFixture(
            "RABBITMQ_LOG_BASE", self.config.homedir))
        self.useFixture(EnvironmentVariableFixture(
            "RABBITMQ_NODE_IP_ADDRESS",
            socket.gethostbyname(self.config.hostname)))
        self.useFixture(EnvironmentVariableFixture(
            "RABBITMQ_NODE_PORT", str(self.config.port)))
        self.useFixture(EnvironmentVariableFixture(
            "RABBITMQ_NODENAME", self.config.fq_nodename))
        self.useFixture(EnvironmentVariableFixture(
            "RABBITMQ_PLUGINS_DIR", self.config.pluginsdir))
        self._errors = []
        self.addDetail('rabbit-errors', Content(
            UTF8_TEXT, self._get_errors))

    def _get_errors(self):
        """Yield all errors as UTF-8 encoded text."""
        for error in self._errors:
            if type(error) is unicode:
                yield error.encode('utf8')
            else:
                yield error
            yield '\n'

    def rabbitctl(self, command, strip=False):
        """Executes a ``rabbitctl`` command and returns status."""
        ctlbin = os.path.join(RABBITBIN, "rabbitmqctl")
        nodename = self.config.fq_nodename
        env = dict(os.environ, HOME=self.config.homedir)
        if isinstance(command, str):
            command = (command,)
        ctl = subprocess.Popen(
            (ctlbin, "-n", nodename) + command, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=preexec_fn)
        outstr, errstr = ctl.communicate()
        if strip:
            return outstr.strip(), errstr.strip()
        return outstr, errstr

    def is_node_running(self):
        """Checks that our RabbitMQ node is up and running."""
        nodename = self.config.fq_nodename
        outdata, errdata = self.rabbitctl("status")
        if errdata:
            self._errors.append(errdata)
        if not outdata:
            return False
        found_node = get_nodename_from_status(outdata)
        if found_node is None:
            self._errors.append(outdata)
            return False
        else:
            return found_node == nodename

    def get_connection(self):
        """Get an AMQP connection to the RabbitMQ server.

        :raises socket.error: If the connection cannot be made.
        """
        host_port = "%s:%s" % (self.config.hostname, self.config.port)
        return amqp.Connection(
            host=host_port, userid="guest",
            password="guest", virtual_host="/", insist=False)


class RabbitServerRunner(Fixture):
    """Run a RabbitMQ server."""

    def __init__(self, config):
        """Create a `RabbitServerRunner` instance.

        :param config: An object exporting the variables
            `RabbitServerResources` exports.
        """
        super(RabbitServerRunner, self).__init__()
        self.config = config
        self.process = None

    def setUp(self):
        super(RabbitServerRunner, self).setUp()
        self.environment = self.useFixture(
            RabbitServerEnvironment(self.config))
        self._start()

    def is_running(self):
        """Is the RabbitMQ server process still running?"""
        if self.process is None:
            return False
        else:
            return self.process.poll() is None

    def check_running(self):
        """Checks that the RabbitMQ server process is still running.

        :raises Exception: If it not running.
        :return: True if it is running.
        """
        if self.is_running():
            return True
        else:
            raise Exception("RabbitMQ server is not running.")

    def _spawn(self):
        """Spawn the RabbitMQ server process."""
        cmd = os.path.join(RABBITBIN, 'rabbitmq-server')
        env = dict(os.environ, HOME=self.config.homedir)
        with open(self.config.logfile, "wb") as logfile:
            with open(os.devnull, "rb") as devnull:
                self.process = subprocess.Popen(
                    [cmd], stdin=devnull, stdout=logfile, stderr=logfile,
                    close_fds=True, cwd=self.config.homedir, env=env,
                    preexec_fn=preexec_fn)
        self.addDetail(
            os.path.basename(self.config.logfile),
            content_from_file(self.config.logfile))

    def _start(self):
        """Start the RabbitMQ server."""
        # Check if Rabbit is already running. In truth this is really to avoid
        # a race condition around creating $HOME/.erlang.cookie: let rabbitctl
        # create it now, before spawning the daemon.
        if self.environment.is_node_running():
            raise AssertionError(
                "RabbitMQ OTP already running even though it "
                "hasn't been started it yet!")
        self._spawn()
        # Wait for the server to come up: stop when the process is dead, or
        # the timeout expires, or the server responds.
        timeout = time.time() + 15
        while time.time() < timeout and self.is_running():
            if self.environment.is_node_running():
                break
            time.sleep(0.3)
        else:
            raise Exception(
                "Timeout waiting for RabbitMQ server to start: log in %r." %
                (self.config.logfile,))
        # The Erlang OTP is up, but RabbitMQ may not be usable. We need to
        # cleanup up the process from here on in even if the full service
        # fails to get together.
        self.addCleanup(self._stop)
        # `rabbitctl status` can say a node is up before it is ready to accept
        # connections. Wait at least 5 more seconds for the node to come up...
        timeout = max(timeout, time.time() + 5)
        while time.time() < timeout and self.check_running():
            try:
                self.environment.get_connection().close()
            except socket.error:
                time.sleep(0.1)
            else:
                break
        else:
            raise Exception(
                "Timeout waiting for RabbitMQ node to come up: log in %r." %
                (self.config.logfile,))

    def _request_stop(self):
        outstr, errstr = self.environment.rabbitctl("stop", strip=True)
        if outstr:
            self.addDetail('stop-out', Content(UTF8_TEXT, lambda: [outstr]))
        if errstr:
            self.addDetail('stop-err', Content(UTF8_TEXT, lambda: [errstr]))

    def _stop(self):
        """Stop the running server. Normally called by cleanups."""
        self._request_stop()
        # Wait for the node to go down...
        timeout = time.time() + 15
        while time.time() < timeout:
            if not self.environment.is_node_running():
                break
            time.sleep(0.3)
        else:
            raise Exception(
                "Timeout waiting for RabbitMQ node to go down.")
        # Wait at least 5 more seconds for the process to end...
        timeout = max(timeout, time.time() + 5)
        while time.time() < timeout:
            if not self.is_running():
                break
            self.process.terminate()
            time.sleep(0.1)
        else:
            # Die!!!
            if self.is_running():
                self.process.kill()
                time.sleep(0.5)
            if self.is_running():
                raise Exception("RabbitMQ server just won't die.")


class RabbitServer(Fixture):
    """A RabbitMQ server fixture.

    When setup a RabbitMQ instance will be running and the environment
    variables needed to talk to it will be already configured.

    :ivar config: The `RabbitServerResources` used to start the server.
    :ivar runner: The `RabbitServerRunner` that bootstraps the server.
    """

    def __init__(self, config=None):
        super(RabbitServer, self).__init__()
        self.config = config

    def setUp(self):
        super(RabbitServer, self).setUp()
        if self.config is None:
            self.config = RabbitServerResources()
        self.useFixture(self.config)
        self.runner = RabbitServerRunner(self.config)
        self.useFixture(self.runner)
