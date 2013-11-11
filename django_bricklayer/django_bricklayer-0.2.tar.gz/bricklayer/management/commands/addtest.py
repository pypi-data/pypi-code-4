from django.core.management.base import AppCommand, CommandError
from django.template import loader as TemplateLoader, Context
from optparse import make_option
from bricklayer.management.commands.testpackage import Command as TestFolderCommand
from bricklayer.utils import exists_dir, underscore_to_camelcase, exists_path, SUCCESS_MESSAGE
import os

class Command(AppCommand):
    help = 'Add a test file. Create a tests package if doesn\'t exist'
    # Uncomment the lines below for extending option list
    option_list = AppCommand.option_list + (
         make_option('--name', '-n', 
                     dest='test_name', 
                     type="string",
                     default=None,
                     help='test name'),
     )
    def handle_app(self, app, **options):
        app_label = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)
        is_verbose = options['verbosity'] >= 1

        if not options['test_name']:
            raise CommandError("Test name missing.")
        else:
            test_name = options["test_name"]
        

        if not exists_dir(app_path, 'testsuite'):
            self.stdout.write("testsuite package doesn't exist. A new one is going to be created.")
            command = TestFolderCommand()
            command.handle_app(app)

        # Create a new test file named "TESTNAME.py" if it doesn't exist
        if not exists_path(app_path,'testsuite', test_name.lower()+".py" ):
            template = TemplateLoader.get_template('test.py.template')
            context = Context({
                'lower_name': options["test_name"].lower(),
                'camel_name': underscore_to_camelcase( test_name.lower() )
                })
            with open(os.path.join(app_path, 'testsuite', test_name.lower())+".py", "w") as f:
                f.write(template.render(context))
            
            if is_verbose:
                msg = "%s.py created"%test_name
                try:
                    self.stdout.write(msg, SUCCESS_MESSAGE)
                except:
                    self.stdout.write(msg)

        # Update testsuite.__init__.py
        template = TemplateLoader.get_template('addtest.py.template')
        context = Context({
            'test_name': test_name,
            'app': app_label
            })

        with open(os.path.join(app_path, 'testsuite', '__init__.py'), "a") as f:
            f.write(template.render(context))

        if is_verbose:
            msg = "%s added to testsuite"%test_name
            try:
                self.stdout.write(msg, SUCCESS_MESSAGE)
            except:
                self.stdout.write(msg)
                





