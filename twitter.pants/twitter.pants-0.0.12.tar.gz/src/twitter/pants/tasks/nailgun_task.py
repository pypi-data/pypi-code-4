# ==================================================================================================
# Copyright 2011 Twitter, Inc.
# --------------------------------------------------------------------------------------------------
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this work except in compliance with the License.
# You may obtain a copy of the License in the LICENSE file, or at:
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================================

import os
import re
import subprocess
import sys
import time

from twitter.common import log
from twitter.common.dirutil import safe_open

from twitter.pants import binary_util, get_buildroot
from twitter.pants.java import NailgunClient
from twitter.pants.tasks import Task


def _check_pid(pid):
  try:
    os.kill(pid, 0)
    return True
  except OSError:
    return False


class NailgunTask(Task):
  # Used to identify we own a given java nailgun server
  PANTS_NG_ARG_PREFIX = '-Dtwitter.pants.buildroot'
  PANTS_NG_ARG = '%s=%s' % (PANTS_NG_ARG_PREFIX, get_buildroot())

  _DAEMON_OPTION_PRESENT = False

  @staticmethod
  def create_pidfile_arg(pidfile):
    return '-Dpidfile=%s' % os.path.relpath(pidfile, get_buildroot())

  @staticmethod
  def _log_kill(log, pid, port=None):
    log.info('killing ng server @ pid:%d%s' % (pid, ' port:%d' % port if port else ''))

  @classmethod
  def setup_parser(cls, option_group, args, mkflag):
    if not NailgunTask._DAEMON_OPTION_PRESENT:
      option_group.parser.add_option("--ng-daemons", "--no-ng-daemons", dest="nailgun_daemon",
                                     default=True, action="callback", callback=mkflag.set_bool,
                                     help="[%default] Use nailgun daemons to execute java tasks.")
      NailgunTask._DAEMON_OPTION_PRESENT = True

  def __init__(self, context, use_daemon=None, classpath=None, workdir=None, nailgun_args=None,
               stdin=None, stderr=sys.stderr, stdout=sys.stdout):
    Task.__init__(self, context)

    self._classpath = classpath
    self._nailgun_profile = context.config.get('nailgun', 'profile', default='nailgun')
    self._ng_server_args = nailgun_args or context.config.getlist('nailgun', 'args')
    self._stdin = stdin
    self._stderr = stderr
    self._stdout = stdout
    self._daemon = use_daemon if use_daemon is not None else context.options.nailgun_daemon

    workdir = workdir or os.path.join(context.config.get('nailgun', 'workdir'),
                                      self.__class__.__name__)
    self._pidfile = os.path.join(workdir, 'pid')
    self._ng_out = os.path.join(workdir, 'stdout')
    self._ng_err = os.path.join(workdir, 'stderr')

  def _runjava_common(self, main, classpath=None, opts=None, args=None, jvmargs=None):
    cp = (self._classpath or []) + (classpath or [])
    if self._daemon:
      nailgun = self._get_nailgun_client()
      try:
        if cp:
          nailgun('ng-cp', *[os.path.relpath(jar, get_buildroot()) for jar in cp])
        opts_args = []
        if opts:
          opts_args.extend(opts)
        if args:
          opts_args.extend(args)

        log.debug('Executing via nailgun %s: %s %s' % (nailgun, main, ' '.join(opts_args)))
        return nailgun(main, *opts_args)
      except nailgun.NailgunError as e:
        self._ng_shutdown()
        raise e
    else:
      return binary_util.runjava(main=main, classpath=cp, opts=opts, args=args, jvmargs=jvmargs)

  def runjava(self, main, classpath=None, opts=None, args=None, jvmargs=None):
    """Runs the java main using the given classpath and args.

    If --no-ng-daemons is specified then the java main is run in a freshly spawned subprocess,
    otherwise a persistent nailgun server dedicated to this Task subclass is used to speed up
    amortized run times. The args list is divisable so it can be split across multiple invocations
    of the command similiar to xargs.
    """

    return self._runjava_common(main, classpath=classpath, opts=opts, args=args, jvmargs=jvmargs)

  def runjava_indivisible(self, main, classpath=None, opts=None, args=None, jvmargs=None):
    """Runs the java main using the given classpath and args.

    If --no-ng-daemons is specified then the java main is run in a freshly spawned subprocess,
    otherwise a persistent nailgun server dedicated to this Task subclass is used to speed up
    amortized run times. The args list is indivisable so it can't be split across multiple
    invocations of the command similiar to xargs.
    """

    return self._runjava_common(main, classpath=classpath, opts=opts, args=args, jvmargs=jvmargs)

  def profile_classpath(self, profile):
    """Ensures the classpath for the given profile ivy.xml is available and returns it as a list of
    paths.

    If the classpath has changed since the last check for this profile this Task's build cache is
    invalidated.

    profile: The name of the tool profile classpath to ensure.
    """
    updated, classpath = binary_util.profile_classpath(profile,
                                                       java_runner=self.runjava_indivisible,
                                                       config=self.context.config)
    if updated:
      self.invalidate()
    return classpath

  def _ng_shutdown(self):
    endpoint = self._get_nailgun_endpoint()
    if endpoint:
      pid, port = endpoint
      NailgunTask._log_kill(self.context.log, pid, port)
      try:
        os.kill(pid, 9)
      except OSError:
        pass
      finally:
        os.remove(self._pidfile)

  def _get_nailgun_endpoint(self):
    if os.path.exists(self._pidfile):
      with safe_open(self._pidfile, 'r') as pidfile:
        contents = pidfile.read()

        def invalid_pidfile():
          log.warn('Invalid ng pidfile %s contained: %s' % (self._pidfile, contents))
          return None
        endpoint = contents.split(':')
        if len(endpoint) != 2:
          return invalid_pidfile()
        pid, port = endpoint
        try:
          return int(pid.strip()), int(port.strip())
        except ValueError:
          return invalid_pidfile()
    elif NailgunTask._find:
      pid_port = NailgunTask._find(self._pidfile)
      if pid_port:
        self.context.log.info('found ng server @ pid:%d port:%d' % pid_port)
        with safe_open(self._pidfile, 'w') as pidfile:
          pidfile.write('%d:%d\n' % pid_port)
      return pid_port
    return None

  def _get_nailgun_client(self):
    updated, ng_classpath = binary_util.profile_classpath(self._nailgun_profile)
    endpoint = self._get_nailgun_endpoint()
    running = _check_pid(endpoint[0]) if endpoint else False
    if running and not updated:
      return self._create_ngclient(port=endpoint[1])
    else:
      if running and updated:
        self._ng_shutdown()
      return self._spawn_nailgun_server(ng_classpath)

  # 'NGServer started on 127.0.0.1, port 53785.'
  _PARSE_NG_PORT = re.compile('.*\s+port\s+(\d+)\.$')

  def _parse_nailgun_port(self, line):
    match = NailgunTask._PARSE_NG_PORT.match(line)
    if not match:
      raise NailgunClient.NailgunError('Failed to determine spawned ng port from response'
                                       ' line: %s' % line)
    return int(match.group(1))

  def _await_nailgun_server(self):
    nailgun_timeout_seconds = 5
    max_socket_connect_attempts = 10
    nailgun = None
    port_parse_start = time.time()
    with safe_open(self._ng_out, 'r') as ng_out:
      while not nailgun:
        started = ng_out.readline()
        if started:
          port = self._parse_nailgun_port(started)
          with open(self._pidfile, 'a') as pidfile:
            pidfile.write(':%d\n' % port)
          nailgun = self._create_ngclient(port)
          log.debug('Detected ng server up on port %d' % port)
        elif time.time() - port_parse_start > nailgun_timeout_seconds:
          raise NailgunClient.NailgunError('Failed to read ng output after'
                                           ' %s seconds' % nailgun_timeout_seconds)

    attempt = 0
    while nailgun:
      sock = nailgun.try_connect()
      if sock:
        sock.close()
        log.info('Connected to ng server pid: %d @ port: %d' % self._get_nailgun_endpoint())
        return nailgun
      elif attempt > max_socket_connect_attempts:
        raise nailgun.NailgunError('Failed to connect to ng output after %d connect attempts'
                                   % max_socket_connect_attempts)
      attempt += 1
      log.debug('Failed to connect on attempt %d' % attempt)
      time.sleep(0.1)

  def _create_ngclient(self, port):
    return NailgunClient(port=port, work_dir=get_buildroot(), ins=self._stdin, out=self._stdout,
                         err=self._stderr)

  def _spawn_nailgun_server(self, ng_classpath):
    log.info('No ng server found, spawning...')

    with safe_open(self._ng_out, 'w'):
      pass  # truncate

    pid = os.fork()
    if pid != 0:
      # In the parent tine - block on ng being up for connections
      return self._await_nailgun_server()

    os.setsid()
    in_fd = open('/dev/null', 'w')
    out_fd = safe_open(self._ng_out, 'w')
    err_fd = safe_open(self._ng_err, 'w')

    args = ['java']
    if self._ng_server_args:
      args.extend(self._ng_server_args)
    args.append(NailgunTask.PANTS_NG_ARG)
    args.append(NailgunTask.create_pidfile_arg(self._pidfile))
    args.extend(['-cp', os.pathsep.join(ng_classpath),
                 'com.martiansoftware.nailgun.NGServer', ':0'])
    log.debug('Executing: %s' % ' '.join(args))

    with binary_util.safe_classpath(logger=log.warn):
      process = subprocess.Popen(
        args,
        stdin=in_fd,
        stdout=out_fd,
        stderr=err_fd,
        close_fds=True,
        cwd=get_buildroot()
      )
      with safe_open(self._pidfile, 'w') as pidfile:
        pidfile.write('%d' % process.pid)
      log.debug('Spawned ng server @ %d' % process.pid)
      # Prevents finally blocks and atexit handlers from being executed, unlike sys.exit(). We
      # don't want to execute finally blocks because we might, e.g., clean up tempfiles that the
      # parent still needs.
      os._exit(0)


