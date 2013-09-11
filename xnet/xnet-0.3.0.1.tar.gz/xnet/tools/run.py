#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#


import sys
import os
import os.path
import optparse
import itertools
import time
import fcntl
import subprocess

import gevent
import gevent.pool
import gevent.monkey
from gevent.socket import wait_read

import xnet.tools
from xnet.net.ssh import SSHPopen


gevent.monkey.patch_all(thread=False)

DEVELOPMENT = 1

if DEVELOPMENT:
    #
    # FIXME: FULHACK dev
    #
    import os
    from os.path import join, abspath
    sys.path.insert(0, abspath(join(os.getcwd(), '../../')))


DEFAULT_NR_MICROTHREADS='128'

class XNetOptionParser(optparse.OptionParser):
    '''
        Provides some common options and an interface to add nicely formatted
        local options for each tool. Each local option is defined as a
        four-tuple of (shortoption, longoption, helptext, keyword-dict).

        Example follows below:

        class LocalOptionParser(OptionParserBase):
            local_options = [
                ('-p', '--port', 'Port to state.',
                    dict(dest='port'))
            ]
    '''
    def __init__(self, local_options, **kw):
        optparse.OptionParser.__init__(self, **kw)
        self.add_option('', '--test', dest='test', action='store_true',
                        help='run tests')
        self.add_option('', '--pdb', dest='pdb', action='store_true',
                        help='enable interactive pdb debugging on exceptions')
        self.add_option('', '--print-source', dest='print_source', action='store_true',
                        help='print source code of tool')
        self.add_option('-x', '--nr-microthreads', dest='nr_microthreads', metavar='n',
                        help='number of microthreads per process (default 128)')
        self.add_option('-y', '--nr-processes', dest='nr_processes', metavar='n',
                        help='number of processes (default 1)')
        self.add_option('-z', '--ssh-nodes-file', dest='ssh_nodes_file', metavar='path',
                        help='ssh workers file with user@host on each line')
        self.add_option('', '--ssh-args', dest='ssh_args', metavar='..',
                        help='additional arguments to the ssh command')
        self.add_option('', '--ssh-display', dest='ssh_display', metavar='..',
                        help='export DISPLAY=.. on ssh nodes')
        self.add_option('-r', '--read', dest='read', metavar='path',
                        help='read input from file')
        self.add_option('-w', '--wait', dest='wait', metavar='nsecs',
                        help='wait at most nsecs seconds for actions to complete')
        self.add_option('-i', '--interval', dest='interval', metavar='nsecs',
                        help='time interval between each action ')
        self.add_option('', '--repeat', dest='repeat', metavar='ntimes',
                        help='repeat action this many times (-1 = infinity)')
        self.add_option('', '--time', dest='time', action='store_true',
                        help='print time consumed by action')
        self.add_option('-T', '--supress-timeout', dest='supress_timeout',
                        help='supress messages from tasks timing out', action='store_true')
        self.add_option('', '--apply', dest='apply', metavar='fn',
                        help='execute python function `fn` for each input: item = fn(item)')
        self.add_option('-f', '--format', dest='format', metavar='fmt',
                        help='specify output format, see --format-help for info')
        self.add_option('', '--format-help', dest='format_help', action='store_true',
                        help='print output format help')
        self.add_option('', '--split-output', dest='split_output', metavar='base',
                        help='produce one output file for each piece of input')
        self.add_option('', '--split-tee', dest='split_tee', metavar='base',
                        help='like --split-output but also print to stdout')
        self.add_option('-v', '--verbose', dest='verbose',
                        help='verbose output', action='count')
        self._load_local_options(local_options)

    def _load_local_options(self, local_options):
        for (short_, long_, help_, kw) in local_options:
            help_ = '* ' + help_  # mark tool-unique options
            self.add_option(short_, long_, help=help_, **kw)


