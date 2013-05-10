import os
import json
import urllib
import urllib2

from .constants import TASKER_URL

INTERNAL_LOOP_COMMANDS = ('set/token', 'set/project')
INTERNAL_LOOP_COMMANDS_DICT = [
    {
        'command': 'set project',
        'args': ['project_id'],
        'help': '[project_id] sets given project_id as active',
    },
    {
        'command': 'set token',
        'args': ['token'],
        'help': '[token] sets given token as active',
    }
]


def red(text, bold=False):
    """Just a function that colors terminal output red
    """
    c = 31
    if bold:
        c = "1;31"
    return "\033[{0}m{1}\033[0m".format(c, text)


def match_command(user_input, av_commands):
    """Function that matches user input to commands that API will understand.
    """
    temp_join = []
    rest_of_args = user_input[:]
    for arg in user_input:
        temp_join.append(arg)
        rest_of_args.remove(arg)
        current = ' '.join(temp_join)
        if current in av_commands:
            return current, rest_of_args
    return False, []


def get_arg_names_from_help(command, help_dict):
    """Function that takes full help dict and searches for specific command
    then returns its arguments.
    """
    for command_dict in help_dict:
        if command_dict['command'] == command:
            return command_dict.get('args', [])
    return []


def build_arguments_dict(arguments, needed_args_names):
    """Function that matches user arguments to names of arguments that API
    needs.
    """
    arguments_dict = {}

    for i, name in enumerate(needed_args_names):
        arguments_dict.update({name: arguments[i]})
    return arguments_dict


def send(command, token, project, params={}):
    """Function that sends request to API and returns result.
    """
    if not params.get('token') and not params.get('project_id'):
        params.update({'token': token, 'project_id': project})

    if command in INTERNAL_LOOP_COMMANDS:
        return params

    url = TASKER_URL.format(command)
    data = urllib.urlencode(params)
    try:
        content = urllib2.urlopen(url=url, data=data)
    except urllib2.HTTPError as content:
        print(red('Error: {0}'.format(content.code)))
    except urllib2.URLError as error:
        print(red(error))
        return {}

    try:
        return json.loads(content.read())
    except ValueError:
        return content.read()
