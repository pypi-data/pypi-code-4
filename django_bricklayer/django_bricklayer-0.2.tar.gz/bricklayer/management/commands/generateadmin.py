from django.core.management.base import AppCommand, CommandError
from django.db.models import get_models
from django.template import loader as TemplateLoader, Context
from optparse import make_option
import os
import re


class Command(AppCommand):
    help = "Creates a basic admin.py file if it doesn't exists. For each model, create an AdminModel class (if it doesn't exists) and then register the model on the admin site."

    args = '[appname ...]'

    option_list = AppCommand.option_list + (
        make_option('--models', '-m', 
                    dest='models', 
                    type="string",
                    default=None,
                    help='Model/s name. Multiple models can be passed separated by a comma. E.g. -m User,Post,Comment'), 
    )

    def handle_app(self, app, **options):
        app_name = app.__name__.split('.')[-2]

        admin_filename = os.path.join(os.path.dirname(app.__file__), 'admin.py')
        # Get the name of each model in the app
        app_models = [model._meta.object_name for model in get_models(app)]
        # if models    
        template = TemplateLoader.get_template("admin.py.template")
        if options['models']:
            # Accept list of models as CSV
            requested_models = options["models"].split(",")
            for model in requested_models:
                if model not in app_models:
                    raise CommandError("No model %s in %s"%(model,app_name))
            app_models = filter(lambda model: model in requested_models, app_models)
        if not os.path.exists(admin_filename):
            self.stdout.write(app_name+".admin.py created")
            mode = "w"
            context = Context({"app": app_name, 
                                "models": app_models,
                                "models_to_define": app_models,
                                "models_to_register": app_models})
            
        else:
            self.stdout.write("admin.py already exists")
            """
            Check if each model is already registered.
            For each model which hasn't been registered yet,
            create an AdminClass and register the model.
            """
            
            with open(admin_filename, 'r') as admin_file:
                admin_file_lines = admin_file.readlines()
                admin_file_text = "".join( admin_file_lines  )
            
            mode = 'a'
            models_to_define = []
            models_to_register = []
            for model in app_models:
                regex = re.compile("(admin.site.register\(\s*"+model+"\s*,)",re.MULTILINE)
                
                #if model has not been registered yet..
                if not regex.search(admin_file_text):
                    models_to_register.append(model)
                
                # If admin model name doesn't collide with an existing one
                if not "%sAdmin"%model in admin_file_text:
                    models_to_define.append(model)
            
            context = Context({"app": app_name, 
                              "models": app_models,
                              "models_to_define": models_to_define,
                              "models_to_register": models_to_register})

        # Write admin.py   
        with open(admin_filename, mode) as admin_file:
                admin_file.write(template.render(context))    
            