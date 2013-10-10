# Note, this library is free software
# Copyright 2010 FreeCode AS
# Licensed under the MIT license

from django import template
import mezzanine.pages.models

register = template.Library()


@register.filter
def get_page_content(slug_name):
    try:
        page = mezzanine.pages.models.ContentPage.objects.get(slug=slug_name)
        if page is not None:
            return page.content
            
    except:
        print "Error: unable to get mezzanine page:", slug_name
        return "Missing article: /" + slug_name
    
    return ""

@register.filter
def get_page_title(slug_name):
    try:
        page = mezzanine.pages.models.ContentPage.objects.get(slug=slug_name)
        if page is not None:
            return page.title
            
    except:
        print "Error: unable to get mezzanine page:", slug_name
        return "Missing article: /" + slug_name
    
    return ""
