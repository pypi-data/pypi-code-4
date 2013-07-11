# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import get_model
from djaloha import settings

def aloha_init(request):
    """
    Build the javascript file which is initializing the aloha-editor
    Run the javascript code for the AlohaInput widget
    """
    
    links = []
    for full_model_name in settings.link_models():
        app_name, model_name = full_model_name.split('.')
        model = get_model(app_name, model_name)
        if model:
            links.extend(model.objects.all())

    return render_to_response(
        settings.init_js_template(),
        {
            'links': links,
            'config':{
                'jquery_no_conflict': settings.jquery_no_conflict(),
                'sidebar_disabled': 'true' if settings.sidebar_disabled() else 'false',
                'css_classes': settings.css_classes(),
                'resize_disabled': settings.resize_disabled(),
            },
        },
        mimetype='text/javascript',
        context_instance=RequestContext(request)
    )
