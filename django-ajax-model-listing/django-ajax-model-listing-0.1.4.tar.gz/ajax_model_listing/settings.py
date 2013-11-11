# -*- coding: utf-8 -*-


from django.conf import settings


AJAX_LIST_SETTINGS = {
    'PAGE_FIRST_ELEMENT':   '<span>&lt;&lt;</span>',
    'PAGE_PREVIOUS_ELEMENT':'<span>&lt;</span>',
    'PAGE_NEXT_ELEMENT':    '<span>&gt;</span>',
    'PAGE_LAST_ELEMENT':    '<span>&gt;&gt;</span>',
    'SHOW_RECORDS_COUNT':   True
}


AJAX_LIST_SETTINGS.update( getattr(settings, 'AJAX_LIST_SETTINGS', lambda: {})() )