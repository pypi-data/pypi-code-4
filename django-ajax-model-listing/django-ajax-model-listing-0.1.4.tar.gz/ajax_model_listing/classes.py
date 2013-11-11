# -*- coding: utf-8 -*-

import inspect
import re

from django.db.models.query import QuerySet
from django.conf import settings
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.http import HttpRequest
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe

from ajax_model_listing.settings import AJAX_LIST_SETTINGS


DEFAULT_PER_PAGE = 12


# ===== FIELDS HELPERS =====

default_field = lambda: {
    'th_tag_attrs': {'class': 'ajax_list_header'},
    'td_tag_attrs': lambda instance: {'class': 'ajax_list_value'},
    'column_title': None,
    'display_value': None,
    'escape_display': True,
    'link': True,
    'order_field': None
}

def create_field(list_order_by, field_dict):
    # 'class' key in th_tag_attrs dict and td_tag_attrs function need to be concatenated
    # all other values must be overwritten
    
    field = default_field()
    
    if not field_dict.get('th_tag_attrs'):
        field_dict['th_tag_attrs'] = {}
    
    # TR classes that deal with the list ordering
    th_classes = field['th_tag_attrs'].get('class', '').split()
    field_order_by = field_dict.get('order_field')
    if field_order_by:
        th_classes.append('ajax_list_sorter')
        if list_order_by:
            if list_order_by == field_order_by:
                th_classes.extend(['ajax_list_sorter_asc', 'active_sort'])
            elif list_order_by == '-' + field_order_by:
                th_classes.extend(['ajax_list_sorter_desc', 'active_sort'])
    th_classes = ' '.join(th_classes)
    
    for key, value in field_dict.items():
        if key == 'th_tag_attrs':
            field['th_tag_attrs']['class'] = th_classes
            for tag_name, tag_value in field_dict['th_tag_attrs'].items():
                if tag_name == 'class':
                    field['th_tag_attrs']['class'] += ' ' + field_dict['th_tag_attrs'].get('class', '')
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


# ===== TR HELPERS =====

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


# ===== TABLE HELPERS =====

default_table_attrs = lambda: {
    'class': 'ajax_list'
}

def create_table_attrs(table_attrs_dict):
    attrs = default_table_attrs()
    for tag_name, tag_value in table_attrs_dict.items():
        if tag_name == 'class':
            attrs['class'] = ' '.join(   ( attrs.get('class', '') + ' ' + table_attrs_dict.get('class', '') ).split()   )
        else:
            attrs[tag_name] = tag_value
    return attrs


# ===== MAIN CLASS =====

class AjaxList(object):
    
    def __init__(self,
            request,
            queryset,
            fields,
            after_paginate = None,
            url = None,
            new_tab = True,
            per_page = DEFAULT_PER_PAGE,
            table_tag_attrs = {},
            tr_tag_attrs = lambda instance: {},
            filter_form = None,
            custom_table_foot_template = None,
            show_records_count = None
        ):
        
        # ===== SET INSTANCE PROPERTIES =====
        
        assert isinstance(request, HttpRequest), 'Invalid parameter: request. It must be a django.http.HttpRequest instance.'
        assert isinstance(queryset, QuerySet), 'Invalid parameter: queryset. It must be a django.db.models.query.QuerySet instance.'
        assert isinstance(fields, (list, tuple)), 'Invalid parameter: fields: It must be a list (or tuple) that contains dicts.'
        for index, field in enumerate(fields):
            assert isinstance(field, dict), 'Invalid parameter: fields[%s]: It must be a dict.' % index
        # ToDo: validate parameters: after_paginate, url, new_tab, per_page, table_tag_attrs, tr_tag_attrs, filter_form, custom_table_foot_template, show_records_count
        
        self.request = request
        self.queryset = queryset
        
        # ===== FILTER QUERYSET =====
        self.filter_form = filter_form
        if self.filter_form:
            if filter_form.is_valid():
                self.queryset = filter_form.filter_queryset(self.queryset)
        
        # ===== ORDER QUERYSET =====
        if request.GET.get('order_by'):
            self.order_by = request.GET['order_by']
            self.queryset = self.queryset.order_by(self.order_by, 'id')
        else:
            self.order_by = None
        
        self.fields = [ create_field(self.order_by, d) for d in fields ]
        self.after_paginate = after_paginate
        self.url = url
        self.new_tab = new_tab
        self.per_page = per_page
        self.table_tag_attrs = table_tag_attrs
        self.tr_tag_attrs = tr_tag_attrs
        self.custom_table_foot_template = custom_table_foot_template
        self.show_records_count = show_records_count or AJAX_LIST_SETTINGS['SHOW_RECORDS_COUNT']
        
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
    
    def head(self):
        context = {
            'fields': self.fields,
            'order_by': self.order_by
        }
        return render_to_response('ajax_model_listing/list_head.html', context).content
    
    
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
                
                if display_value == None:
                    display_value = ''
                
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
        return render_to_response('ajax_model_listing/list_body.html', context).content
    
    
    def foot(self):
        context = {
            'fields_count': len(self.fields),
            'page': self.page,
            'PAGE_FIRST_ELEMENT': AJAX_LIST_SETTINGS['PAGE_FIRST_ELEMENT'],
            'PAGE_PREVIOUS_ELEMENT': AJAX_LIST_SETTINGS['PAGE_PREVIOUS_ELEMENT'],
            'PAGE_NEXT_ELEMENT': AJAX_LIST_SETTINGS['PAGE_NEXT_ELEMENT'],
            'PAGE_LAST_ELEMENT': AJAX_LIST_SETTINGS['PAGE_LAST_ELEMENT'],
            'SHOW_RECORDS_COUNT': self.show_records_count,
        }
        foot_template = self.custom_table_foot_template or 'ajax_model_listing/list_foot.html'
        return render_to_response(foot_template, context).content
    
    
    def __unicode__(self):
        context = {
            'STATIC_URL': settings.STATIC_URL,
            'table_attrs': create_table_attrs(self.table_tag_attrs),
            'thead': self.head(),
            'tfoot': self.body(),
            'tbody': self.foot(),
        }
        html = render_to_response('ajax_model_listing/list.html', context).content
        return mark_safe( unicode(html, 'utf-8') )