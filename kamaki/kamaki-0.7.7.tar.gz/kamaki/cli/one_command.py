# Copyright 2012-2013 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.command

from logging import getLogger

from kamaki.cli import get_command_group, set_command_params
from kamaki.cli import print_subcommands_help, exec_cmd, update_parser_help
from kamaki.cli import _groups_help, _load_spec_module


kloger = getLogger('kamaki')


def _get_cmd_tree_from_spec(spec, cmd_tree_list):
    for tree in cmd_tree_list:
        if tree.name == spec:
            return tree
    return None


def _get_best_match_from_cmd_tree(cmd_tree, unparsed):
    matched = [term for term in unparsed if not term.startswith('-')]
    while matched:
        try:
            return cmd_tree.get_command('_'.join(matched))
        except KeyError:
            matched = matched[:-1]
    return None


def run(parser, _help):
    group = get_command_group(list(parser.unparsed), parser.arguments)
    if not group:
        parser.parser.print_help()
        _groups_help(parser.arguments)
        exit(0)

    nonargs = [term for term in parser.unparsed if not term.startswith('-')]
    set_command_params(nonargs)

    global _best_match
    _best_match = []

    spec_module = _load_spec_module(group, parser.arguments, '_commands')

    cmd_tree = _get_cmd_tree_from_spec(group, spec_module._commands)

    if _best_match:
        cmd = cmd_tree.get_command('_'.join(_best_match))
    else:
        cmd = _get_best_match_from_cmd_tree(cmd_tree, parser.unparsed)
        _best_match = cmd.path.split('_')
    if cmd is None:
        kloger.info(
            'Unexpected error: failed to load command (-d for details)')
        exit(1)

    update_parser_help(parser, cmd)

    if _help or not cmd.is_command:
        parser.parser.print_help()
        print_subcommands_help(cmd)
        exit(0)

    cls = cmd.get_class()
    executable = cls(parser.arguments)
    parser.update_arguments(executable.arguments)
    #parsed, unparsed = parse_known_args(parser, executable.arguments)
    for term in _best_match:
            parser.unparsed.remove(term)
    exec_cmd(executable, parser.unparsed, parser.parser.print_help)