def get_action_usage():
    _action_usage = ''
    for tup in _available_actions:
        name = tup[0]
        desc = available_actions[name].__description__
        line = ' '
        line += name
        line += ' ' * (11 - len(name))
        line += desc
        line += '\n'
        _action_usage += line
    return _action_usage


__usage__ = """

    $$$ Merry Xnet! $$$

 $ {{tool}} [options] item1 item2 ...
 $ {{tool}} [options] -r itemfile.txt
 $ cat itemsfile.txt | {{tool}} [options] -
"""


def top_usage():
    output = __usage__
    output += '\n'
    output += 'Available tools:\n'
    output += get_action_usage()
    return output


def print_error(a):
    errmsg = str(a.error)
    if not errmsg.strip():
        errmsg = 'no-error-set\n'
    if not errmsg[-1] == '\n':
        errmsg += '\n'
    item = str(a._item).strip()
    errmsg = item + ' ' + errmsg
    sys.stderr.write(errmsg)


def stdin_disperser_greenlet(pool):
    '''
        loop forever feeding active greenlets with data
        read from stdin.
    '''
    done = False
    fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
    while not done:
        wait_read(sys.stdin.fileno())
        try:
            data = sys.stdin.read()
        except:
            raise
        done = (data == '')
        for greenlet in pool:
            obj = greenlet._run  # fulhack
            if not hasattr(obj, '__massage__'):  # fulhack
                continue
            #obj.feed_stdin(data)  # put in queue or list
            os.write(obj._stdin_pipe[1], data)


def _get_output_filepath(a, base):
    #
    # item is the result of some specific processing
    # and may contain arbitrary meta characters
    # which should not affect the file system path
    # where the output file is created.
    #
    path = base + a.__filename__()
    return path


def repeaterator(it, count):
    '''
        repeat iterator count times or -1 for infinity
    '''
    assert type(count) is int
    cpy = []
    if count != 0:
        for item in it:
            cpy.append(item)
            yield item
        if count > 0:
            count -= 1
    while count != 0:
        for item in cpy:
            yield item
        if count > 0:
            count -= 1


def do_ssh(opt, ToolImplementation, args, inputchain):
    argv = sys.argv[:]
    subprocesses = []
    for ssh_node in SSHPopen.parse_ssh_nodes_file(opt.ssh_nodes_file):
        user, host = ssh_node.split('@', 1)
        env = {}
        if opt.ssh_display:
            env['DISPLAY'] = opt.ssh_display
        ssh_args = opt.ssh_args or []
        proc = SSHPopen(ssh_args, argv, args, user=user, host=host,
                        stdin=subprocess.PIPE, env=env)
        subprocesses.append(proc)

    for (i, item) in enumerate(inputchain):
        #
        # Newlines are our input separator.
        # Should this be argument-controlled?
        #
        while len(item) and item[-1] == '\n':
            item = item[:-1]
        item += '\n'
        proc_index = i % len(subprocesses)
        proc = subprocesses[proc_index]
        proc.stdin.write(item)

    for proc in subprocesses:
        #print os.getpid(), 'SSH-CLOSE-STDIN', proc
        proc.stdin.close()

    for proc in subprocesses:
        #print os.getpid(), 'SSH-WAIT', proc
        proc.wait()
    return 0


