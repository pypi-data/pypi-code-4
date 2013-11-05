from django.core.management.base import AppCommand, CommandError
# Uncomment the next line for extending option list
from optparse import make_option
from bricklayer.management.commands.testfolder import Command as TestFolderCommand
from bricklayer.utils import exists_dir, underscore_to_camelcase
from django.template import loader as TemplateLoader, Context
import os
class Command(AppCommand):
    help = 'Add a test file. Create a tests package if doesn\'t exist'
    # Uncomment the lines below for extending option list
    option_list = AppCommand.option_list + (
         make_option('--name', '-n', 
                     dest='testname', 
                     type="string",
                     default=None,
                     help='test name'),
     )
    def handle_app(self, app, **options):
        app_label = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)

        if not options['testname']:
            raise CommandError("Test name missing.")

        if not exists_dir(app_path, 'tests'):
            self.stdout.write("tests package doesn't exists. A new one is going to be created")
            command = TestFolderCommand()
            command.handle_app(app)

        # Update tests.__init__.py
        template = TemplateLoader.get_template('addtest.py.template')
        context = Context({
            'testname': options["testname"],
            'app': app_label
            })

        with open(os.path.join(app_path, 'tests', '__init__.py'), "a") as f:
            f.write(template.render(context))
        
        # Update tests.__init__.py
        template = TemplateLoader.get_template('test.py.template')
        context = Context({
            'lower_name': options["testname"].lower(),
            'camel_name': underscore_to_camelcase( options["testname"].lower() )
            })

        with open(os.path.join(app_path, 'tests', options["testname"].lower())+".py", "w") as f:
            f.write(template.render(context))

        self.stdout.write("Test %s created"%options["testname"])





