# -*- coding: utf-8 -*-

import inspect
import re

from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.safestring import mark_safe

from ajax_model_listing.settings import AJAX_LIST_SETTINGS


DEFAULT_PER_PAGE = 12


default_field = lambda: {
    'th_tag_attrs': {'class': 'ajax_list_header'},
    'td_tag_attrs': lambda instance: {'class': 'ajax_list_value'},
    'column_title': None,
    'display_value': None,
    'escape_display': True,
    'link': True,
    'min_width': None,
    'order_field': None
}


def create_field(field_dict):
    field = default_field()
    
    # 'class' key in th_tag_attrs dict and td_tag_attrs function need to be concatenated
    # all other values must be overwritten
    for key, value in field_dict.items():
        if key == 'th_tag_attrs':
            for tag_name, tag_value in field_dict['th_tag_attrs'].items():
                if tag_name == 'class':
                    field['th_tag_attrs']['class'] = ' '.join(   ( field['th_tag_attrs'].get('class', '') + ' ' + field_dict['th_tag_attrs'].get('class', '') ).split()   )
                else:
                    field['th_tag_attrs'][tag_name] = tag_value
        elif key == 'td_tag_attrs':
            default_function = field['td_tag_attrs']
            field_function = field_dict.get('td_tag_attrs')
            if not field_function:
                field['td_tag_attrs'] = default_function
            else:
                def mixed_function(instance):
                    td_tags = default_function(instance)
                    td_update_attrs = field_function(instance)
                    for tag_name, tag_value in td_update_attrs.items():
                        if tag_name == 'class':
                            td_tags['class'] = ' '.join(  (td_tags.get('class', '') + ' ' + tag_value).split()  )
                        else:
                            td_tags[tag_name] = tag_value
                    return td_tags
                field['td_tag_attrs'] = mixed_function
        else:
            field[key] = value
    
    return field


default_tr_attrs = lambda: {
    'class': 'ajax_list_row'
}


def create_tr_attrs(tr_attrs_dict):
    attrs = default_tr_attrs()
    for tag_name, tag_value in tr_attrs_dict.items():
        if tag_name == 'class':
            attrs['class'] = ' '.join(   ( attrs.get('class', '') + ' ' + tr_attrs_dict.get('class', '') ).split()   )
        else:
            attrs[tag_name] = tag_value
    return attrs


class AjaxList(object):
    
    def __init__(self,
            request,
            queryset,
            fields,
            after_paginate = None,
            url = None,
            new_tab = True,
            per_page = DEFAULT_PER_PAGE,
            tr_tag_attrs = lambda instance: {},
            filter_form = None
        ):
        
        
        # ===== SET INSTANCE PROPERTIES =====
        
        assert isinstance(request, HttpRequest), 'Invalid parameter: request. It must be a django.http.HttpRequest instance.'
        assert isinstance(queryset, QuerySet), 'Invalid parameter: queryset. It must be a django.db.models.query.QuerySet instance.'
        assert isinstance(fields, (list, tuple)), 'Invalid parameter: fields: It must be a list (or tuple) that contains dicts.'
        for index, field in enumerate(fields):
            assert isinstance(field, dict), 'Invalid parameter: fields[%s]: It must be a dict.' % index
        
        self.request = request
        self.queryset = queryset
        self.fields = [ create_field(d) for d in fields ]
        # ToDo: validate parameters below:
        self.after_paginate = after_paginate
        self.url = url
        self.new_tab = new_tab
        self.per_page = per_page
        self.tr_tag_attrs = tr_tag_attrs
        self.filter_form = filter_form
        
        # ===== FILTER QUERYSET =====
        if self.filter_form:
            if filter_form.is_valid():
                self.queryset = filter_form.filter_queryset(self.queryset)
        
        # ===== ORDER QUERYSET =====
        if request.GET.get('order_by'):
            self.order_by = request.GET['order_by']
            self.queryset = self.queryset.order_by(self.order_by, 'id')
        else:
            self.order_by = None
        
        # ===== PAGINATE QUERYSET =====
        self.paginator = Paginator(self.queryset, self.per_page)
        page_no = request.GET.get('page', '1')
        if page_no.isdigit() and int(page_no) in self.paginator.page_range:
            self.page = self.paginator.page( int(page_no) )
        else:
            self.page = self.paginator.page(1)
        
        if callable(self.after_paginate):
            for obj in self.page.object_list:
                self.after_paginate(obj)
    
    def header(self):
        context = {
            'fields': self.fields,
            'order_by': self.order_by,
            'SORT_ASC_ELEMENT': AJAX_LIST_SETTINGS['SORT_ASC_ELEMENT'],
            'SORT_DESC_ELEMENT': AJAX_LIST_SETTINGS['SORT_DESC_ELEMENT']
        }
        return render(self.request, 'ajax_model_listing/list_header.html', context).content
    
    
    def body(self):
        
        # Set values for each instance
        for obj in self.page.object_list:
            
            # Set values for each field
            fields_values = []
            for field in self.fields:
                # DISPLAY VALUE
                if isinstance(field['display_value'], basestring) and hasattr(obj, field['display_value']):
                    display_value = getattr(obj, field['display_value'])
                elif inspect.isfunction(field['display_value']):
                    display_value = field['display_value'](obj)
                else:
                    raise ValueError("Field display_value invalid. Received: %s" % field['display_value'])
                
                fields_values.append({
                    'display_value': display_value,
                    'escape_display': field['escape_display'],
                    'td_tag_attrs': field['td_tag_attrs'](obj),
                    'link': field['link']
                })
            
            # Set URL
            computed_url = None
            if self.url:
                if isinstance(self.url, basestring):
                    computed_url = reverse(self.url, args=[obj.id])
                elif callable(self.url):
                    computed_url = self.url(obj)
            
            obj.computed_values = {
                'tr_tag_attrs': create_tr_attrs( self.tr_tag_attrs(obj) ),
                'fields_values': fields_values,
                'url': computed_url,
            }
            
        context = {
            'fields': self.fields,
            'page': self.page,
            'new_tab': self.new_tab,
        }
        return render(self.request, 'ajax_model_listing/list_body.html', context).content
    
    
    def foot(self):
        context = {
            'fields_count': len(self.fields),
            'page': self.page,
            'PAGE_FIRST_ELEMENT': AJAX_LIST_SETTINGS['PAGE_FIRST_ELEMENT'],
            'PAGE_PREVIOUS_ELEMENT': AJAX_LIST_SETTINGS['PAGE_PREVIOUS_ELEMENT'],
            'PAGE_NEXT_ELEMENT': AJAX_LIST_SETTINGS['PAGE_NEXT_ELEMENT'],
            'PAGE_LAST_ELEMENT': AJAX_LIST_SETTINGS['PAGE_LAST_ELEMENT'],
        }
        return render(self.request, 'ajax_model_listing/list_foot.html', context).content
    
    
    def __unicode__(self):
        html = u"<table class='ajax_list'>%s%s%s</div>" % (
            unicode(self.header(), 'utf-8'),
            unicode(self.body(), 'utf-8'),
            unicode(self.foot(), 'utf-8'),
        )
        return mark_safe(html)