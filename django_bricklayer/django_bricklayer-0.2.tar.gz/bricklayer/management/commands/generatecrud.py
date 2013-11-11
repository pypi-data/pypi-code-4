from django.conf import settings
from django.core.management.base import AppCommand, CommandError
from django.db.models import get_models, get_model
from django.template import loader as TemplateLoader, Context
from django.utils.module_loading import import_module
from bricklayer.utils import exists_dir, exists_path
from optparse import make_option
import os, imp
import inspect



class Command(AppCommand):
    help = """Creates generic views, urls.py and templates for your models."""
    option_list = AppCommand.option_list + (
        make_option('--models', '-m', 
                    dest='models', 
                    type="string",
                    default=None,
                    help='Model/s name. Multiple models can be passed separated by a comma. E.g. -m User,Post,Comment'),
        make_option('--all', '-a', 
                    dest='all',
                    action="store_true",
                    default=False,
                    help='Process all models'),
        make_option('--form', '-f', 
                    dest='forms',
                    action="store_true",
                    default=False,
                    help='Generate a ModelForm for each model'),
    )
    

    def handle_app(self, app, **options):
                
        
        if options['all'] and options['models']:
            raise CommandError("Do you want process all models or just %s?"%options['models'])
        
        # Check if multiple model are passed as arguments
        if options['models'] and ',' in options['models']:
            options['models'] = options['models'].split(',')
        else:
            options['models'] = [ options['models'] ]
        
        # some useful shortcuts
        app_models = [model._meta.object_name for model in get_models(app)]
        models = app_models if options['all'] else options['models']
        app_name = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)
        template_path = os.path.join(app_path, 'templates')
        app_template_path = os.path.join(app_path, 'templates', app_name)
       
        # Test if models exists in the app
        if not options['all']:
            for model in models:
                if model not in app_models:
                    raise CommandError("No model %s in %s"%(model,app_name))
            
        # Create templates folder if not exists
        if not exists_dir(template_path):
            os.mkdir(template_path)
        
        if not exists_dir(app_template_path):
            os.mkdir(app_template_path)
        
        # Create templates 
        for model in models:
            model_name = model.lower()
            model_class = get_model(app_name, model)
            assert model_class is not None, "model_class is None"
            
            
            
            # Model form template
            template = TemplateLoader.get_template('form.html.template')
            context = Context({"model":model})
            
            if not exists_path(app_template_path, model_name + "_form.html"):
                with open(os.path.join(app_template_path, model_name + "_form.html" ),'w') as f:
                    f.write(template.render(context))
            
            # Model confirm delete template
            template = TemplateLoader.get_template('confirm_delete.html.template')
            context = Context({"model":model})
            
            if not exists_path(app_template_path, model_name + "_confirm_delete.html"):
                with open(os.path.join(app_template_path, model_name + "_confirm_delete.html" ),'w') as f:
                    f.write(template.render(context))
            
            # Model list template
            template = TemplateLoader.get_template('list.html.template')
            context = Context({'model':model, 
                               'verbose_name': model_class._meta.verbose_name,
                               'verbose_name_plural':model_class._meta.verbose_name_plural })
            
            if not exists_path(app_template_path, model_name + "_list.html"):
                with open(os.path.join(app_template_path, model_name + "_list.html" ),'w') as f:
                    f.write(template.render(context))
            
            
            # Model detail template
            template = TemplateLoader.get_template('detail.html.template')
            context = Context({'model':model, 
                               'fields': [ field.name for field in model_class._meta.fields] })
            
            if not exists_path(app_template_path, model_name + "_detail.html"):
                with open(os.path.join(app_template_path, model_name + "_detail.html" ),'w') as f:
                    f.write(template.render(context))
            
            # Create forms.py
            if options["forms"]:
                template = TemplateLoader.get_template("forms.py.template")
                if not exists_path(app_path, 'forms.py'):
                    mode = "w"
                    context = Context({'model': model,
                                        'app': app_name,
                                        'import_forms': True,
                                        'already_defined': False})
                else:
                    forms = imp.load_source("views",os.path.join(app_path, 'forms.py'))
                    mode = "a"
                    context = Context({'app': app_name,
                                       'model': model,
                                       'import_forms': not hasattr(forms, "forms"),
                                       'already_defined':  hasattr(forms, model+"Form")})
                with open(os.path.join(app_path, "forms.py"), mode) as f:
                    f.write(template.render(context))
                
                
            # Create views.py
            # If views.py exists (it should exists), it generates a view
            # only if one with that name doesn't already exist.
            template = TemplateLoader.get_template("views.py.template")
            generic_views = ["CreateView", "DetailView", "ListView", "UpdateView", "DeleteView"]
            if not exists_path(app_path, 'views.py'):
                mode = "w"
                context  = Context({'app': app_name,
                                    'model': model,
                                    'has_form': options['forms'],
                                    'generic_views': generic_views,
                                    'import_model': True,
                                    'import_reverse_lazy': True,
                                    'import_form': options['forms'],
                                    'create': True,
                                    'detail': True,
                                    'list': True,
                                    'update': True,
                                    'delete': True})
            else:
                views = imp.load_source("views",os.path.join(app_path, 'views.py'))
                mode ="a"
                generic_views = filter(lambda view: view not in dir(views), generic_views)
                context  = Context({'app': app_name,
                                    'model': model,
                                    'import_model': not hasattr(views, model),
                                    'import_reverse_lazy': not hasattr(views, "reverse_lazy" ),
                                    'import_form': options['forms'] and not hasattr(views, model+"Form" ),
                                    'has_form': options['forms'],
                                    'generic_views': generic_views,
                                    'create': not hasattr(views, model+"Create" ),
                                    'detail': not hasattr(views, model+"Detail" ),
                                    'list':   not hasattr(views, model+"List" ),
                                    'update': not hasattr(views, model+"Update" ),
                                    'delete': not hasattr(views, model+"Delete" )})
                
            with open(os.path.join(app_path, 'views.py'),mode) as f:
                    f.write(template.render(context))
            
                
            # Create urls.py
            template = TemplateLoader.get_template("urls.py.template")
            imports = ['url', 'patterns']
            if not exists_path(app_path, 'urls.py'):
                context  = Context({'app': app_name,
                                    'model': model,
                                    'imports':imports,
                                    'extend_urlpatterns': False })
                
                mode = "w"
            else:
                urls = imp.load_source("urls",os.path.join(app_path, 'urls.py'))
                imports = filter( lambda func: func not in dir(urls), imports)
                extend_urlpatterns = hasattr(urls, 'urlpatterns')
                    
                context  = Context({'app': app_name,
                                    'model_name':model_name, 
                                    'model': model,
                                    'imports':imports,
                                    'extend_urlpatterns': extend_urlpatterns })
                mode = "a"
            
            with open(os.path.join(app_path, 'urls.py'),mode) as f:
                    f.write(template.render(context))
            
            
            root_urlconf_path = inspect.getsourcefile(import_module(settings.ROOT_URLCONF)) 
            with open(root_urlconf_path, "r") as f:
                urls_text = "".join(f.readlines())
            with open(root_urlconf_path, "w") as f:
                extend_patterns = "\nurlpatterns+=patterns(\"\",url(r\"%s/\",include(\"%s.urls\")),)"%(model_name, app_name)
                if extend_patterns not in urls_text:
                    urls_text += extend_patterns
                f.write(urls_text)
        
            
            