from django.core.management import get_commands, CommandError,load_command_class,BaseCommand
from django.utils import termcolors
from optparse import OptionParser
from sys import stdout, stderr
from os.path import exists, join, isdir


SUCCESS_MESSAGE = termcolors.make_style(fg='green', opts=('bold',))

def underscore_to_camelcase(word, lower_first=False):
    result = ''.join(char.capitalize() for char in word.split('_'))
    if lower_first:
        return result[0].lower() + result[1:]
    else:
        return result

def run_manage_py(command):
    """
        Run console-like command.
        e.g.
        " run_manage_py("syncdb") "
        is equivalent to
        " $ python manage.py syncdb "
        
    """
    args = filter( lambda token: token.strip()!='', command.split(" "))
    
    name = args.pop(0)
    
    # Load the command object.
    try:
        app_name = get_commands()[name]
    except KeyError:
        raise CommandError("Unknown command: %r" % name)

    if isinstance(app_name, BaseCommand):
        # If the command is already loaded, use it directly.
        cmd = app_name
    else:
        cmd = load_command_class(app_name, name)
    
    cmd.stdout = stdout
    cmd.sterr  = stderr
    (opts, args) = OptionParser(option_list=cmd.option_list).parse_args(list(args))
    cmd.handle(*args, **vars(opts))
    
def exists_path(*args):
    """
        Test whether a path exists.
        e.g. 
        to test /usr/lib/python use
        exists_path('usr', 'lib', 'python')
    """
    return exists(join(*args))

def exists_dir(*args):
    """
        Test whether a path exists and is a dir.
        e.g. 
        to test /usr/lib/python use
        exists_path('usr', 'lib', 'python')
    """
    if not exists_path(*args): 
        return False
    
    return isdir(join(*args))

