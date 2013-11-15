from django.db.models import get_app
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError
from django.template import loader as TemplateLoader, Context
from bricklayer.utils import exists_dir, underscore_to_camelcase, exists_path, ColoredOutputMixin
from bricklayer.management.commands.generatetestpackage import Command as TestFolderCommand
import os

class Command(BaseCommand, ColoredOutputMixin):
    help = 'Add a test file. Create a tests package if doesn\'t exist'
    args = '[test_name, app_name]'
    
    def handle(self, test_name, app_name, **options):
        try:
            app = get_app(app_name)
        except (ImproperlyConfigured, ImportError) as e:
            raise CommandError("%s. Are you sure your INSTALLED_APPS setting is correct?" % e)
        
        app_label = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)
        is_verbose = options['verbosity'] >= 1

        if not exists_dir(app_path, 'testsuite'):
            self.stdout.write("testsuite package doesn't exist. A new one is going to be created.")
            command = TestFolderCommand()
            command.handle_app(app)

        # Create a new test file named "TESTNAME.py" if it doesn't exist
        if not exists_path(app_path,'testsuite', test_name.lower()+".py" ):
            template = TemplateLoader.get_template('test.py.template')
            context = Context({
                'lower_name': test_name.lower(),
                'camel_name': underscore_to_camelcase( test_name.lower() )
                })
            with open(os.path.join(app_path, 'testsuite', test_name.lower())+".py", "w") as f:
                f.write(template.render(context))
            
            if is_verbose:
                msg = "%s.py created"%test_name
                self.print_success(msg)
                    
        # Update testsuite.__init__.py
        template = TemplateLoader.get_template('addtest.py.template')
        context = Context({
            'test_name': test_name,
            'app': app_label
            })
        
        # import the new test in the test suite
        with open(os.path.join(app_path, 'testsuite', '__init__.py'), "r+") as f:
            content = template.render(context)
            test_suite_content = f.read()
            if content not in test_suite_content:
                f.write(content)

                if is_verbose:
                    msg = "%s added to %s.testsuite"%(test_name, app_label)
                    self.print_success(msg)
            elif is_verbose:
                msg = "%s already imported in the %s.testsuite"%(test_name, app_label)
                self.print_warning(msg)