def do_fork(opt, ToolImplementation, tool_reads_stdin, args, nr_processes, nr_microthreads, inputchain):
    #
    # Remove --nr-processes from sys.argv and spawn children.
    #
    argv = sys.argv[:]
    if '-y' in argv:
        i = argv.index('-y')
        del argv[i]
        del argv[i]
    if '--nr-processes' in argv:
        i = argv.index('--nr-processes')
        del argv[i]
        del argv[i]
    if '--nr-processes={0}'.format(nr_processes) in argv:
        argv.remove('--nr-processes={0}'.format(nr_processes))

    #
    # Remove all non-option args from argv before remote
    # execution; these values will be trickled down and
    # distributed across nodes from the parent invocation.
    #
    for non_option_arg in args[1:]:
        while non_option_arg in argv:
            i = argv.index(non_option_arg)
            del argv[i]

    if not '-' in argv:
        argv.append('-')

    subprocesses = []

    #
    # Spawn subprocesses.
    #
    subprocesses = []
    for i in xrange(nr_processes):
        proc = subprocess.Popen(argv, stdin=subprocess.PIPE)
        subprocesses.append(proc)

    for (i, item) in enumerate(inputchain):
        #
        # Newlines are our input separator.
        # Should this be argument-controlled?
        #
        while len(item) and item[-1] == '\n':
            item = item[:-1]
        item += '\n'
        proc_index = i % nr_processes
        proc = subprocesses[proc_index]
        proc.stdin.write(item)

    for proc in subprocesses:
        #print os.getpid(), 'CLOSE STDIN', proc
        proc.stdin.close()

    for proc in subprocesses:
        #print os.getpid(), 'WAIT', proc
        proc.wait()


def run(ToolImplementation, tool_reads_stdin=False):
    try:
        return _run(ToolImplementation, tool_reads_stdin)
    except KeyboardInterrupt:
        return 1


