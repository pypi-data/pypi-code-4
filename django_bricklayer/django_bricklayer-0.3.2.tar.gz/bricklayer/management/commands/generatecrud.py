from django.conf import settings
from django.core.management.base import AppCommand
from django.db.models import get_models, get_model
from django.template import loader as TemplateLoader, Context
from django.utils.module_loading import import_module
from bricklayer.utils import exists_dir, exists_path, is_blank
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
        make_option('--form', '-f', 
                    dest='forms',
                    action="store_true",
                    default=False,
                    help='Generate a ModelForm for each model'),
        make_option('-c', 
                    dest='create',
                    action="store_true",
                    default=False,
                    help='Prevent create view from being generated'),
        make_option('-r', 
                    dest='read',
                    action="store_true",
                    default=False,
                    help='Prevent list and detial view from being generated'),
        make_option('-u', 
                    dest='update',
                    action="store_true",
                    default=False,
                    help='Prevent update view from being generated'),
        make_option('-d', 
                    dest='delete',
                    action="store_true",
                    default=False,
                    help='Prevent delete view from being generated'),
                                            
                                        
    )
    

    def handle_app(self, app, **options):
                
        # Check if multiple model are passed as arguments
        if options['models'] and ',' in options['models']:
            options['models'] = options['models'].split(',')
        else:
            options['models'] = [ options['models'] ]
        
        is_verbose = options['verbosity'] >= 1
        # some useful shortcuts
        app_models = [model._meta.object_name for model in get_models(app)]
        models = options['models'] or app_models
        app_name = app.__name__.split('.')[-2]
        app_path = os.path.dirname(app.__file__)
        template_path = os.path.join(app_path, 'templates')
        app_template_path = os.path.join(app_path, 'templates', app_name)
       
        # Test if models exists in the app
        if options['models']:
            models = [ model for model in options['models'] if model in app_models ]
        
        # Set which views are going to be generated
        generic_views = ["CreateView", "DetailView", "ListView", "UpdateView", "DeleteView"]
        if options['create']:
            generic_views.remove("CreateView")
        
        if options['read']:
            generic_views.remove("DetailView")
            generic_views.remove("ListView")
        
        if options['update']:
            generic_views.remove("UpdateView")
            
        if options['delete']:
            generic_views.remove("DeleteView")
                
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
            if not exists_path(app_template_path, model_name + "_form.html"):
                template = TemplateLoader.get_template('form.html.template')
                context = Context({"model":model})
                with open(os.path.join(app_template_path, model_name + "_form.html" ),'w') as f:
                    f.write(template.render(context))
            
            # Model confirm delete template
            if not exists_path(app_template_path, model_name + "_confirm_delete.html") and "DeleteView" in generic_views:
                template = TemplateLoader.get_template('confirm_delete.html.template')
                context = Context({"model":model})
                with open(os.path.join(app_template_path, model_name + "_confirm_delete.html" ),'w') as f:
                    f.write(template.render(context))
            
            # Model list template
            
            if not exists_path(app_template_path, model_name + "_list.html") and "ListView" in generic_views:
                template = TemplateLoader.get_template('list.html.template')
                context = Context({'model':model, 
                                   'verbose_name': model_class._meta.verbose_name,
                                   'verbose_name_plural':model_class._meta.verbose_name_plural })
                with open(os.path.join(app_template_path, model_name + "_list.html" ),'w') as f:
                    f.write(template.render(context))
            
            
            # Model detail template
            if not exists_path(app_template_path, model_name + "_detail.html") and "DetailView" in generic_views:
                template = TemplateLoader.get_template('detail.html.template')
                context = Context({'model':model, 
                                   'fields': [ field.name for field in model_class._meta.fields] })
                with open(os.path.join(app_template_path, model_name + "_detail.html" ),'w') as f:
                    f.write(template.render(context))
            
            # Create forms.py
            if options["forms"]:
                from bricklayer.management.commands import GenerateFormCommand
                import copy
                command = GenerateFormCommand()
                form_options = copy.copy(options)
                form_options["models"] = model
                command.handle_app(app, **form_options)
                
            # Create views.py
            # If views.py exists (it should exists), it generates a view
            # only if one with that name doesn't already exist.
            template = TemplateLoader.get_template("views.py.template")
            
            if not exists_path(app_path, 'views.py') or is_blank(app_path, "views.py"):
                mode = "w"
                context  = Context({'app': app_name,
                                    'model': model,
                                    'has_form': options['forms'],
                                    'generic_views': generic_views,
                                    'import_model': True,
                                    'import_reverse_lazy': True,
                                    'import_form': options['forms'],
                                    'create': "CreateView" in generic_views,
                                    'detail': "DetailView" in generic_views,
                                    'list':   "ListView"   in generic_views,
                                    'update': "UpdateView" in generic_views,
                                    'delete': "DeleteView" in generic_views})
            else:
                views_module = dir( imp.load_source("views",os.path.join(app_path, 'views.py')) )
                mode ="a"
                generic_views = filter(lambda view: view not in views_module, generic_views)
                context  = Context({'app': app_name,
                                    'model': model,
                                    'import_model': model not in views_module,
                                    'import_reverse_lazy': "reverse_lazy" not in views_module ,
                                    'import_form': options['forms'] and model+"Form" not in views_module ,
                                    'has_form': options['forms'],
                                    'generic_views': generic_views,
                                    'create': model+"Create" not in views_module and "CreateView" in generic_views,
                                    'detail': model+"Detail" not in views_module and "DetailView" in generic_views,
                                    'list':   model+"List"   not in views_module and "ListView"   in generic_views,
                                    'update': model+"Update" not in views_module and "UpdateView" in generic_views,
                                    'delete': model+"Delete" not in views_module and "DeleteView" in generic_views})
                
            with open(os.path.join(app_path, 'views.py'),mode) as f:
                    f.write(template.render(context))
            
                
            # Create urls.py
            template = TemplateLoader.get_template("urls.py.template")
            imports = ['url', 'patterns']
            generic_view_types = map(lambda v: v.replace("View",""), generic_views) 
            if not exists_path(app_path, 'urls.py'):
                context  = Context({'app': app_name,
                                    'model': model,
                                    'imports':imports,
                                    'extend_urlpatterns': False,
                                    'generic_view_types':generic_view_types })
                
                mode = "w"
            else:
                urls_module = dir( imp.load_source("urls",os.path.join(app_path, 'urls.py')) )
                imports = filter( lambda func: func not in urls_module, imports)
                extend_urlpatterns = 'urlpatterns' in urls_module
                    
                context  = Context({'app': app_name,
                                    'model_name':model_name, 
                                    'model': model,
                                    'imports':imports,
                                    'extend_urlpatterns': extend_urlpatterns,
                                    'generic_view_types': generic_view_types })
                mode = "a"
            
            with open(os.path.join(app_path, 'urls.py'),mode) as f:
                    f.write(template.render(context))
            
            
            root_urlconf_path = inspect.getsourcefile(import_module(settings.ROOT_URLCONF)) 
            with open(root_urlconf_path, "r") as f:
                urls_text = "".join(f.readlines())
            with open(root_urlconf_path, "a") as f:
                extend_patterns = "\nurlpatterns+=patterns(\"\",url(r\"%s/\",include(\"%s.urls\")),)"%(model_name, app_name)
                if extend_patterns not in urls_text:
                    f.write(extend_patterns)
        
            
            