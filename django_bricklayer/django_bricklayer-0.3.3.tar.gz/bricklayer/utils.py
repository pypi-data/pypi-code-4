from django.core.management import get_commands, CommandError,load_command_class,BaseCommand, execute_from_command_line
from django.core.management.base import BaseCommand
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
    args = map(lambda token: token.strip(), filter( lambda token: token.strip()!='', command.split(" ")) )
    args.insert(0, "manage.py")
    
    execute_from_command_line(args)
        
    
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


class ColoredOutputMixin:
    """
        Mixin to print colored output,
        It should be used with classes extending BaseCommand.
    """
    def print_message(self, msg, ending='\n'):
        if ending and not msg.endswith(ending):
                msg += ending
        self.stdout.write(msg)
        
    def print_success(self, msg, ending='\n'):
        '''
            display a green message
        '''
        SUCCESS_MESSAGE = termcolors.make_style(fg='green', opts=('bold',))
        self.__display_colored_message(msg, SUCCESS_MESSAGE, ending)
    
    def print_error(self, msg, ending='\n'):
        '''
            display a red message
        '''
        ERROR_MESSAGE = termcolors.make_style(fg='red', opts=('bold',))
        self.__display_colored_message(msg, ERROR_MESSAGE, ending)
    
    def print_warning(self,msg, ending='\n'):
        '''
            display a yellow message
        '''
        WARNING_MESSAGE = termcolors.make_style(fg='yellow', opts=('bold',))
        self.__display_colored_message(msg, WARNING_MESSAGE, ending)
    
    def __display_colored_message(self, msg, style_func, ending):
        '''
            display a message given a color.
            Handle exceptions properly
        '''
        out = getattr(self, 'stdout', stdout)
        try:
            out.write(msg, style_func, ending)
        except TypeError:
            if ending and not msg.endswith(ending):
                msg += ending
            out.write(msg)

def is_blank(*args):
    if not exists_path(*args):
        return True
    
    with open(join(*args)) as f:
        body = f.read()
    
    return body.strip() == ""
        