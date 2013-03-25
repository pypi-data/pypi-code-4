"""
Library module for sprinter. To handle a lot of the typical
features of the library.

"""
import inspect
import imp
import re
import subprocess
import urllib2
from base64 import b64encode

from getpass import getpass
from subprocess import PIPE, STDOUT

from sprinter.recipebase import RecipeBase


def get_recipe_class(recipe, environment):
    """
    Get the recipe name and return an instance The recipe path is a
    path to the module. get_recipe_class performs reflection to find
    the first class that extends recipebase, and that is the class
    that an instance of it gets returned.
    """
    try:
        r = __recursive_import(recipe)
        member_dict = dict(inspect.getmembers(r))
        for v in member_dict.values():
            if inspect.isclass(v) and issubclass(v, RecipeBase) and v != RecipeBase:
                return v(environment)
        raise Exception("No recipe %s exists in classpath!" % recipe)
    except ImportError as e:
        raise e


def call(command, stdin=None, env=None, cwd=None, bash=False):
    if not bash:
        args = __whitespace_smart_split(command)
        p = subprocess.Popen(args, stdout=PIPE, stdin=PIPE, stderr=STDOUT, env=env, cwd=cwd)
        return p.communicate(input=stdin)[0]
    else:
        command = " ".join([__process(arg) for arg in __whitespace_smart_split(command)])
        subprocess.call(command, shell=True, executable='/bin/bash')


def __process(arg):
    """
    Process args for a bash shell
    """
    # assumes it's wrappen in quotes, or is a flag
    if arg[0] in ["'", '"', '-']:
        return arg
    else:
        return re.escape(arg)


def __whitespace_smart_split(command):
    """
    Split a command by whitespace, taking care to not split on whitespace within quotes.

    >>> __whitespace_smart_split("test this \\\"in here\\\" again")
    ['test', 'this', '"in here"', 'again']
    """
    return_array = []
    s = ""
    in_double_quotes = False
    escape = False
    for c in command:
        if c == '"':
            if in_double_quotes:
                if escape:
                    s += c
                    escape = False
                else:
                    s += c
                    in_double_quotes = False
            else:
                in_double_quotes = True
                s += c
        else:
            if in_double_quotes:
                if c == '\\':
                    escape = True
                    s += c
                else:
                    escape = False
                    s += c
            else:
                if c == ' ':
                    return_array.append(s)
                    s = ""
                else:
                    s += c
    if s != "":
        return_array.append(s)
    return return_array


def authenticated_get(username, password, url):
    """
    Perform an authorized query to the url, and return the result
    """
    request = urllib2.Request(url)
    base64string = b64encode((b"%s:%s" % (username, password)).decode("ascii"))
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)
    return result.read()


def prompt(prompt_string, default=None, secret=False):
    """
    Prompt user for a string, with a default value
    """
    prompt_string += (" (default %s): " % default if default else ": ")
    if secret:
        val = getpass(prompt_string)
    else:
        val = raw_input(prompt_string)
    return (val if val else default)


def __recursive_import(module_name):
    """
    Recursively looks for and imports the names, returning the
    module desired

    >>> __recursive_import("sprinter.recipes.unpack") # doctest: +ELLIPSIS
    <module 'unpack' from '...'>

    currently module with relative imports don't work.
    """
    names = module_name.split(".")
    path = None
    module = None
    while len(names) > 0:
        if module:
            path = module.__path__
        name = names.pop(0)
        (module_file, pathname, description) = imp.find_module(name, path)
        module = imp.load_module(name, module_file, pathname, description)
    return module

if __name__ == '__main__':
    import doctest
    doctest.testmod()
