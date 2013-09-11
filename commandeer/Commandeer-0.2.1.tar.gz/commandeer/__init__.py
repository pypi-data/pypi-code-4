# Copyright (C) 2012 Johannes Spielmann
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Use this module to add a simple way to add nice command line interaction to your program.

Usage: in your main python script, arrange for all functions that should be reachable from
the command line to have a name ending in ``_command``. All arguments to your function are
parsed as arguments in a smart way.
At the end of your script, simply add
a call to ``commandeer.cli()`` and you're good to go. A simple example script could look like
this::

  "This script echo's your input."
  def echo_command(input, timestamp=False, indent=0):
      "Outputs the input, with an optional timestamp and some indenting."
      echo_str = input
      if timestamp:
          echo_str = "[date]" + echo_str
      echo_str = " " * indent + echo_str
      print(echo_str)
      
  if __name__ == '__main__':
      commandeer.cli()

Calling this script without any arguments (or with only "help") will show a short help screen::

  $ python script.py help
  This script echo's your input.
  Usage: script.py command [options]
  
  Command can be one of the following:
    echo   Outputs the input, with an optional timestamp and some indenting.

Calling the script with "help commandname" will print more information from the docstring as
well as the available arguments.

For a more detailed explanation refer to the documentation.
"""

import inspect
import sys

is_PY2 = sys.version_info[0] == 2
is_PY3 = sys.version_info[0] == 3

#exported functions

def cli(with_help=True):
    """Create a really nice command line from the callers local space, then parse the program arguments and act accordingly.
    
    If you set the ``with_help`` parameter to ``True``, commandeer will add the help command by itself and also execute that command
    when no other commands are passed to the program. If you set it to ``False``, no help will be added and only your commands will
    be available.
    """
    # we need to go back one frame because we need to parse the caller's local namespace
    # this line is here because we don't want to inflate the stack frame backtracing too much, it's only one level we have to go back from here
    caller_locals = inspect.currentframe().f_back.f_locals

    # build the command map (i.e. short commands)
    commands = _build_commands_from_locals(caller_locals)
    commandmap = _condense(commands)
    
    maindoc = caller_locals['__doc__']
    
    # parse command line arguments into components
    calledfile, command, switches, args = _argparse()
    
    # add help to the mix if it is enabled
    if with_help:
        def help(*helpforcommands):
            """Show this help screen."""
            if helpforcommands:
                for commandname in helpforcommands:
                    return _help_for_command(calledfile, commandname, commandmap[commandname])
            return _help(calledfile, maindoc, commands, command)
        commands['help'] = help
        commandmap['help'] = commandmap['hlp'] = commandmap['?'] = help
        if command == '':
            command = 'help'

    # before calling a command, find the right command
    if command not in commandmap:
        return _error_command_not_found(calledfile, maindoc, commands, command, switches, args)
        
    command_func = commandmap[command]
    
    return _call_command_with_args(command, commandmap[command], switches, args)
    
    
###############################################################################################################################
# constants

# help for the whole program
HELP_FORMAT = """  {doc}Usage: {name} command [options]

  Here are the commands you can try:

  {commands_formatted}
  If you need help on any of them, try "{name} help command" for any of them."""

# we build the actual format string from this format_format string. Oh, fun!
COMMAND_SHORTDOC_FORMAT_FORMAT = """  {{name:<{spacerlength}}}{{docline}}\n  """

# help format for a single command
HELP_COMMAND_FORMAT = """Usage: {name} {command}{required}{aliases}
  {shortexp}

  {explanation}"""

ARG_DOC_FORMAT_FORMAT = """    {{name:<{spacerlength}}}  {{doc}}
"""
ARG_ADD_FORMAT = """

  Required arguments:
{args_formatted}"""

SWITCH_DOC_FORMAT_FORMAT = """    --{{name:<{spacerlength}}}  {{doc}}
        {spacer}default value: {{default}}
"""
SWITCH_ADD_FORMAT = """

  Command line options:  
{switches_formatted}"""

# allowed values for boolean switch values
TRUE_VALUES = "true", "yes", "on", "1", 
FALSE_VALUES = "false", "no", "off", "0", "-1"
# but, honestly, just use --switchname or --noswitchname


###############################################################################################################################
# functions directly called from the exported functions

def _build_commands_from_locals(caller_locals):
    """Extract all callable commands from the 'locals' dictionary of the caller."""
    commands = dict()
    for l in caller_locals:
        if l.endswith('_command'):
            commands[l[:-8]] = caller_locals[l]

    return commands
    
    
def _condense(command_dict):
    """Create a list of short commands.
    
    Creates a dictionary of strings that can be used to start commands. These short commands
    are built from all available commands in such a way that the shortest (and all longer)
    mnemonics that uniquely idenfity one command.
    
    It's O(n^2), but that really shouldn't matter because we don't expect there to be many commands."""
    
    res = dict()
    candidates = set()
    for command_name, command in command_dict.items():
        res[command_name] = command
        if 'aliases' in command.__dict__:
            for alias in command.aliases:   # note that we might clobber legitimate functions if the aliases are duplicate (or the other way around)
                res[alias] = command
    
    # now that the commands and aliases have been added 
    for command_name, command in command_dict.items():
        for length in range(1, len(command_name)):
            unique = True
            short_command_name = command_name[:length]
            for othercommand_name, other_command in res.items():
                if othercommand_name.startswith(short_command_name) and command_name != othercommand_name:
                    unique = False
                    break
            if unique:
                res[short_command_name] = command
    
    return res


