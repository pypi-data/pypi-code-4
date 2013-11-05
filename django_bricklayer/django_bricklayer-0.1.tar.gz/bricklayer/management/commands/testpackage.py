from django.core.management.base import AppCommand
# Uncomment the next line for extending option list
# from optparse import make_option
from bricklayer.utils import exists_path, exists_dir
from django.template import loader as TemplateLoader, Context
import os
class Command(AppCommand):
    help = 'Create a package for app tests.'
    
    def handle_app(self, app, **options):
        app_label = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)

        # read tests.py file (if any)
        if exists_path(app_path, "tests.py"):
            with open(os.path.join(app_path, "tests.py")) as f:
                tests_py = f.read()

            #remove tests.py to avoid confilicts
            os.remove(os.path.join(app_path, "tests.py"))

        if not exists_dir(app_path, "tests"):
            os.mkdir(os.path.join(app_path, "tests"))

        if not exists_path(app_path, "tests", "__init__.py"):
            template = TemplateLoader.get_template("tests.__init__.py.template")
            context = Context({
                "app": app_label
                })
            with open(os.path.join(app_path, "tests", "__init__.py"), "w") as f:
                f.write(template.render(context))

        # Write the old tests.py in tests.app_label.py
        if not exists_path(app_path, "tests", app_label + ".py"):
            with open(os.path.join(app_path, "tests", app_label + ".py"), "w") as f: 
                f.write(tests_py)






