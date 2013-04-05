#!/usr/bin/env python
"""A simple interactive kernel that talks to a frontend over 0MQ.

Things to do:

* Implement `set_parent` logic. Right before doing exec, the Kernel should
  call set_parent on all the PUB objects with the message about to be executed.
* Implement random port and security key logic.
* Implement control messages.
* Implement event loop and poll version.
"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function

# Standard library imports
import __builtin__
import atexit
import sys
import time
import traceback
import logging
import uuid

from datetime import datetime
from signal import (
        signal, getsignal, default_int_handler, SIGINT, SIG_IGN
)

# System library imports
import zmq
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream

# Local imports
from IPython.config.configurable import Configurable
from IPython.config.application import boolean_flag, catch_config_error
from IPython.core.application import ProfileDir
from IPython.core.error import StdinNotImplementedError
from IPython.core.shellapp import (
    InteractiveShellApp, shell_flags, shell_aliases
)
from IPython.utils import io
from IPython.utils import py3compat
from IPython.utils.frame import extract_module_locals
from IPython.utils.jsonutil import json_clean
from IPython.utils.traitlets import (
    Any, Instance, Float, Dict, CaselessStrEnum, List, Set, Integer, Unicode
)

from entry_point import base_launch_kernel
from kernelapp import KernelApp, kernel_flags, kernel_aliases
from serialize import serialize_object, unpack_apply_message
from session import Session, Message
from zmqshell import ZMQInteractiveShell


#-----------------------------------------------------------------------------
# Main kernel class
#-----------------------------------------------------------------------------

class Kernel(Configurable):

    #---------------------------------------------------------------------------
    # Kernel interface
    #---------------------------------------------------------------------------

    # attribute to override with a GUI
    eventloop = Any(None)
    def _eventloop_changed(self, name, old, new):
        """schedule call to eventloop from IOLoop"""
        loop = ioloop.IOLoop.instance()
        loop.add_timeout(time.time()+0.1, self.enter_eventloop)

    shell = Instance('IPython.core.interactiveshell.InteractiveShellABC')
    session = Instance(Session)
    profile_dir = Instance('IPython.core.profiledir.ProfileDir')
    shell_streams = List()
    control_stream = Instance(ZMQStream)
    iopub_socket = Instance(zmq.Socket)
    stdin_socket = Instance(zmq.Socket)
    log = Instance(logging.Logger)
    
    user_module = Any()
    def _user_module_changed(self, name, old, new):
        if self.shell is not None:
            self.shell.user_module = new
    
    user_ns = Dict(default_value=None)
    def _user_ns_changed(self, name, old, new):
        if self.shell is not None:
            self.shell.user_ns = new
            self.shell.init_user_ns()

    # identities:
    int_id = Integer(-1)
    ident = Unicode()

    def _ident_default(self):
        return unicode(uuid.uuid4())


    # Private interface
    
    # Time to sleep after flushing the stdout/err buffers in each execute
    # cycle.  While this introduces a hard limit on the minimal latency of the
    # execute cycle, it helps prevent output synchronization problems for
    # clients.
    # Units are in seconds.  The minimum zmq latency on local host is probably
    # ~150 microseconds, set this to 500us for now.  We may need to increase it
    # a little if it's not enough after more interactive testing.
    _execute_sleep = Float(0.0005, config=True)

    # Frequency of the kernel's event loop.
    # Units are in seconds, kernel subclasses for GUI toolkits may need to
    # adapt to milliseconds.
    _poll_interval = Float(0.05, config=True)

    # If the shutdown was requested over the network, we leave here the
    # necessary reply message so it can be sent by our registered atexit
    # handler.  This ensures that the reply is only sent to clients truly at
    # the end of our shutdown process (which happens after the underlying
    # IPython shell's own shutdown).
    _shutdown_message = None

    # This is a dict of port number that the kernel is listening on. It is set
    # by record_ports and used by connect_request.
    _recorded_ports = Dict()
    
    # set of aborted msg_ids
    aborted = Set()


    def __init__(self, **kwargs):
        super(Kernel, self).__init__(**kwargs)

        # Initialize the InteractiveShell subclass
        self.shell = ZMQInteractiveShell.instance(config=self.config,
            profile_dir = self.profile_dir,
            user_module = self.user_module,
            user_ns     = self.user_ns,
        )
        self.shell.displayhook.session = self.session
        self.shell.displayhook.pub_socket = self.iopub_socket
        self.shell.displayhook.topic = self._topic('pyout')
        self.shell.display_pub.session = self.session
        self.shell.display_pub.pub_socket = self.iopub_socket

        # TMP - hack while developing
        self.shell._reply_content = None

        # Build dict of handlers for message types
        msg_types = [ 'execute_request', 'complete_request',
                      'object_info_request', 'history_request',
                      'connect_request', 'shutdown_request',
                      'apply_request',
                    ]
        self.shell_handlers = {}
        for msg_type in msg_types:
            self.shell_handlers[msg_type] = getattr(self, msg_type)
        
        control_msg_types = msg_types + [ 'clear_request', 'abort_request' ]
        self.control_handlers = {}
        for msg_type in control_msg_types:
            self.control_handlers[msg_type] = getattr(self, msg_type)

    def dispatch_control(self, msg):
        """dispatch control requests"""
        idents,msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.unserialize(msg, content=True, copy=False)
        except:
            self.log.error("Invalid Control Message", exc_info=True)
            return

        self.log.debug("Control received: %s", msg)

        header = msg['header']
        msg_id = header['msg_id']
        msg_type = header['msg_type']

        handler = self.control_handlers.get(msg_type, None)
        if handler is None:
            self.log.error("UNKNOWN CONTROL MESSAGE TYPE: %r", msg_type)
        else:
            try:
                handler(self.control_stream, idents, msg)
            except Exception:
                self.log.error("Exception in control handler:", exc_info=True)
    
    def dispatch_shell(self, stream, msg):
        """dispatch shell requests"""
        # flush control requests first
        if self.control_stream:
            self.control_stream.flush()
        
        idents,msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.unserialize(msg, content=True, copy=False)
        except:
            self.log.error("Invalid Message", exc_info=True)
            return

        header = msg['header']
        msg_id = header['msg_id']
        msg_type = msg['header']['msg_type']
        
        # Print some info about this message and leave a '--->' marker, so it's
        # easier to trace visually the message chain when debugging.  Each
        # handler prints its message at the end.
        self.log.debug('\n*** MESSAGE TYPE:%s***', msg_type)
        self.log.debug('   Content: %s\n   --->\n   ', msg['content'])

        if msg_id in self.aborted:
            self.aborted.remove(msg_id)
            # is it safe to assume a msg_id will not be resubmitted?
            reply_type = msg_type.split('_')[0] + '_reply'
            status = {'status' : 'aborted'}
            sub = {'engine' : self.ident}
            sub.update(status)
            reply_msg = self.session.send(stream, reply_type, subheader=sub,
                        content=status, parent=msg, ident=idents)
            return
        
        handler = self.shell_handlers.get(msg_type, None)
        if handler is None:
            self.log.error("UNKNOWN MESSAGE TYPE: %r", msg_type)
        else:
            # ensure default_int_handler during handler call
            sig = signal(SIGINT, default_int_handler)
            try:
                handler(stream, idents, msg)
            except Exception:
                self.log.error("Exception in message handler:", exc_info=True)
            finally:
                signal(SIGINT, sig)
    
    def enter_eventloop(self):
        """enter eventloop"""
        self.log.info("entering eventloop")
        # restore default_int_handler
        signal(SIGINT, default_int_handler)
        while self.eventloop is not None:
            try:
                self.eventloop(self)
            except KeyboardInterrupt:
                # Ctrl-C shouldn't crash the kernel
                self.log.error("KeyboardInterrupt caught in kernel")
                continue
            else:
                # eventloop exited cleanly, this means we should stop (right?)
                self.eventloop = None
                break
        self.log.info("exiting eventloop")
        # if eventloop exits, IOLoop should stop
        ioloop.IOLoop.instance().stop()

    def start(self):
        """register dispatchers for streams"""
        self.shell.exit_now = False
        if self.control_stream:
            self.control_stream.on_recv(self.dispatch_control, copy=False)

        def make_dispatcher(stream):
            def dispatcher(msg):
                return self.dispatch_shell(stream, msg)
            return dispatcher

        for s in self.shell_streams:
            s.on_recv(make_dispatcher(s), copy=False)
    
    def do_one_iteration(self):
        """step eventloop just once"""
        if self.control_stream:
            self.control_stream.flush()
        for stream in self.shell_streams:
            # handle at most one request per iteration
            stream.flush(zmq.POLLIN, 1)
            stream.flush(zmq.POLLOUT)


    def record_ports(self, ports):
        """Record the ports that this kernel is using.

        The creator of the Kernel instance must call this methods if they
        want the :meth:`connect_request` method to return the port numbers.
        """
        self._recorded_ports = ports

    #---------------------------------------------------------------------------
    # Kernel request handlers
    #---------------------------------------------------------------------------
    
    def _make_subheader(self):
        """init subheader dict, for execute/apply_reply"""
        return {
            'dependencies_met' : True,
            'engine' : self.ident,
            'started': datetime.now(),
        }
    
    def _publish_pyin(self, code, parent, execution_count):
        """Publish the code request on the pyin stream."""

        self.session.send(self.iopub_socket, u'pyin',
                            {u'code':code, u'execution_count': execution_count},
                            parent=parent, ident=self._topic('pyin')
        )
    
    def _publish_status(self, status, parent=None):
        """send status (busy/idle) on IOPub"""
        self.session.send(self.iopub_socket,
                          u'status',
                          {u'execution_state': status},
                          parent=parent,
                          ident=self._topic('status'),
                          )
        

    def execute_request(self, stream, ident, parent):
        """handle an execute_request"""
        
        self._publish_status(u'busy', parent)
        
        try:
            content = parent[u'content']
            code = content[u'code']
            silent = content[u'silent']
        except:
            self.log.error("Got bad msg: ")
            self.log.error("%s", parent)
            return
        
        sub = self._make_subheader()

        shell = self.shell # we'll need this a lot here

        # Replace raw_input. Note that is not sufficient to replace
        # raw_input in the user namespace.
        if content.get('allow_stdin', False):
            raw_input = lambda prompt='': self._raw_input(prompt, ident, parent)
        else:
            raw_input = lambda prompt='' : self._no_raw_input()

        if py3compat.PY3:
            __builtin__.input = raw_input
        else:
            __builtin__.raw_input = raw_input

        # Set the parent message of the display hook and out streams.
        shell.displayhook.set_parent(parent)
        shell.display_pub.set_parent(parent)
        try:
            sys.stdout.set_parent(parent)
        except AttributeError:
            pass
        try:
            sys.stderr.set_parent(parent)
        except AttributeError:
            pass

        # Re-broadcast our input for the benefit of listening clients, and
        # start computing output
        if not silent:
            self._publish_pyin(code, parent, shell.execution_count)

        reply_content = {}
        try:
            # FIXME: the shell calls the exception handler itself.
            shell.run_cell(code, store_history=not silent, silent=silent)
        except:
            status = u'error'
            # FIXME: this code right now isn't being used yet by default,
            # because the run_cell() call above directly fires off exception
            # reporting.  This code, therefore, is only active in the scenario
            # where runlines itself has an unhandled exception.  We need to
            # uniformize this, for all exception construction to come from a
            # single location in the codbase.
            etype, evalue, tb = sys.exc_info()
            tb_list = traceback.format_exception(etype, evalue, tb)
            reply_content.update(shell._showtraceback(etype, evalue, tb_list))
        else:
            status = u'ok'

        reply_content[u'status'] = status

        # Return the execution counter so clients can display prompts
        reply_content['execution_count'] = shell.execution_count - 1

        # FIXME - fish exception info out of shell, possibly left there by
        # runlines.  We'll need to clean up this logic later.
        if shell._reply_content is not None:
            reply_content.update(shell._reply_content)
            e_info = dict(engine_uuid=self.ident, engine_id=self.int_id, method='execute')
            reply_content['engine_info'] = e_info
            # reset after use
            shell._reply_content = None

        # At this point, we can tell whether the main code execution succeeded
        # or not.  If it did, we proceed to evaluate user_variables/expressions
        if reply_content['status'] == 'ok':
            reply_content[u'user_variables'] = \
                         shell.user_variables(content.get(u'user_variables', []))
            reply_content[u'user_expressions'] = \
                         shell.user_expressions(content.get(u'user_expressions', {}))
        else:
            # If there was an error, don't even try to compute variables or
            # expressions
            reply_content[u'user_variables'] = {}
            reply_content[u'user_expressions'] = {}

        # Payloads should be retrieved regardless of outcome, so we can both
        # recover partial output (that could have been generated early in a
        # block, before an error) and clear the payload system always.
        reply_content[u'payload'] = shell.payload_manager.read_payload()
        # Be agressive about clearing the payload because we don't want
        # it to sit in memory until the next execute_request comes in.
        shell.payload_manager.clear_payload()

        # Flush output before sending the reply.
        sys.stdout.flush()
        sys.stderr.flush()
        # FIXME: on rare occasions, the flush doesn't seem to make it to the
        # clients... This seems to mitigate the problem, but we definitely need
        # to better understand what's going on.
        if self._execute_sleep:
            time.sleep(self._execute_sleep)

        # Send the reply.
        reply_content = json_clean(reply_content)
        
        sub['status'] = reply_content['status']
        if reply_content['status'] == 'error' and \
                        reply_content['ename'] == 'UnmetDependency':
                sub['dependencies_met'] = False

        reply_msg = self.session.send(stream, u'execute_reply',
                                      reply_content, parent, subheader=sub,
                                      ident=ident)
        
        self.log.debug("%s", reply_msg)

        if not silent and reply_msg['content']['status'] == u'error':
            self._abort_queues()

        self._publish_status(u'idle', parent)

    def complete_request(self, stream, ident, parent):
        txt, matches = self._complete(parent)
        matches = {'matches' : matches,
                   'matched_text' : txt,
                   'status' : 'ok'}
        matches = json_clean(matches)
        completion_msg = self.session.send(stream, 'complete_reply',
                                           matches, parent, ident)
        self.log.debug("%s", completion_msg)

    def object_info_request(self, stream, ident, parent):
        content = parent['content']
        object_info = self.shell.object_inspect(content['oname'],
                        detail_level = content.get('detail_level', 0)
        )
        # Before we send this object over, we scrub it for JSON usage
        oinfo = json_clean(object_info)
        msg = self.session.send(stream, 'object_info_reply',
                                oinfo, parent, ident)
        self.log.debug("%s", msg)

    def history_request(self, stream, ident, parent):
        # We need to pull these out, as passing **kwargs doesn't work with
        # unicode keys before Python 2.6.5.
        hist_access_type = parent['content']['hist_access_type']
        raw = parent['content']['raw']
        output = parent['content']['output']
        if hist_access_type == 'tail':
            n = parent['content']['n']
            hist = self.shell.history_manager.get_tail(n, raw=raw, output=output,
                                                            include_latest=True)

        elif hist_access_type == 'range':
            session = parent['content']['session']
            start = parent['content']['start']
            stop = parent['content']['stop']
            hist = self.shell.history_manager.get_range(session, start, stop,
                                                        raw=raw, output=output)

        elif hist_access_type == 'search':
            pattern = parent['content']['pattern']
            hist = self.shell.history_manager.search(pattern, raw=raw,
                                                     output=output) 

        else:
            hist = []
        hist = list(hist)
        content = {'history' : hist}
        content = json_clean(content)
        msg = self.session.send(stream, 'history_reply',
                                content, parent, ident)
        self.log.debug("Sending history reply with %i entries", len(hist))

    def connect_request(self, stream, ident, parent):
        if self._recorded_ports is not None:
            content = self._recorded_ports.copy()
        else:
            content = {}
        msg = self.session.send(stream, 'connect_reply',
                                content, parent, ident)
        self.log.debug("%s", msg)

    def shutdown_request(self, stream, ident, parent):
        self.shell.exit_now = True
        content = dict(status='ok')
        content.update(parent['content'])
        self.session.send(stream, u'shutdown_reply', content, parent, ident=ident)
        # same content, but different msg_id for broadcasting on IOPub
        self._shutdown_message = self.session.msg(u'shutdown_reply',
                                                  content, parent
        )

        self._at_shutdown()
        # call sys.exit after a short delay
        loop = ioloop.IOLoop.instance()
        loop.add_timeout(time.time()+0.1, loop.stop)

    #---------------------------------------------------------------------------
    # Engine methods
    #---------------------------------------------------------------------------

    def apply_request(self, stream, ident, parent):
        try:
            content = parent[u'content']
            bufs = parent[u'buffers']
            msg_id = parent['header']['msg_id']
        except:
            self.log.error("Got bad msg: %s", parent, exc_info=True)
            return

        self._publish_status(u'busy', parent)

        # Set the parent message of the display hook and out streams.
        shell = self.shell
        shell.displayhook.set_parent(parent)
        shell.display_pub.set_parent(parent)
        try:
            sys.stdout.set_parent(parent)
        except AttributeError:
            pass
        try:
            sys.stderr.set_parent(parent)
        except AttributeError:
            pass

        # pyin_msg = self.session.msg(u'pyin',{u'code':code}, parent=parent)
        # self.iopub_socket.send(pyin_msg)
        # self.session.send(self.iopub_socket, u'pyin', {u'code':code},parent=parent)
        sub = self._make_subheader()
        try:
            working = shell.user_ns

            prefix = "_"+str(msg_id).replace("-","")+"_"

            f,args,kwargs = unpack_apply_message(bufs, working, copy=False)

            fname = getattr(f, '__name__', 'f')

            fname = prefix+"f"
            argname = prefix+"args"
            kwargname = prefix+"kwargs"
            resultname = prefix+"result"

            ns = { fname : f, argname : args, kwargname : kwargs , resultname : None }
            # print ns
            working.update(ns)
            code = "%s = %s(*%s,**%s)" % (resultname, fname, argname, kwargname)
            try:
                exec code in shell.user_global_ns, shell.user_ns
                result = working.get(resultname)
            finally:
                for key in ns.iterkeys():
                    working.pop(key)

            packed_result,buf = serialize_object(result)
            result_buf = [packed_result]+buf
        except:
            # invoke IPython traceback formatting
            shell.showtraceback()
            # FIXME - fish exception info out of shell, possibly left there by
            # run_code.  We'll need to clean up this logic later.
            reply_content = {}
            if shell._reply_content is not None:
                reply_content.update(shell._reply_content)
                e_info = dict(engine_uuid=self.ident, engine_id=self.int_id, method='apply')
                reply_content['engine_info'] = e_info
                # reset after use
                shell._reply_content = None
            
            self.session.send(self.iopub_socket, u'pyerr', reply_content, parent=parent,
                                ident=self._topic('pyerr'))
            result_buf = []

            if reply_content['ename'] == 'UnmetDependency':
                sub['dependencies_met'] = False
        else:
            reply_content = {'status' : 'ok'}

        # put 'ok'/'error' status in header, for scheduler introspection:
        sub['status'] = reply_content['status']

        # flush i/o
        sys.stdout.flush()
        sys.stderr.flush()
        
        reply_msg = self.session.send(stream, u'apply_reply', reply_content,
                    parent=parent, ident=ident,buffers=result_buf, subheader=sub)

        self._publish_status(u'idle', parent)

    #---------------------------------------------------------------------------
    # Control messages
    #---------------------------------------------------------------------------

    def abort_request(self, stream, ident, parent):
        """abort a specifig msg by id"""
        msg_ids = parent['content'].get('msg_ids', None)
        if isinstance(msg_ids, basestring):
            msg_ids = [msg_ids]
        if not msg_ids:
            self.abort_queues()
        for mid in msg_ids:
            self.aborted.add(str(mid))

        content = dict(status='ok')
        reply_msg = self.session.send(stream, 'abort_reply', content=content,
                parent=parent, ident=ident)
        self.log.debug("%s", reply_msg)

    def clear_request(self, stream, idents, parent):
        """Clear our namespace."""
        self.shell.reset(False)
        msg = self.session.send(stream, 'clear_reply', ident=idents, parent=parent,
                content = dict(status='ok'))


    #---------------------------------------------------------------------------
    # Protected interface
    #---------------------------------------------------------------------------


    def _wrap_exception(self, method=None):
        # import here, because _wrap_exception is only used in parallel,
        # and parallel has higher min pyzmq version
        from IPython.parallel.error import wrap_exception
        e_info = dict(engine_uuid=self.ident, engine_id=self.int_id, method=method)
        content = wrap_exception(e_info)
        return content

    def _topic(self, topic):
        """prefixed topic for IOPub messages"""
        if self.int_id >= 0:
            base = "engine.%i" % self.int_id
        else:
            base = "kernel.%s" % self.ident
        
        return py3compat.cast_bytes("%s.%s" % (base, topic))
    
    def _abort_queues(self):
        for stream in self.shell_streams:
            if stream:
                self._abort_queue(stream)

    def _abort_queue(self, stream):
        poller = zmq.Poller()
        poller.register(stream.socket, zmq.POLLIN)
        while True:
            idents,msg = self.session.recv(stream, zmq.NOBLOCK, content=True)
            if msg is None:
                return

            self.log.info("Aborting:")
            self.log.info("%s", msg)
            msg_type = msg['header']['msg_type']
            reply_type = msg_type.split('_')[0] + '_reply'

            status = {'status' : 'aborted'}
            sub = {'engine' : self.ident}
            sub.update(status)
            reply_msg = self.session.send(stream, reply_type, subheader=sub,
                        content=status, parent=msg, ident=idents)
            self.log.debug("%s", reply_msg)
            # We need to wait a bit for requests to come in. This can probably
            # be set shorter for true asynchronous clients.
            poller.poll(50)


    def _no_raw_input(self):
        """Raise StdinNotImplentedError if active frontend doesn't support
        stdin."""
        raise StdinNotImplementedError("raw_input was called, but this "
                                       "frontend does not support stdin.") 
        
    def _raw_input(self, prompt, ident, parent):
        # Flush output before making the request.
        sys.stderr.flush()
        sys.stdout.flush()

        # Send the input request.
        content = json_clean(dict(prompt=prompt))
        self.session.send(self.stdin_socket, u'input_request', content, parent,
                          ident=ident)

        # Await a response.
        while True:
            try:
                ident, reply = self.session.recv(self.stdin_socket, 0)
            except Exception:
                self.log.warn("Invalid Message:", exc_info=True)
            else:
                break
        try:
            value = reply['content']['value']
        except:
            self.log.error("Got bad raw_input reply: ")
            self.log.error("%s", parent)
            value = ''
        if value == '\x04':
            # EOF
            raise EOFError
        return value

    def _complete(self, msg):
        c = msg['content']
        try:
            cpos = int(c['cursor_pos'])
        except:
            # If we don't get something that we can convert to an integer, at
            # least attempt the completion guessing the cursor is at the end of
            # the text, if there's any, and otherwise of the line
            cpos = len(c['text'])
            if cpos==0:
                cpos = len(c['line'])
        return self.shell.complete(c['text'], c['line'], cpos)

    def _object_info(self, context):
        symbol, leftover = self._symbol_from_context(context)
        if symbol is not None and not leftover:
            doc = getattr(symbol, '__doc__', '')
        else:
            doc = ''
        object_info = dict(docstring = doc)
        return object_info

    def _symbol_from_context(self, context):
        if not context:
            return None, context

        base_symbol_string = context[0]
        symbol = self.shell.user_ns.get(base_symbol_string, None)
        if symbol is None:
            symbol = __builtin__.__dict__.get(base_symbol_string, None)
        if symbol is None:
            return None, context

        context = context[1:]
        for i, name in enumerate(context):
            new_symbol = getattr(symbol, name, None)
            if new_symbol is None:
                return symbol, context[i:]
            else:
                symbol = new_symbol

        return symbol, []

    def _at_shutdown(self):
        """Actions taken at shutdown by the kernel, called by python's atexit.
        """
        # io.rprint("Kernel at_shutdown") # dbg
        if self._shutdown_message is not None:
            self.session.send(self.iopub_socket, self._shutdown_message, ident=self._topic('shutdown'))
            self.log.debug("%s", self._shutdown_message)
        [ s.flush(zmq.POLLOUT) for s in self.shell_streams ]

#-----------------------------------------------------------------------------
# Aliases and Flags for the IPKernelApp
#-----------------------------------------------------------------------------

flags = dict(kernel_flags)
flags.update(shell_flags)

addflag = lambda *args: flags.update(boolean_flag(*args))

flags['pylab'] = (
    {'IPKernelApp' : {'pylab' : 'auto'}},
    """Pre-load matplotlib and numpy for interactive use with
    the default matplotlib backend."""
)

aliases = dict(kernel_aliases)
aliases.update(shell_aliases)

#-----------------------------------------------------------------------------
# The IPKernelApp class
#-----------------------------------------------------------------------------

class IPKernelApp(KernelApp, InteractiveShellApp):
    name = 'ipkernel'

    aliases = Dict(aliases)
    flags = Dict(flags)
    classes = [Kernel, ZMQInteractiveShell, ProfileDir, Session]

    @catch_config_error
    def initialize(self, argv=None):
        super(IPKernelApp, self).initialize(argv)
        self.init_path()
        self.init_shell()
        self.init_gui_pylab()
        self.init_extensions()
        self.init_code()

    def init_kernel(self):
        
        shell_stream = ZMQStream(self.shell_socket)

        kernel = Kernel(config=self.config, session=self.session,
                                shell_streams=[shell_stream],
                                iopub_socket=self.iopub_socket,
                                stdin_socket=self.stdin_socket,
                                log=self.log,
                                profile_dir=self.profile_dir,
        )
        self.kernel = kernel
        kernel.record_ports(self.ports)
        shell = kernel.shell

    def init_gui_pylab(self):
        """Enable GUI event loop integration, taking pylab into account."""

        # Provide a wrapper for :meth:`InteractiveShellApp.init_gui_pylab`
        # to ensure that any exception is printed straight to stderr.
        # Normally _showtraceback associates the reply with an execution,
        # which means frontends will never draw it, as this exception
        # is not associated with any execute request.

        shell = self.shell
        _showtraceback = shell._showtraceback
        try:
            # replace pyerr-sending traceback with stderr
            def print_tb(etype, evalue, stb):
                print ("GUI event loop or pylab initialization failed",
                       file=io.stderr)
                print (shell.InteractiveTB.stb2text(stb), file=io.stderr)
            shell._showtraceback = print_tb
            InteractiveShellApp.init_gui_pylab(self)
        finally:
            shell._showtraceback = _showtraceback

    def init_shell(self):
        self.shell = self.kernel.shell
        self.shell.configurables.append(self)


#-----------------------------------------------------------------------------
# Kernel main and launch functions
#-----------------------------------------------------------------------------

def launch_kernel(*args, **kwargs):
    """Launches a localhost IPython kernel, binding to the specified ports.

    This function simply calls entry_point.base_launch_kernel with the right
    first command to start an ipkernel.  See base_launch_kernel for arguments.

    Returns
    -------
    A tuple of form:
        (kernel_process, shell_port, iopub_port, stdin_port, hb_port)
    where kernel_process is a Popen object and the ports are integers.
    """
    return base_launch_kernel('from IPython.zmq.ipkernel import main; main()',
                              *args, **kwargs)


def embed_kernel(module=None, local_ns=None, **kwargs):
    """Embed and start an IPython kernel in a given scope.
    
    Parameters
    ----------
    module : ModuleType, optional
        The module to load into IPython globals (default: caller)
    local_ns : dict, optional
        The namespace to load into IPython user namespace (default: caller)
    
    kwargs : various, optional
        Further keyword args are relayed to the KernelApp constructor,
        allowing configuration of the Kernel.  Will only have an effect
        on the first embed_kernel call for a given process.
    
    """
    # get the app if it exists, or set it up if it doesn't
    if IPKernelApp.initialized():
        app = IPKernelApp.instance()
    else:
        app = IPKernelApp.instance(**kwargs)
        app.initialize([])
        # Undo unnecessary sys module mangling from init_sys_modules.
        # This would not be necessary if we could prevent it
        # in the first place by using a different InteractiveShell
        # subclass, as in the regular embed case.
        main = app.kernel.shell._orig_sys_modules_main_mod
        if main is not None:
            sys.modules[app.kernel.shell._orig_sys_modules_main_name] = main

    # load the calling scope if not given
    (caller_module, caller_locals) = extract_module_locals(1)
    if module is None:
        module = caller_module
    if local_ns is None:
        local_ns = caller_locals
    
    app.kernel.user_module = module
    app.kernel.user_ns = local_ns
    app.shell.set_completer_frame()
    app.start()

def main():
    """Run an IPKernel as an application"""
    app = IPKernelApp.instance()
    app.initialize()
    app.start()


if __name__ == '__main__':
    main()