def _run(ToolImplementation, tool_reads_stdin):
    '''
            tool_reads_stdin - tool uses stdin for other purpose than
                               to obtain startup arguments
    '''
    args = sys.argv[:]
    action_name = args[0]
    #args = list(args)[1:]

    _E_INVALID_ARGUMENT_STDIN = \
        '-: Invalid argument, target hosts may not be specified on stdin.'

    _usage = __usage__.replace('{{tool}}', action_name)
    if hasattr(ToolImplementation, '__itemname__'):
        itemname = ToolImplementation.__itemname__
        _usage = _usage.replace('item', itemname)
    parser = XNetOptionParser(ToolImplementation.cmdline_options, usage=_usage)
    (opt, args) = parser.parse_args(args)
    cmdlineinputs = args[1:]

    #
    # chain input sources, handle options
    # precedence order: cmdline, -r, stdin
    #
    # If --nr-processes=n and n > 1, then let this process
    # produce for a number of child processes.
    #
    _inputs = []
    if '-' in cmdlineinputs:
        if tool_reads_stdin:
            raise Exception(_E_INVALID_ARGUMENT_STDIN)
        cmdlineinputs.remove('-')
        _inputs.append(sys.stdin)
    if opt.read:
        f = open(opt.read)
        _inputs.insert(0, f)
    if len(cmdlineinputs):
        _inputs.insert(0, cmdlineinputs)
    inputchain = itertools.chain(*_inputs)

    _nr_processes = 1
    if opt.nr_processes:
        _nr_processes = int(opt.nr_processes)

    if opt.pdb:
        import xnet.debug
        xnet.debug.interactive_debugger_on_exception(True)

    if opt.print_source:
        ToolImplementation.print_source()
        return

    _nr_microthreads = 128
    if not opt.nr_microthreads is None:
        _nr_microthreads = int(opt.nr_microthreads)

    _wait = None
    if not opt.wait is None:
        _wait = float(opt.wait)

    _interval = 0.0
    if not opt.interval is None:
        _interval = float(opt.interval)

    _repeat = 1
    if not opt.repeat is None:
        _repeat = int(opt.repeat)

    if opt.format_help:
        print ToolImplementation.__format_help__()
        sys.exit(0)

    if opt.split_tee:
        opt.split_output = opt.split_tee

    _outfile = sys.stdout

    #
    # Handle SSH-distributed execution.
    # If SSH-dist., main process returns on do_ssh() here.
    #
    if opt.ssh_nodes_file:
        #
        # __massage__() expands wildcard IP-ranges such as 10.0.0.*.
        # This should be done in parent in order to split the expanded
        # set of IP:s across its children.
        #
        inputchain = ToolImplementation.__massage__(inputchain, opt)
        if _repeat != 1:
            inputchain = repeaterator(inputchain, _repeat)
        return do_ssh(opt, ToolImplementation, args, inputchain)

    #
    # Handle multiproc.
    # If multiproc, main process returns on do_fork() here.
    #
    if _nr_processes == 1:
        pass
    elif _nr_processes < 1:
        errmsg = 'invalid number of processes: {0}'.format(_nr_processes)
        sys.stderr.write(errmsg)
        sys.exit(1)
    else:
        #
        # __massage__() expands wildcard IP-ranges such as 10.0.0.*.
        # This should be done in parent in order to split the expanded
        # set of IP:s across its children.
        #
        inputchain = ToolImplementation.__massage__(inputchain, opt)
        if _repeat != 1:
            inputchain = repeaterator(inputchain, _repeat)
        return do_fork(opt, ToolImplementation, tool_reads_stdin, args,
                       _nr_processes, _nr_microthreads, inputchain)

    #
    # verify commandline options and do preparations
    #
    ToolImplementation.__setup__(opt)

    #
    # Errors if pool is too small.
    #
    pool = gevent.pool.Pool(_nr_microthreads)
    #pool = gevent.pool.Pool(opt.nr_microthreads or DEFAULT_NR_MICROTHREADS)
    greenlets = []

    wkpool = None
    if _wait:
        wkpool = gevent.pool.Pool(_nr_microthreads)

    def waitkill(g, killtime):
        from xnet.tools import WaitTimeout
        sleeptime = killtime - time.time()
        #print 'waitkill', sleeptime
        if sleeptime > 0:
            gevent.sleep(sleeptime)
        if not g.ready():
            gevent.kill(g, WaitTimeout)
            g.join()

    inputchain = ToolImplementation.__massage__(inputchain, opt)

    kwargs = {}

    if tool_reads_stdin:
        gevent.spawn(stdin_disperser_greenlet, pool)

    _t = 0.0
    killtime = 0

    if _repeat != 1:
        inputchain = repeaterator(inputchain, _repeat)

    greenlet_id = 0
    for (i, line) in enumerate(inputchain):
        action = ToolImplementation(opt, greenlet_id=greenlet_id, **kwargs)
        greenlet_id += 1
        pool.wait_available()
        if _wait:
            killtime = time.time() + _wait
        g = pool.spawn(action, line, inputchain)
        g.action = action
        greenlets.append(g)
        #
        # Timeout seems unreliable on debian squeeze, use waitkill instead.
        #
        if _wait:
            wkpool.wait_available()
            wkpool.spawn(waitkill, g, killtime)

        #
        # handle finished actions
        #
        while len(greenlets) and greenlets[0].ready():
            action = greenlets[0].action
            output_action_result(action, opt, _outfile)
            del action
            del greenlets[0]

        #
        # handle interval
        #
        _this_interval = _interval - (time.time() - _t)
        if _this_interval > 0:
            gevent.sleep(_this_interval)
        _t = time.time()

    if wkpool:
        wkpool.join()
    gevent.joinall(greenlets)  #, timeout=timeout)
    not_done = filter(lambda g: (not g.ready()), greenlets)
    if len(not_done) > 0 and not _wait is None:
        print 'ERROR: not_done has contents inspite of _wait and grace time'
        print not_done

    #
    # Force-kill greenlets that didn't die in spite of 1 sec of grace time.
    #
    gevent.killall(not_done, block=True)
    gevent.joinall(not_done)

    #
    # cleanups
    #
    ToolImplementation.__teardown__(opt)

    #
    # print results
    #
    for g in greenlets:
        action = g.action
        output_action_result(action, opt, _outfile)
        del action


