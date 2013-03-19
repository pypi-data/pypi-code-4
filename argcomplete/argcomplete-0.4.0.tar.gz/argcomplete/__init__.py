# Copyright 2012-2013, Andrey Kislyuk and argcomplete contributors.
# Licensed under the Apache License. See https://github.com/kislyuk/argcomplete for more info.

from __future__ import print_function

import os, sys, argparse, shlex, contextlib, subprocess, locale, re

try:
    basestring
except NameError:
    basestring = str

_DEBUG = True if '_ARC_DEBUG' in os.environ else False

try:
    debug_stream = os.fdopen(9, 'w')
except:
    debug_stream = sys.stderr

def warn(*args):
    print("\n", file=debug_stream, *args)

def debug(*args):
    if _DEBUG:
        print(file=debug_stream, *args)

BASH_FILE_COMPLETION_FALLBACK = 79
BASH_DIR_COMPLETION_FALLBACK = 80

safe_actions = (argparse._StoreAction,
                argparse._StoreConstAction,
                argparse._StoreTrueAction,
                argparse._StoreFalseAction,
                argparse._AppendAction,
                argparse._AppendConstAction,
                argparse._CountAction)

from . import completers
from .my_argparse import IntrospectiveArgumentParser

@contextlib.contextmanager
def mute_stdout():
    stdout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    yield
    sys.stdout = stdout

@contextlib.contextmanager
def mute_stderr():
    stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    yield
    sys.stderr.close()
    sys.stderr = stderr

def action_is_satisfied(action):
    num_consumed_args = getattr(action, 'num_consumed_args', 0)
    if action.nargs == argparse.ONE_OR_MORE and num_consumed_args < 1:
        return False
    else:
        try:
            return num_consumed_args == action.nargs
        except:
            return True

class ArgcompleteException(Exception):
    pass

def split_line(line, point):
    lexer = shlex.shlex(line)
    lexer.whitespace_split = True
    words = []

    def split_word(word):
        # TODO: make this less ugly
        point_in_word = len(word) + point - lexer.instream.tell()
        if isinstance(lexer.state, basestring) and lexer.state in lexer.whitespace:
            point_in_word += 1
        if point_in_word > len(word):
            debug("In trailing whitespace")
            words.append(word)
            word = ''
        prefix, suffix = word[:point_in_word], word[point_in_word:]
        return prefix, suffix, words

    while True:
        try:
            word = lexer.get_token()
            if word == lexer.eof:
                # TODO: check if this is ever unsafe
                # raise ArgcompleteException("Unexpected end of input")
                return "", "", words
            if lexer.instream.tell() >= point:
                debug("word", word, "split")
                return split_word(word)
            words.append(word)
        except ValueError:
            debug("word", lexer.token, "split (lexer stopped)")
            if lexer.instream.tell() >= point:
                return split_word(lexer.token)
            else:
                raise ArgcompleteException("unexpected state? TODO")

