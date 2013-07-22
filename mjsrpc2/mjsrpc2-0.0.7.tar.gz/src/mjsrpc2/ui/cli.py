'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''


import sys
import os

import logging
import urlparse
import shlex

from yaml import safe_dump

from clicmd import BaseCmd, opts, option, FriendlyArgumentParser, ParserError


class ProxyMixer(BaseCmd):
    def __init__(self, name, proxy_obj):
        self.name = name
        BaseCmd.__init__(self)
        self._proxy_obj = proxy_obj
        self.log.debug("Adding methods")
        self.add_methods(proxy_obj)

    def add_methods(self, proxy):
        methods = proxy.rpc_methods()
        for meth in methods.keys():
            desc = methods[meth]
            if desc['type'] == "instance":
                inner_proxy = ProxyMixer(meth, proxy.get_proxy(meth))
                self.add_command(meth, inner_proxy)
            else:
                wrapper = self.__get_wrapper(meth, desc, proxy)
                help_wrapper = self.__get_help_wrapper(meth, desc, proxy, wrapper)
                mname = "do_%s" % meth
                hname = "help_%s" % meth
                self.log.debug("Registering wrapper methods %s(%s) and %s(%s)" % (mname, wrapper, hname, help_wrapper))
                setattr(self, str(mname), wrapper)
                setattr(self, str(hname), help_wrapper)

    def __get_help_wrapper(self, name, info, proxy, func = None):
        def __help_rpc_wrapper(*args, **kw):
            no_doc_string = 'No documentation associated with %s' % name
            self.log.debug("Display documentation for %s" % name)
            doc = info.get('documentation', no_doc_string)
            if doc is None:
                doc = no_doc_string
            sys.stdout.write(doc + "\n")
            if func is not None:
                func._arg_parser.print_help()
        return __help_rpc_wrapper

    def __get_wrapper(self, name, info, proxy):
        parser = FriendlyArgumentParser(prog = name)
        if 'argument_specification' in info and info['argument_specification']:
            remote_args = info['argument_specification']
            self.__setup_arguments(parser, remote_args)

        def __rpc_wrapper(inst, *ap, **kw):
            supplied_args = shlex.split(inst)
            try:
                args = parser.parse_args(supplied_args)
            except ParserError, e:
                return
            args = vars(args)
            self.log.debug("Invoking effective method %s", name)
            hndl = getattr(proxy, name)
            result = hndl(*ap, **args)
            self.pretty_print_results(result)

        __rpc_wrapper.__doc__ = getattr(info, 'documentation', None)
        __rpc_wrapper._arg_parser = parser
        return __rpc_wrapper

    def __setup_arguments(self, parser, remote_args):
        for arg, arg_spec in remote_args.items():
            arg_name = "--%s" % arg
            kind = arg_spec.get('kind')
            if kind == 'str' or kind == 'unicode' or kind == 'basestring':
                type_spec = unicode
            elif kind == 'int':
                type_spec = int
            elif kind == 'float':
                type_spec = float
            elif kind == 'bool':
                type_spec = bool
            else:
                type_spec = unicode
            documentation = arg_spec.get('documentation', None)
            parser.add_argument(arg_name, type = type_spec, help = documentation)

    def pretty_print_results(self, data):
        sys.stdout.write(safe_dump(data, default_flow_style = False))


class CliHandler(BaseCmd):
    def __init__(self, name = "cli"):
        self.name = name
        BaseCmd.__init__(self)
        self.log = logging.getLogger("CliHandler")

    @option('--uri', type = str, default = None, help = 'The URL of the server')
    @opts
    def do_connect(self, args):
        from mjsrpc2 import RPCProxy
        if args.uri is None:
            self.log.critical("No server specified")
            return
        self.log.debug("URL is: %s", args.uri)
        url = urlparse.urlparse(args.uri)
        proxy = None
        if url.scheme == 'unix':
            from mjsrpc2 import UnixStreamTransport
            transport = UnixStreamTransport(url)
            proxy = RPCProxy(transport)
        if url.scheme == 'http':
            from mjsrpc2 import HTTPTransport
            transport = HTTPTransport(url)
            proxy = RPCProxy(transport)
        else:
            self.log.error("Unsupport scheme %s", url.scheme)

        if proxy is None:
            self.log.critical("Could not create proxy! ")
            return
        mixer = ProxyMixer("mde", proxy)
        self.add_command("mde", mixer)

def loadCfg(target_cmd, extra = []):
    log = logging.getLogger("configuration")
    fileLoaded = False
    configs = extra
    commands = []
    for cfg in configs:
        if not os.path.isfile(cfg):
            log.debug("Can't load file %s", cfg)
            continue

        try:
            fd = open(cfg, "r")
            with fd:
                for line in fd.readlines():
                    ln = line.strip()
                    if len(ln) == 0 or ln.startswith("#"):
                        continue
                    commands.append(line)
            fileLoaded = True
        except IOError:
            log.exception("Could not load file")

    for command in commands:
        target_cmd.onecmd(command)

    if not fileLoaded:
        log.error("No config file could be loaded")
