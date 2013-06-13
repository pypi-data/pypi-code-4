# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET


def _convert_to_xml_recurse(parent, data, renderers={}):
    """helper function for converting given data var to xml"""
    #Iterating through a dict and creating parts of xml like <key></key>
    if isinstance(data, dict):
        for (tag, child) in sorted(data.iteritems()):
            if isinstance(child, list) or isinstance(child, tuple):
                #Creating xml element from dict key
                listelem = ET.Element(tag)
                parent.append(listelem)
                # iterating through list or tuple and convert
                for listchild in child:
                    elem = ET.Element('item')
                    listelem.append(elem)
                    #Recurse calling with dict value
                    _convert_to_xml_recurse(elem, listchild, renderers=renderers)
            else:
                #Creating xml element from dict key
                elem = ET.Element(tag)
                parent.append(elem)
                #Recurse calling with dict value
                _convert_to_xml_recurse(elem, child, renderers=renderers)
    #Same thing for lists and tuples, parts are like <item></item>
    elif isinstance(data, list) or isinstance(data, tuple):
        for child in data:
            elem = ET.Element('item')
            parent.append(elem)
            #Recurse calling with list or tuple item
            _convert_to_xml_recurse(elem, child, renderers=renderers)
    #If data not list, tuple or dict, then adding its value to its parent (filling element with value)
    else:
        for r in renderers.iteritems():
            if isinstance(data, r[0]):
                parent.text = str(r[1](data))
                break
        else:
            try:
                parent.text = unicode(data)
            except UnicodeDecodeError:
                parent.text = data.decode('utf8')


def dumps(data, renderers={}):
    """Creates xml string from data variable with structure like
    Does work with anything that can be passed to 'str' class construcor
    <?xml version='1.0' encoding='utf-8'?>
    <data>
        data here
    </data>

    >>> dumps(TEST_DATA_DICT)
    "<?xml version='1.0' encoding='utf-8'?><data><now>2000-02-15 13:33:54</now><some_dict><a>string value</a><b><item>list</item><item>&#1092;&#1099;&#1074;</item></b><c><nested>dictionary</nested></c><d><item>a</item><item>3</item><item>tuple</item></d></some_dict><some_list><item>Python</item><item>XML</item><item>Pyramid</item></some_list><some_object>object data</some_object></data>"

    >>> dumps(TEST_DATA_LIST)
    "<?xml version='1.0' encoding='utf-8'?><data><item><item>1</item><item>2</item><item>3</item></item><item><now>2000-02-15 13:33:54</now><some_dict><a>string value</a><b><item>list</item><item>&#1092;&#1099;&#1074;</item></b><c><nested>dictionary</nested></c><d><item>a</item><item>3</item><item>tuple</item></d></some_dict><some_list><item>Python</item><item>XML</item><item>Pyramid</item></some_list><some_object>object data</some_object></item><item>string</item><item>10</item></data>"

    >>> dumps(dict(a=''))
    "<?xml version='1.0' encoding='utf-8'?><data><a /></data>"

    >>> dumps('')
    "<?xml version='1.0' encoding='utf-8'?><data />"

    >>> dumps(1)
    "<?xml version='1.0' encoding='utf-8'?><data>1</data>"

    >>> dumps([1, 2, 3, [1, 2, 3, [1, 2, 3]]])
    "<?xml version='1.0' encoding='utf-8'?><data><item>1</item><item>2</item><item>3</item><item><item>1</item><item>2</item><item>3</item><item><item>1</item><item>2</item><item>3</item></item></item></data>"

    >>> dumps(1)
    "<?xml version='1.0' encoding='utf-8'?><data>1</data>"

    >>> dumps(None)
    "<?xml version='1.0' encoding='utf-8'?><data>None</data>"

    >>> dumps(0)
    "<?xml version='1.0' encoding='utf-8'?><data>0</data>"

    >>> dumps(False)
    "<?xml version='1.0' encoding='utf-8'?><data>False</data>"

    >>> dumps(' ')
    "<?xml version='1.0' encoding='utf-8'?><data> </data>"

    >>> dumps()
    Traceback (most recent call last):
     ...
    TypeError: dumps() takes at least 1 argument (0 given)
    """

    root = ET.Element('data')
    _convert_to_xml_recurse(root, data, renderers)
    return "<?xml version='1.0' encoding='utf-8'?>" + ET.tostring(root)


if __name__ == "__main__":
    from datetime import datetime
    import doctest

    NOW = datetime(year=2000, month=2, day=15, hour=13, minute=33, second=54)

    class Model(object):
        def __init__(self, data):
            self.data = data

        def __str__(self):
            return self.data

    TEST_DATA_DICT = {
        'now': NOW,
        'some_list': ['Python', 'XML', 'Pyramid'],
        'some_dict': {
            'a': 'string value',
            'b': ['list', 'фыв'],
            'c': {'nested': 'dictionary'},
            'd': ('a', 3, 'tuple', )
        },
        'some_object': Model('object data')
    }

    TEST_DATA_LIST = [[1, 2, 3], {
        'now': NOW,
        'some_list': ['Python', 'XML', 'Pyramid'],
        'some_dict': {
            'a': 'string value',
            'b': ['list', 'фыв'],
            'c': {'nested': 'dictionary'},
            'd': ('a', 3, 'tuple', )
        },
        'some_object': Model('object data')
    }, 'string', Model('10')]

    doctest.testmod()
