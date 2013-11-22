from django.core.management.base import BaseCommand, CommandError
from django.core.management import get_commands
from django.utils.importlib import import_module
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.template import loader as TemplateLoader, Context
from optparse import make_option
from bricklayer.utils import ColoredOutputMixin, underscore_to_camelcase
import os

class Command(BaseCommand, ColoredOutputMixin):
    option_list = BaseCommand.option_list + (
        make_option('--app', '-a', 
                    dest='appcommand', 
                    action="store_true",
                    default=False,
                    help='Create an AppCommand'),
    )
    help = 'It generates new command skeleton.'
    args = '[command_name, app_label]'
    def handle(self, command_name, app_label, **options):
        
        
        
        assert app_label is not None
        assert command_name is not None
        
        # Check if command with the same name exist
        # to avoid name clashes
        
        if command_name in get_commands().keys():
            raise CommandError("A command with the name '%s' is already defined in %s"%(command_name, get_commands()[command_name]))
        try:      
            app = import_module(app_label)
            # Check if the app is installed
            try:
                models.get_app(app_label)
            except ImproperlyConfigured:
                self.print_warning("WARNING: %s is not installed.")
                
        except ImportError:
            raise Exception("app %s doesn't exist"%app_label)
        
        app_path = os.path.dirname(app.__file__)
        
        management_path = os.path.join(app_path, "management")
        commands_path   = os.path.join(management_path, "commands")
        
        # Create management and management/commands folders
        if not ( os.path.exists(commands_path) and os.path.isdir(commands_path) ):
            os.makedirs(commands_path)
        
        # Add __init__.py file to management folder in order to turn it into
        # a python package.
        management_init_file = os.path.join(management_path,"__init__.py")
        if not os.path.exists(management_init_file):
            with open(management_init_file,"w") as f: f.close()
            self.print_message("management package created")
            
        
        
        # Add __init__.py file to commands folder in order to turn it into
        # a python package.
        # Create a command shortcut.
        commands_init_file = os.path.join(commands_path,"__init__.py")
        template = TemplateLoader.get_template("command.init.py.template")
        context = Context({'app': app_label, 
                           'command_name':command_name,
                           'command_name_camel':underscore_to_camelcase(command_name)})
        if not os.path.exists(commands_init_file):
            mode = 'w'
            self.print_message("commands package created")
        else:
            mode = 'a'
        with open(commands_init_file,mode) as f: 
            f.write(template.render(context))
        
        command_file = os.path.join(commands_path,command_name+".py")
        
        template = TemplateLoader.get_template('appcommand.py.template' if options['appcommand'] else 'command.py.template')
        context = Context({})
        if not os.path.exists(command_file):
            with open(command_file,"w") as f: 
                f.write(template.render(context))
            
            self.print_success("command %s created."%command_name)
        else:
            self.print_error("file %s.py already exists"%command_name) 
           
    
        