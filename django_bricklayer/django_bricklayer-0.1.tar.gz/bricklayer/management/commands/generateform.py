from django.db.models import get_models
from django.core.management.base import AppCommand, CommandError
from django.template import loader as TemplateLoader, Context
from bricklayer.utils import exists_path
from optparse import make_option

import imp, os

class Command(AppCommand):
    help = 'Create ModelForm for each model passed as argument.'
    # Uncomment the lines below for extending option list
    option_list = AppCommand.option_list + (
        make_option('--models', '-m', 
                    dest='models', 
                    type="string",
                    default=None,
                    help='Model/s name. Multiple models can be passed separated by a comma. E.g. -m User,Post,Comment'),
    )
    def handle_app(self, app, **options):
        
        
        app_label = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)
        app_models = [model._meta.object_name for model in get_models(app)]
        # Parse params
        if options['models']:
            models = options['models'].split(",")
            # Test if models exists in the app
            for model in models:
                if model not in app_models:
                    raise CommandError("No model %s in %s"%(model,app_label))
        else:
            models = app_models

        template = TemplateLoader.get_template("forms.py.template")
        if exists_path(app_path, 'forms.py'):
            # forms.py write mode   
            mode = "a"
            models_to_define = filter( lambda m: not hasattr(forms, m), models)
            forms = imp.load_source('forms', os.path.join(app_path, 'forms.py'))
            context = Context({
                "app":app_label,
                "models_to_define": models_to_define,
                "import_forms":     not hasattr(forms, "forms")
                })
        else:
            mode = "w"
            context = Context({
                "app":app_label,
                "models_to_define": models,
                "import_forms":     True
                })

        with open(os.path.join(app_path, 'forms.py'), mode) as f: 
            f.write(template.render(context))
        
        





        assert models is not None
        