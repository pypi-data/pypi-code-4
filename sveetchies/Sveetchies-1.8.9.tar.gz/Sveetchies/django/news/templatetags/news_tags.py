# -*- coding: utf-8 -*-
#
# Template tags pour les catégories et billets
#
from django import template
from django.utils.safestring import mark_safe

from Sveetchies.django.utils import get_string_or_variable

from Sveetchies.django.news import NEWS_LASTNEWS_TAGS_TEMPLATE
from Sveetchies.django.news.models import Category, Entry

register = template.Library()

@register.tag(name="last_news_entries")
def do_last_news_entries(parser, token):
    """
    Lecture de préparation du Tag
   
    Derniers billets toute catégorie : ::
    
        {% last_news_entries limit %}
    
    Derniers billets de la catégorie 'category_id' : ::
    
        {% last_news_entries limit category_id %}
    
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify a limit"
    else:
        return last_news_entries(*args[1:])

class last_news_entries(template.Node):
    """
    Génération du rendu html du tag "last_news_entries"
    """
    def __init__(self, limit, category_id=None, templatepath=None):
        self.limit = limit
        self.category_id = category_id
        self.templatepath = templatepath
    
    def render(self, context):
        string = ''
        category_object = None
        limit = get_string_or_variable(self.limit, context, capture_none_value=False)
        
        category_id = get_string_or_variable(self.category_id, context, capture_none_value=True)
        if category_id:
            category_object = Category.objects.get(pk=int(category_id))
        
        templatepath = NEWS_LASTNEWS_TAGS_TEMPLATE
        if self.templatepath:
            templatepath = get_string_or_variable(self.templatepath, context, capture_none_value=True)
        
        entries_queryset = Entry.objects.publishable_filter()
        if category_object:
            entries_queryset = entries_queryset.filter(category=category_object)
        entries_queryset = entries_queryset.order_by('-publish_date')[:limit]
            
        context.update({
            'last_news_limit' : limit,
            'last_news_category_object' : category_object,
            'last_news_object_list' : entries_queryset,
        })
        string = template.loader.get_template(templatepath).render(template.Context(context))
        
        return mark_safe( string )