def output_action_result(a, opt, _outfile):
    outfile = _outfile
    if opt.split_output:
        path = _get_output_filepath(a, opt.split_output)
        outfile = open(path, 'wb')
    if not a.error is None:
        if a.error == xnet.tools.WaitTimeout:
            if not opt.supress_timeout:
                #
                # __timeout__() messages always go to stderr.
                #
                msg = a.__timeout__()
                if not msg is None:
                    sys.stderr.write(msg)
        else:
            if opt.verbose >= a._error_verbosity_limit:
                print_error(a)
    else:
        if a._action_result:
            msg = str(a)
            #
            # ignore empty output from Tool.__format__()
            #
            if len(msg) == 0:
                return
            msg += '\n'
            if a.stderr:
                outfile = sys.stderr
            outfile.write(msg)
            if opt.split_tee and not a.stderr:
                _outfile.write(msg)

    _outfile.flush()
    if not outfile is _outfile:
        outfile.flush()

    if opt.split_output:
        outfile.close()


__xnet_usage__ = '''

    $$$ Merry Xnet! $$$

The following xnet tools are available in your PATH, if installation succeeded:
 xnet      - xnet meta tool
 iprange   - IP range enumerator
 resolv    - hostname resolver
 tcpstate  - port scanner
 netcats   - multi-peer netcat client
 webget    - web client
 sslinfo   - SSL info harvester
 iissn     - IIS shortname enumeration

Help for some specific tool:
 $ tcpstate --help

Analogous commands:
 $ iprange ...
 $ xnet iprange ...
 $ iprange --print-source > foo.py && xnet foo.py

Develop your own, or make alternative versions of existing xnet tools:
 $ existing_xnet_tool --print-source > newtool.py
 $ vim newtool.py
 $ xnet newtool.py ...
'''


def main():
    args = sys.argv[:]

    if len(args) < 2 or args[1] in ('-h', '--help'):
        print __xnet_usage__
        return

    ToolImplementation = None

    toolname = args[1]
    if toolname.endswith('.py'):
        if not toolname.startswith('/'):
            toolname = os.path.abspath(toolname)
        if not os.path.exists(toolname):
            print 'File not found:', toolname
        folder = os.path.dirname(toolname)
        if len(folder):
            sys.path.insert(0, folder)
        modulename = os.path.basename(toolname).rsplit('.', 1)[0]
        toolmodule = __import__(modulename)
        sys.path = sys.path[1:]
        for name in dir(toolmodule):
            val = getattr(toolmodule, name)
            found = False
            try:
                if issubclass(val, xnet.tools.Tool):
                    found = True
            except TypeError:
                pass
            if found and not val is xnet.tools.Tool:
                if not ToolImplementation is None:
                    errmsg = 'Multiple Tool implementations in {0}: {1}, {2}'
                    errmsg = errmsg.format(toolname, ToolImplementation, val)
                    print errmsg
                    sys.exit(1)
                ToolImplementation = val

    if not ToolImplementation:
        if toolname == 'iissn':
            from xnet.tools.iissn import IISShortnameTool as ToolImplementation
        if toolname == 'iprange':
            from xnet.tools.iprange import IPRangeTool as ToolImplementation
        if toolname == 'netcats':
            from xnet.tools.netcats import NetcatsTool as ToolImplementation
        if toolname == 'resolv':
            from xnet.tools.resolv import ResolvTool as ToolImplementation
        if toolname == 'sslinfo':
            from xnet.tools.sslinfo import SSLInfoTool as ToolImplementation
        if toolname == 'tcpstate':
            from xnet.tools.tcpstate import TcpStateTool as ToolImplementation
        if toolname == 'webget':
            from xnet.tools.webget import WebgetTool as ToolImplementation

    if not ToolImplementation:
        print 'Tool not found:', toolname
        sys.exit(1)

    sys.argv = sys.argv[1:]

    result = run(ToolImplementation)
    return result


if __name__ == "__main__":
    main()
    #if '--test' in sys.argv:
    #    sys.argv.remove('--test')
    #    doctest.testmod()
    #    unittest.main()
    #else:
    #    main(*sys.argv)