def _argparse(argv=None):
    """Parse arguments into an easily digestible dictionary.
    
    Returns the name of the called file, the command, all switches and their values and all arguments.
    Arguments are such values in the array that do not start with a dash, switches are the rest.
    The first argument is special because it is the command. If the first entry in the array (afte
    the file name) is a switch, the command will be ''.
    Expects an array in the same form as sys.argv."""
    if argv is None:
        argv = sys.argv

    start_args_index = 2
    
    callfile = argv[0]
    if len(argv) > 1:
        if argv[1].startswith('-'):
            start_args_index = 1
            command = ''
        else:
            command = argv[1]
    else:
        command = ''

    args = list()
    switches = dict()
    last = None
    for arg_pos in argv[start_args_index:]:
        if arg_pos.startswith('-'):
            last = None
            switch = _clean_switch(arg_pos)
            if switch.find('=') != -1:
                switchname, switchval = switch.split('=', 1)
                switches[switchname] = switchval
            else:
                switches[switch] = ''
                last = switch        # last is our 'carry bit', because we might need to add something to this command at the next position
        else:
            if last is not None:
                switches[last] = arg_pos
                last = None
            else:
                args.append(arg_pos)
        
    return callfile, command, switches, args

def _call_command_with_args(command, command_func, switches, args):
    """Call the given command_func (with name 'command') using the specified switches and args."""
    
    fn_accepts_args, fn_args, fn_defaults, fn_kwargs, fn_all_args = _funcspec(command_func)

    pass_args = list()
    pass_kwargs = dict()

    #check number of arguments
    if len(args) < len(fn_args):
        return _error_too_few_input_arguments(command, command_func, args, fn_args)
    else:
        if len(args) == len(fn_args):
            pass_args = args
        else: #len(args) > len(fn_args)
            if fn_accepts_args:
                pass_args = args[:len(fn_args)]   # we'll have to fill up the default arguments before we can go on, unfortunately
                for def_arg in fn_all_args[len(fn_args):len(fn_defaults)+len(fn_args)]:
                    pass_args.append(fn_defaults[def_arg])
                pass_args.extend(args[len(fn_args):])
            else:
                return _error_too_many_input_arguments(command, command_func, args, fn_args)

    # fill up arguments array with defaults
    for argname in fn_all_args:
        if argname in fn_defaults:
            pass_args.append(fn_defaults[argname])

    #clean up the switch values (and check for errors)
    error_switches = dict()
    for switch in switches:
        # we clean once because we want to get rid of the 'no'-beginnings
        switch_val = switches[switch]
        switch_val, switch = _clean_value(switch_val, '', switch)
        
        if switch not in fn_defaults and switch not in fn_kwargs:
            error_switches[switch] = switch_val
            continue
        
        if switch in fn_defaults:
            switch_default = fn_defaults.get(switch)
            clean_value, clean_switch = _clean_value(switch_val, switch_default, switch)
            pass_args[fn_all_args.index(clean_switch)] = clean_value 
        else: # switch in fn_kwargs
            switch_default = fn_kwargs.get(switch)
            clean_value, clean_switch = _clean_value(switch_val, switch_default, switch)
            pass_kwargs[clean_switch] = clean_value 

    if error_switches:
        return _error_too_many_switches(command, command_func, error_switches)

    return command_func(*pass_args, **pass_kwargs)



###############################################################################################################################
# help functionality
def _help(name, maindoc, commands, command):
    """Show a helpful help message for available commands."""

    maxlength = max(map(len, commands))
    # produce shortdoc-format by inserting the max-length + 4 into the shortdoc-format-format
    COMMAND_SHORTDOC_FORMAT = COMMAND_SHORTDOC_FORMAT_FORMAT.format(spacerlength=maxlength+6)
    commands_formatted = ""
    for command in sorted(commands):
        commands_formatted += COMMAND_SHORTDOC_FORMAT.format(name=command, docline=_firstline(commands[command].__doc__))
    
    if maindoc:
        maindoc += "\n  "
    else:
        maindoc = ''
    helpstr = HELP_FORMAT.format(name=name, doc=maindoc, commands_formatted=commands_formatted)
    
    print(helpstr)
        
