# -*- coding: utf-8 -*-


from django.conf import settings


AJAX_LIST_SETTINGS = {
    'show_records_count': True,
    'per_page': 12,
    'table_foot_template': 'ajax_model_listing/list_foot.html',
    'table_tag_attrs': {},
    'sort_icon_default': '%sajax_model_listing/sort_icons/sort_both.png' % settings.STATIC_URL,
    'sort_icon_asc': '%sajax_model_listing/sort_icons/sort_asc.png' % settings.STATIC_URL,
    'sort_icon_desc': '%sajax_model_listing/sort_icons/sort_desc.png' % settings.STATIC_URL,
}


AJAX_LIST_SETTINGS.update( getattr(settings, 'AJAX_LIST_SETTINGS', lambda: {})() )