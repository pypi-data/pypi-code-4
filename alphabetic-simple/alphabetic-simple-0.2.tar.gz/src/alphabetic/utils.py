### -*- coding: utf-8 -*- ####################################################
from django.utils.datastructures import SortedDict
from django.conf import settings

from .models import set_second_level, get_second_level

PARAM_NAME = 'firstletter'
ALPHABET_SECOND_INDEX_NAME = getattr(settings, 'ALPHABET_SECOND_INDEX_NAME', 'second_level_letters')
ALPHABET_SECOND_FILTER_COUNT = getattr(settings, 'ALPHABET_SECOND_FILTER_COUNT', 6)
ALPHABET_SECOND_PREFIX_LETTERS = getattr(settings, 'ALPHABET_SECOND_PREFIX_LETTERS', 3)

def term_lookup(request, param_name=PARAM_NAME):
    return request.REQUEST.get(param_name, '')
    
def alphabetic_setup(request, object_list, field_name='title', param_name=PARAM_NAME, 
                     second=False, second_cache_timeout=3600, cache_params=()):
    """
        Returns ordered queryset by field_name

        - **object_list** -- queryset to sort
        - **field_name** -- name of the field to sort by. Default: title.
        - **param_name** -- name of the param appended to the url when clicked on the letter at index.
                            Default: firstletter.
    """
    term = term_lookup(request, param_name)
    if term:
        if hasattr(object_list, 'filter_and'): # for haystack support
            object_list = object_list.filter_and(**{"%s__startswith" % field_name: term})
        elif hasattr(object_list, 'filter'):
            object_list = object_list.filter(**{"%s__iregex" % field_name: r'^[%s]' % term})
        else:
            object_list = filter(lambda obj: getattr(obj, field_name).startswith(term), object_list)
        if second:
            alphabet_second = get_second_level(object_list, term, cache_params)
            if not alphabet_second:
                alphabet_second = alphabetic_setup_second(
                    object_list.order_by(field_name) if hasattr(object_list, 'order_by') else object_list,
                    field_name
                )
                if alphabet_second:
                    set_second_level(object_list, term, alphabet_second, second_cache_timeout, cache_params)
            if alphabet_second:
                object_list = filter_queryset_second(request, object_list, alphabet_second, field_name)
    return object_list

def filter_queryset_second(request, queryset, alphabet_second, field_name):
    second_term = request.REQUEST.get(ALPHABET_SECOND_INDEX_NAME)
    if not second_term:
        return queryset
    else:
        second_term = int(second_term)
    if hasattr(queryset, 'order_by'):
        queryset = queryset.order_by(field_name)
    if second_term >= len(alphabet_second) - 1:
        end = getattr(queryset, 'count', '__len__')()
        return queryset[alphabet_second.keys()[len(alphabet_second) - 1]:end]
    return queryset[alphabet_second.keys()[second_term]:alphabet_second.keys()[second_term + 1]] 


def alphabetic_setup_second(queryset, field_name='title'):
    prefixes = alphabetic_second_get_prefixes(queryset, field_name)
    if not prefixes:
        return None
    prefixes_count = len(prefixes.items())
    if prefixes_count <= ALPHABET_SECOND_FILTER_COUNT:
        return prefixes
    else:
        single_prefixes_count = ALPHABET_SECOND_FILTER_COUNT * 2 - prefixes_count
        intervals = SortedDict()
        cached = None
        prefixes = prefixes.items()
        for i in range(prefixes_count):
            if not cached and prefixes_count - i > single_prefixes_count:
                cached = prefixes[i]
            else:
                if cached:
                    intervals[cached[0]] = "%s-%s" % (cached[1], prefixes[i][1])
                    cached = None
                else:
                    intervals[prefixes[i][0]] = prefixes[i][1]
        return intervals


def get_second_level_letters(obj, field_name):
    return getattr(obj, field_name)[:ALPHABET_SECOND_PREFIX_LETTERS]


def alphabetic_second_get_prefixes(queryset, field_name='title'):
    queryset_count = getattr(queryset, 'count', '__len__')()
    count_per_item = 1.0 * queryset_count / ALPHABET_SECOND_FILTER_COUNT
    if count_per_item >= 1:
        count_per_item = int(count_per_item)
        item = get_second_level_letters(queryset[0], field_name)
        prefixes = SortedDict({ 0: item })
        curr_index = 0
        for i in range(1, ALPHABET_SECOND_FILTER_COUNT + 1):
            if len(prefixes.items()) == ALPHABET_SECOND_FILTER_COUNT * 2 - 1:
                curr_index = queryset_count - 1
            else:
                curr_index = count_per_item * i - 1 if curr_index <= count_per_item * i - 1 else curr_index + 1

            for j in range(2):
                curr_index, item = alphabetic_second_get_str(queryset, field_name, curr_index, queryset_count, item)
                if curr_index and item:
                    prefixes[curr_index] = item
                else:
                    break
        return prefixes

def alphabetic_second_get_str(queryset, field_name, curr_index, queryset_count, prev_str):
    curr_str = None
    while curr_index < queryset_count and (curr_str == prev_str or not curr_str):
        curr_str = get_second_level_letters(queryset[curr_index], field_name)
        curr_index += 1

    if curr_str and curr_str != prev_str:
        return curr_index - 1, curr_str
    else:
        return None, None

#def alphabetic_setup_second(queryset, field_name='title'):
#    queryset_count = queryset.count() if hasattr(queryset, 'model') else len(queryset)
#    alphabet_second_count = 1.0 * queryset_count / ALPHABET_SECOND_FILTER_COUNT
#    if alphabet_second_count >= 1:
#        alphabet_second_count = int(round(alphabet_second_count))
#        alphabet_second = SortedDict({ 0: getattr(queryset[0], field_name)[:ALPHABET_SECOND_PREFIX_LETTERS] })
#        next_index = 0
#        for i in range(1, ALPHABET_SECOND_FILTER_COUNT):
#            index = alphabet_second_count * i - 1
#            if next_index > index:
#                index = next_index
#            prefix = getattr(queryset[index], field_name)[:ALPHABET_SECOND_PREFIX_LETTERS]
#            next_index = index + 1
#            while next_index < queryset_count - 1 and prefix == getattr(queryset[next_index], field_name)[:ALPHABET_SECOND_PREFIX_LETTERS]:
#                next_index += 1
#            if next_index - index > alphabet_second_count:
#                continue
#            key, value = alphabet_second.items()[-1]
#            alphabet_second[key] = "%s-%s" % (value, prefix)
#            alphabet_second[next_index] = getattr(queryset[next_index], field_name)[:ALPHABET_SECOND_PREFIX_LETTERS]
#            if next_index > queryset_count - 1:
#                break
#        key, value = alphabet_second.items()[-1]
#        alphabet_second[key] = "%s-%s" % (value, getattr(queryset[queryset_count - 1], field_name)[:ALPHABET_SECOND_PREFIX_LETTERS])
##        import pdb; pdb.set_trace()
#        return alphabet_second