def autocomplete(argument_parser, always_complete_options=True, exit_method=os._exit, output_stream=None):
    '''
    :param argument_parser: The argument parser to autocomplete on
    :type argument_parser: :class:`argparse.ArgumentParser`
    :param always_complete_options: Whether or not to autocomplete options even if an option string opening character (normally ``-``) has not been entered
    :type always_complete_options: boolean
    :param exit_method: Method used to stop the program after printing completions. Defaults to :meth:`os._exit`. If you want to perform a normal exit that calls exit handlers, use :meth:`sys.exit`.
    :type exit_method: method

    Produces tab completions for ``argument_parser``. See module docs for more info.

    Argcomplete only executes actions if their class is known not to have side effects. Custom action classes can be
    added to argparse.safe_actions, if their values are wanted in the ``parsed_args`` completer argument, or their
    execution is otherwise desirable.
    '''

    if '_ARGCOMPLETE' not in os.environ:
        # not an argument completion invocation
        return

    if output_stream is None:
        try:
            output_stream = os.fdopen(8, 'wb')
        except:
            debug("Unable to open fd 8 for writing, quitting")
            exit_method(1)

    # print >>debug_stream, ""
    # for v in 'COMP_CWORD', 'COMP_LINE', 'COMP_POINT', 'COMP_TYPE', 'COMP_KEY', 'COMP_WORDBREAKS', 'COMP_WORDS':
    #     print >>debug_stream, v, os.environ[v]

    ifs = os.environ.get('_ARGCOMPLETE_IFS', '\013')
    if len(ifs) != 1:
        debug("Invalid value for IFS, quitting".format(v=ifs))
        exit_method(1)

    comp_line = os.environ['COMP_LINE']
    comp_wordbreaks = os.environ['COMP_WORDBREAKS']
    comp_point = int(os.environ['COMP_POINT'])
    cword_prefix, cword_suffix, comp_words = split_line(comp_line, comp_point)
    if os.environ['_ARGCOMPLETE'] == "2": # Hook recognized the first word as the interpreter
        comp_words.pop(0)
    debug("\nPREFIX: '{p}'".format(p=cword_prefix), "\nSUFFIX: '{s}'".format(s=cword_suffix), "\nWORDS:", comp_words)

    active_parsers = [argument_parser]
    parsed_args = argparse.Namespace()
    visited_actions = []

    '''
    Since argparse doesn't support much introspection, we monkey-patch it to replace the parse_known_args method and
    all actions with hooks that tell us which action was last taken or about to be taken, and let us have the parser
    figure out which subparsers need to be activated (then recursively monkey-patch those).
    We save all active ArgumentParsers to extract all their possible option names later.
    '''
    def patchArgumentParser(parser):
        parser.__class__ = IntrospectiveArgumentParser
        for action in parser._actions:
            # TODO: accomplish this with super
            class IntrospectAction(action.__class__):
                def __call__(self, parser, namespace, values, option_string=None):
                    debug('Action stub called on', self)
                    debug('\targs:', parser, namespace, values, option_string)
                    debug('\torig class:', self._orig_class)
                    debug('\torig callable:', self._orig_callable)

                    visited_actions.append(self)

                    if self._orig_class == argparse._SubParsersAction:
                        debug('orig class is a subparsers action: patching and running it')
                        active_subparser = self._name_parser_map[values[0]]
                        patchArgumentParser(active_subparser)
                        active_parsers.append(active_subparser)
                        self._orig_callable(parser, namespace, values, option_string=option_string)
                    elif self._orig_class in safe_actions:
                        self._orig_callable(parser, namespace, values, option_string=option_string)
            if getattr(action, "_orig_class", None):
                raise ArgcompleteException("unexpected condition")
            action._orig_class = action.__class__
            action._orig_callable = action.__call__
            action.__class__ = IntrospectAction

    patchArgumentParser(argument_parser)

    try:
        debug("invoking parser with", comp_words[1:])
        with mute_stderr():
            a = argument_parser.parse_known_args(comp_words[1:], namespace=parsed_args)
        debug("parsed args:", a)
    except BaseException as e:
        debug("\nexception", type(e), str(e), "while parsing args")

    debug("Active parsers:", active_parsers)
    debug("Visited actions:", visited_actions)
    debug("Parse result namespace:", parsed_args)
    completions = []

    # Subcommand and options completion
    for parser in active_parsers:
        debug("Examining parser", parser)
        for action in parser._actions:
            debug("Examining action", action)
            if isinstance(action, argparse._SubParsersAction):
                subparser_activated = False
                for subparser in action._name_parser_map.values():
                    if subparser in active_parsers:
                        subparser_activated = True
                if subparser_activated:
                    # Parent parser completions are not valid in the subparser, so flush them
                    completions = []
                else:
                    completions += [subcmd for subcmd in action.choices.keys() if subcmd.startswith(cword_prefix)]
            elif always_complete_options or (len(cword_prefix) > 0 and cword_prefix[0] in parser.prefix_chars):
                completions += [option for option in action.option_strings if option.startswith(cword_prefix)]

        debug("Active actions (L={l}): {a}".format(l=len(parser.active_actions), a=parser.active_actions))

        for active_action in parser.active_actions:
            debug("Activating completion for", active_action, active_action._orig_class)
            #completer = getattr(active_action, 'completer', DefaultCompleter())
            completer = getattr(active_action, 'completer', None)

            if completer is None and active_action.choices is not None:
                if not isinstance(active_action, argparse._SubParsersAction):
                    completer = completers.ChoicesCompleter(active_action.choices)

            if completer:
                if len(active_action.option_strings) > 0: # only for optionals
                    if not action_is_satisfied(active_action):
                        # This means the current action will fail to parse if the word under the cursor is not given
                        # to it, so give it exclusive control over completions (flush previous completions)
                        debug("Resetting completions because", active_action, "is unsatisfied")
                        completions = []
                try:
                    completions += [c for c in completer(prefix=cword_prefix,
                                                         parser=parser,
                                                         action=active_action,
                                                         parsed_args=parsed_args) if c.startswith(cword_prefix)]
                except TypeError:
                    # If completer is not callable, try the readline completion protocol instead
                    debug("Could not call completer, trying readline protocol instead")
                    for i in range(9999):
                        next_completion = completer.complete(cword_prefix, i)
                        if next_completion is None:
                            break
                        if next_completion.startswith(cword_prefix):
                            completions.append(next_completion)
                debug("Completions:", completions)
            elif not isinstance(active_action, argparse._SubParsersAction):
                debug("Completer not available, falling back")
                try:
                    # TODO: what happens if completions contain newlines? How do I make compgen use IFS?
                    completions += subprocess.check_output(['bash', '-c', "compgen -A file -- '{p}'".format(p=cword_prefix)]).decode().splitlines()
                except subprocess.CalledProcessError:
                    pass

    # De-duplicate completions
    seen = set()
    completions = [c for c in completions if c not in seen and not seen.add(c)]

    # If cword_prefix contains a char present in COMP_WORDBREAKS, strip from each completion the portion of
    # cword_prefix up to the last such occurrence.
    cword_break_loc = -1
    for wordbreak_char in comp_wordbreaks:
        cword_break_loc = max(cword_break_loc, cword_prefix.rfind(wordbreak_char))
    if cword_break_loc != -1:
        completions = [c[cword_break_loc+1:] for c in completions]

    continuation_chars = '=/:'
    # If there's only one completion, and it doesn't end with a continuation char, add a space
    if len(completions) == 1 and completions[0][-1] not in continuation_chars:
        completions[0] += ' '

    # TODO: figure out the correct way to quote completions
    # print >>debug_stream, "\nReturning completions:", [pipes.quote(c) for c in completions]
    # print ifs.join([pipes.quote(c) for c in completions])
    # print ifs.join([escape_completion_name_str(c) for c in completions])

    debug("\nReturning completions:", completions)
    output_stream.write(ifs.join(completions).encode(locale.getpreferredencoding()))
    output_stream.flush()
    # os.fsync(output_stream.fileno()) - this raises an error, why?
    debug_stream.flush()
    # os.fsync(debug_stream.fileno())

    exit_method(0)
