from django.core.management.base import BaseCommand
import os
from optparse import make_option
from django.utils.importlib import import_module
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.template import loader as TemplateLoader, Context

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--for', '-4', 
                    dest='app', 
                    type="string",
                    default=None,
                    help='App name'),
        make_option('--cmd', '-c', 
                    dest='command', 
                    type="string",
                    default=None,
                    help='Command name'),
        make_option('--app', '-a', 
                    dest='appcommand', 
                    action="store_true",
                    default=False,
                    help='Create an AppCommand'),
    )
    help = 'Help text goes here'
    
    def handle(self, *args, **options):
        
        # Parse params
        if options['command'] and options['app']:
            
            app_name = options['app']
            command_name = options['command']
        elif not options['command'] and options['app']:
            
            app_name = options['app']
            try:
                command_name = args[0]
            except IndexError:
                raise Exception("Command name missing")
        elif options['command'] and not options['app']:
            command_name = options['command']
            try:
                app_name = args[0]
            except IndexError:
                raise Exception("App name missing")
        else:
            try:
                command_name = args[0]
                app_name = args[1]
            except IndexError:
                raise Exception("App name or Command name missing")
        
        assert app_name is not None
        assert command_name is not None
           
        
        try:      
            app = import_module(app_name)
            # Check if the app is installed
            try:
                models.get_app(app_name)
            except ImproperlyConfigured:
                self.stdout.write("WARNING: %s is not installed.")
                
        except ImportError:
            raise Exception("app %s doesn't exist"%app_name)
        
        app_path = os.path.dirname(app.__file__)
        
        management_path = os.path.join(app_path, "management")
        commands_path   = os.path.join(management_path, "commands")
        
        if not ( os.path.exists(commands_path) and os.path.isdir(commands_path) ):
            os.makedirs(commands_path)
            #self.stdout.write(app_name + ".management.commands created")
        
        management_init_file = os.path.join(management_path,"__init__.py")
        if not os.path.exists(management_init_file):
            with open(management_init_file,"w") as f: f.close()
            #self.stdout.write("management __init__.py created")
            
        commands_init_file = os.path.join(commands_path,"__init__.py")
        if not os.path.exists(commands_init_file):
            with open(commands_init_file,"w") as f: f.close()
            #self.stdout.write("commands __init__.py created")
        
        command_file = os.path.join(commands_path,command_name+".py")
        
        template = TemplateLoader.get_template('appcommand.py.template' if options['appcommand'] else 'command.py.template')
        context = Context({})
        if not os.path.exists(command_file):
            with open(command_file,"w") as f: 
                f.write(template.render(context))
        else:
            self.stdout.write("file %s.py already exists"%command_name) 
           
    
        