### -*- coding: utf-8 -*- ####################################################

import urlparse

from django.utils.translation import ugettext, ugettext_lazy as _

from native_tags.decorators import function

from .models import get_group, get_second_level
from .utils import alphabetic_setup, term_lookup, ALPHABET_SECOND_INDEX_NAME, alphabetic_setup_second, ALPHABET_SECOND_FILTER_COUNT

PARAM_NAME = 'firstletter'

alphabetic_term = function(term_lookup, takes_request=True, name="get_alphabetic_term")
alphabetic_setup = function(alphabetic_setup, takes_request=True)
    

class Group:
    
    label = ''
    key = '' #Unique identifier
    letters = ()
    
    def __init__(self, label, key, letters):
        self.label = label
        self.key = key
        self.letters = letters

LETTERS = (
    u'0-9',
    Group(u'A-Z', "eng", (
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", 
        "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
    )), 
    Group(u'А-Я', "rus", (
        u'А', u'Б', u'В', u'Г', u'Д', u'Е', u'Ж', u'З', u'И', u'К', 
        u'Л', u'М', u'Н', u'О', u'П', u'Р', u'С', u'Т', 
        u'У', u'Ф', u'Х', u'Ц', u'Ч', u'Ш', u'Щ', u'Э', u'Ю', u'Я'
    )),
)

def show_alphabetic_filter(request, queryset, param_name=PARAM_NAME, exclude_param='page', url_fragment='', group_prefix='alphagroup-', cache_params=()):
    url_parts = list(urlparse.urlparse(request.build_absolute_uri()))
    url_parts[5] = url_fragment
    query = request.GET.copy()
    if exclude_param in query:
        del query[exclude_param]
    term = term_lookup(request, param_name)
    second_term = request.REQUEST.get(ALPHABET_SECOND_INDEX_NAME)
    second_level = get_second_level(queryset, term, cache_params)

    def get_url(param, second=False):
        if second: 
            query[param_name] = term
            query[ALPHABET_SECOND_INDEX_NAME] = param
        else:
            query[param_name] = param
            if query.has_key(ALPHABET_SECOND_INDEX_NAME):
                del query[ALPHABET_SECOND_INDEX_NAME]
        url_parts[4] = query.urlencode()
        return urlparse.urlunparse(url_parts)

    def extract_letters(items):
        expanded_group = get_group(request)
        
        # XXX: Refactor this shit. HTML must be in templates
        for item in items:
            if isinstance(item, Group):
                yield u"""
                    <span id="%(prefix)s%(key)s" class="group %(expanded)s" title="%(label)s">
                        <span>%(letters)s</span>
                        <a href="%(url)s">%(label)s</a>
                    </span>
                """  % {
                    'key': item.key, 'label': item.label, 
                    'letters': "".join(extract_letters(item.letters)),
                    'url': get_url(item.label), 'prefix': group_prefix,
                    'expanded': (item.key == expanded_group) and "expanded" or "rolled",
                }
            else:
                result = u'<a href="%(url)s" class="{0}">%(letter)s</a>'.format('selected' if term == item else '')
                yield result % {'url': get_url(item), 'letter': item or ugettext("...")}
    
    # XXX: Refactor this shit. HTML must be in templates
    def extract_second_level(items):
        for i, item in enumerate(items):
            result = u'<span class="selected">%(item)s</span>' \
                     if second_term and (int(second_term) == i) \
                     else '<a href="%(url)s">%(item)s</a>'
            yield result % {'url': get_url(i, True), 'item': item }
    
    return 'alphabetic/fragment.html', {
        'letters': extract_letters(('',) + LETTERS),
        'second_level': extract_second_level(second_level.values()) if second_level else [],
        'prefix': group_prefix,
        'request': request
    }
show_alphabetic_filter = function(show_alphabetic_filter, takes_request=1, inclusion=True)
