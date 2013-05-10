import json
import re


KEYS_TO_REMOVE = ('avatar', 'creator_id', 'owner_id', 'assignee_id')


# TODO: Docstring
def dump_dict(dictionary):
    for key in KEYS_TO_REMOVE:
        dictionary.pop(key, '')
    for key, val in dictionary.iteritems():
        if key in ('creator', 'assignee'):
            try:
                dictionary[key] = val['nick']
            except TypeError:
                dictionary[key] = 'none'
        if isinstance(val, unicode) and len(val) > 60:
            dictionary[key] = u'\n\n    {0}\n\n'.format(val)

    dumped = json.dumps(dictionary, indent=2)
    cleaned = re.sub('[{},"]', '', dumped)
    return cleaned.replace('\\n', '\n')


# TODO: Docstring
def print_title(title, decoration='-'):
    return u'{:^80}'.format(
        title.replace('_', ' ').upper()
    ).replace('  ', decoration * 2)


# TODO: Docstring
# TODO: Optimalization of some kind
def pretty_print(response):
    output = []
    if response.get('data'):

        if isinstance(response['data'], dict):

            for key, val in response['data'].iteritems():

                if isinstance(val, list):
                    output.append(print_title(key, '='))
                    for i, el in enumerate(val):
                        output.append(dump_dict(el))
                        if not len(val) - 1 == i:
                            output.append('-'*80)
                elif isinstance(val, dict):
                    output.append(print_title(key, '-'))
                    output.append(dump_dict(val))
                else:
                    output.append('{0}: {1}'.format(
                        key.replace('_', ' ').upper(), val)
                    )

        elif isinstance(response['data'], list):
            for val in response['data']:
                output.append('='*80)
                if isinstance(val, list):
                    output.append('-'*80)
                    for el in val:
                        output.append(dump_dict(el))
                    output.append('-'*80)
                elif isinstance(val, dict):
                    output.append(dump_dict(val))
        output.append('='*80)
    elif response.get('message'):
        output.append(response['message'])
    print('\n'.join(output))
