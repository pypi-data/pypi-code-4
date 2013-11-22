from django.core.management.base import AppCommand
# Uncomment the next line for extending option list
# from optparse import make_option
from bricklayer.utils import exists_path, exists_dir
from django.template import loader as TemplateLoader, Context
import os
class Command(AppCommand):
    help = """Create a package for app tests.
Import all the tests defined in tests.py in the package.
To add more tests use addtest command """
    
    def handle_app(self, app, **options):
        app_label = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)

        # read tests.py file (if any)
        if exists_path(app_path, "tests.py"):
            tests_py_path = os.path.join(app_path, "tests.py")
            #Read tests.py ans save its content
            with open(tests_py_path) as f:
                tests_py = f.read()

            # Set up tests.py to work with the testsuite package
            with open(tests_py_path, 'w') as f:
                template = TemplateLoader.get_template('tests.py.template')
                context = Context({'app': app_label})
                f.write(template.render(context))

        # Create testsuite package       
        if not exists_dir(app_path, "testsuite"):
            os.mkdir(os.path.join(app_path, "testsuite"))

            
        if not exists_path(app_path, "testsuite", "__init__.py"):
            template = TemplateLoader.get_template("addtest.py.template")
            context = Context({
                "app": app_label,
                "test_name": app_label + "_tests"
                })
            with open(os.path.join(app_path, "testsuite", "__init__.py"), "w") as f:
                f.write(template.render(context))

        # Write the old tests.py in tests.APP_LABEL_tests.py
        if not exists_path(app_path, "testsuite", app_label + "_tests.py"):
            with open(os.path.join(app_path, "testsuite", app_label + "_tests.py"), "w") as f: 
                f.write(tests_py)