try:
  import psutil

  def _find_ngs(everywhere=False):
    def cmdline_matches(cmdline):
      if everywhere:
        return any(filter(lambda arg: arg.startswith(NailgunTask.PANTS_NG_ARG_PREFIX), cmdline))
      else:
        return NailgunTask.PANTS_NG_ARG in cmdline

    for proc in psutil.process_iter():
      try:
        if 'java' == proc.name and cmdline_matches(proc.cmdline):
          yield proc
      except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

  def killall(log, everywhere=False):
    for proc in _find_ngs(everywhere=everywhere):
      try:
        NailgunTask._log_kill(log, proc.pid)
        proc.kill()
      except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass

  NailgunTask.killall = staticmethod(killall)

  def _find_ng_listen_port(proc):
    for connection in proc.get_connections(kind='tcp'):
      if connection.status == 'LISTEN':
        host, port = connection.local_address
        return port
    return None

  def _find(pidfile):
    pidfile_arg = NailgunTask.create_pidfile_arg(pidfile)
    for proc in _find_ngs(everywhere=False):
      try:
        if pidfile_arg in proc.cmdline:
          port = _find_ng_listen_port(proc)
          if port:
            return proc.pid, port
      except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    return None

  NailgunTask._find = staticmethod(_find)
except ImportError:
  NailgunTask.killall = None
  NailgunTask._find = None