def _help_for_command(name, command, command_func):
    """Show the help for a specific command."""

    shortdoc, longdoc, params = _parse_docstring(command_func.__doc__)

    fn_accepts_args, fn_args, fn_defaults, fn_kwargs, fn_all_args = _funcspec(command_func)

    # prepare doc for required arguments
    args_maxlength = max(map(len, fn_args + ['']))
    ARG_DOC_FORMAT = ARG_DOC_FORMAT_FORMAT.format(spacerlength=args_maxlength)
    args_formatted = ""
    for arg in fn_args:
        args_formatted += ARG_DOC_FORMAT.format(name=arg, doc=params.get(arg, ''))

    # prepare doc for each of the optional values
    fn_defaults.update(fn_kwargs)
    switches = list(fn_defaults) + list(fn_kwargs)
    switches_maxlength = max(map(len, switches + ['']))
    SWITCH_DOC_FORMAT = SWITCH_DOC_FORMAT_FORMAT.format(spacerlength=switches_maxlength, spacer=' ' * switches_maxlength)
    switches_formatted = ""
    for switch in fn_defaults:
        default = str(fn_defaults[switch])
        switches_formatted += SWITCH_DOC_FORMAT.format(name=switch, default=default, doc=params.get(switch, ''))

    # assembling final string
    required, aliases = "", ""
    if fn_args:
        required = " " + ' '.join(fn_args)
    if fn_accepts_args:
        required += " [optional arguments]"
    if fn_defaults:
        required += " [optional switches]"
    if 'aliases' in command_func.__dict__:
        aliases = """
  Aliases: {}
""".format(', '.join(command_func.aliases))
    helpstr = HELP_COMMAND_FORMAT.format(name=name, command=command, required=required, aliases=aliases, shortexp=shortdoc, explanation=longdoc).strip()
    if fn_args:
        helpstr += ARG_ADD_FORMAT.format(args_formatted=args_formatted[:-1])  # -1 because that's removing the extra newline at the end
    if switches:
        helpstr += SWITCH_ADD_FORMAT.format(switches_formatted=switches_formatted)

    print(helpstr)
    
    
###############################################################################################################################
# error handlers
def _error_too_few_input_arguments(command, command_func, args, fnargs):
    """Call when the error occurs: too few input arguments."""
    
    print("Error: missing required arguments. Here is a list of arguments this command requires and the values you gave for them:")
    
    shortdoc, longdoc, params = _parse_docstring(command_func.__doc__)
    args_maxlength = max(map(len, fnargs + ['']))
    ARG_DOC_FORMAT = ARG_DOC_FORMAT_FORMAT.format(spacerlength=args_maxlength)
    args_formatted = ""
    for index, arg in enumerate(fnargs):
        if index < len(args):
            args_formatted += ARG_DOC_FORMAT.format(name=arg, doc="'{}'".format(args[index]))
        else:
            args_formatted += ARG_DOC_FORMAT.format(name=arg, doc=params[arg])
    
    print(args_formatted[:-1])   # removing the extra newline at the end
    
    print("Try 'help {}' for a full documentation of this command.".format(command))

def _error_too_many_input_arguments(command, command_func, args, fnargs):
    """Call when the error occurred: Too many input arguments."""
    
    print("Error: too many arguments. Here is a list of arguments this command takes and the values you gave for them:")
    
    shortdoc, longdoc, params = _parse_docstring(command_func.__doc__)
    args_maxlength = max(map(len, fnargs + ['']))
    ARG_DOC_FORMAT = ARG_DOC_FORMAT_FORMAT.format(spacerlength=args_maxlength)
    args_formatted = ""
    for index, arg in enumerate(fnargs):
        args_formatted += ARG_DOC_FORMAT.format(name=arg, doc="'{}'".format(args[index]))
    
    print(args_formatted[:-1])   # removing the extra newline at the end

    print("You supplied the additional arguments: " + ' '.join(args[len(fnargs):]))
    
    print("Try 'help {}' for a full documentation of this command.".format(command))

def _error_too_many_switches(command, command_func, error_switches):
    """Call when there are non-recognized switches."""

    shortdoc, longdoc, params = _parse_docstring(command_func.__doc__)
    fn_accepts_args, fn_args, fn_defaults, fn_kwargs, fn_all_args = _funcspec(command_func)
    
    # prepare doc for each of the optional values
    fn_defaults.update(fn_kwargs)
    switches = list(fn_defaults) + list(fn_kwargs)
    switches_maxlength = max(map(len, switches + list(error_switches)))
    SWITCH_DOC_FORMAT = SWITCH_DOC_FORMAT_FORMAT.format(spacerlength=switches_maxlength, spacer=' ' * switches_maxlength)
    switches_formatted = ""
    for switch in fn_defaults:
        default = str(fn_defaults[switch])
        switches_formatted += SWITCH_DOC_FORMAT.format(name=switch, default=default, doc=params.get(switch, ''))

    ESWITCH_DOC_FORMAT = ARG_DOC_FORMAT_FORMAT.format(spacerlength=switches_maxlength+2, spacer=' ' * (switches_maxlength+2)) # +2 to account for missing --
    eswitches_formatted = ""
    for switch in error_switches:
        eswitches_formatted += ESWITCH_DOC_FORMAT.format(name="--"+switch, doc=repr(error_switches[switch]))

    print("Error: unrecognized options: Here is a list of available options")
    print(switches_formatted)
    print("You supplied the following extra options:")
    print(eswitches_formatted)
    
    

def _error_command_not_found(name, maindoc, commands, command, switches, args):
    """Call when the error occurred: The command was not found."""
    # todo: must be a lot better here!
    _help(name, maindoc, commands, command)
    
    print("Error: Command '{}' not found".format(command))
    # print("available commands are:", ", ".join(commands))
    # print("use '{} help' to get information about each of them".format(name))


###############################################################################################################################
# helper functions

def _clean_switch(switchinput):
    """Remove dashes from the beginning of the string"""
    while switchinput.startswith('-'):
        switchinput = switchinput[1:]
    return switchinput

def _firstline(s):
    """Return the first line of the string."""
    if s is None:
        return ''
    return s.split('\n', 1)[0]

def _parse_docstring(s):
    """Parse out the short and long parts of a docstring and extract the param descriptions from them."""
    if s is None:
        return '', '', {}
    res = s.split('\n', 1)
    if len(res) == 1:
        return s, '', {}
    shortdoc = res[0]
    
    # find and extract the parameter lines
    params = {}
    lines = res[1].split('\n')
    doclines = list()
    for line in lines:
        # TODO: multiline param descriptions
        line = line.strip()
        if line.startswith('\param') or line.startswith('@param'):
            spl = line.split(' ', 2)
            spl.extend(('', '', ''))
            commandname = spl[1]
            doc = spl[2].strip()
            params[commandname] = doc
        else:
            if not line.startswith('\\') and not line.startswith('@'):
                doclines.append(line)
    
    longdoc = ' '.join(line for line in doclines).strip()   #why the second strip? because we get spaces in the beginning otherwise

    return shortdoc, longdoc, params

def _firstline_separated(s):
    if s is None:
        return ''
    res = s.split('\n', 1)
    if len(res) == 1:
        return res[0], ''
    return res
    
def _funcspec(fn):
    """Parse out the function specification from the given function.
    
    Returns a boolean that indicates whether the function accepts a variable number of arguments,
    a list of arguments without a default value, a dictionary of arguments with a default value
    and a list of all arguments the function accepts.
    Note that this is not a "full" functional specification, as we are only interested in certain parts.
    """

    if is_PY2:
        fnargs, fnvarargname, fnkwname, fndefaults = inspect.getargspec(fn)
        fnkwonlyargs = []
        fnkwonlydefaults = None
        fnannotations = {}
    elif is_PY3:
        fnargs, fnvarargname, fnkwname, fndefaults, fnkwonlyargs, fnkwonlydefaults, fnannotations = inspect.getfullargspec(fn)
    else:
        return [], [], [], [], []

    # normalize to empty types instead of None
    fndefaults = fndefaults or []
    fnkwonlydefaults = fnkwonlydefaults or dict()

    defaults = dict()
    for i in range(len(fndefaults)):
        defaults[fnargs[-(i+1)]] = fndefaults[-(i+1)]

    
    if len(fndefaults) > 0:
        args = fnargs[:-len(fndefaults)]
    else:
        args = fnargs[:]

    all_args = fnargs + fnkwonlyargs
    
    accepts_args = fnvarargname is not None
    
    return accepts_args, args, defaults, fnkwonlydefaults, all_args
    
    

def _clean_value(value, default, name):
    """Clean up the switch value for use in calling a function.
    
    This includes checking the type, determining some boolean values as well as accepting
    switches that are in the form 'noYYY' or 'YYY' to indicate boolean values.
    """
    if value == '':                    # values of empty string are those that don't have arguments
        if name.startswith('no'):
            return False, name[2:]
        else:
            return True, name
    if type(default) == type(0) or type(default) == type(0.0):
        try:
            return int(value), name
        except:
            try:
                return float(value), name
            except:
                return value, name
    if type(default) == type(True):
        value = str(value).lower()
        if value not in TRUE_VALUES and value not in FALSE_VALUES:
            return None, name
        return value in TRUE_VALUES, name
    return value, name
    
    

    


