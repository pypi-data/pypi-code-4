# coding: utf-8
from __future__ import unicode_literals, print_function
import __main__ as main
from collections import OrderedDict
import json
import requests
try:  # pragma: no cover - Python 2.x
    import urlparse
    def is_string(text):
        return isinstance(text, (str, unicode))
except ImportError:  # pragma: no cover - Python 3.x
    import urllib.parse as urlparse
    def is_string(text):
        return isinstance(text, str)

version = '0.4.0'


def get(url):
    transport = RequestsTransport()
    return transport.get(url)

def loads(bytes):
    transport = RequestsTransport()
    return transport.loads(bytes)

def dumps(doc, indent=None):
    return json.dumps(doc, cls=DocJSONEncoder, indent=indent)


### Exceptions

class ParseError(Exception):
    """
    Raised when invalid DocJSON content is encountered.
    """
    pass


class DocumentError(Exception):
    """
    Raised when the DocJSON document contains a 'meta.error' attribute.
    """
    pass


### Transport layers

class BaseTransport(object):
    def get(self, url):
        """
        Makes an HTTP GET request and returns the resulting `Document` object.
        """
        return self._request('GET', url)

    def loads(self, bytes):
        """
        Takes a docjson bytestring and returns the resulting `Document` object.
        """
        try:
            data = json.loads(bytes, object_pairs_hook=OrderedDict)
        except ValueError as exc:
            raise ParseError('Malformed JSON - ' + str(exc))

        # Ensure we have a valid document.
        if not isinstance(data, OrderedDict):
            raise ParseError('Expected a DocJSON document, but got %s' % type(data).__name__)
        if not '_type' in data:
            raise ParseError('Document missing "_type": "document"')
        if data['_type'] != 'document':
            raise ParseError('Document should have "_type": "document", but had incorrect "_type": "%s"' % data['_type'])
        if 'meta' not in data:
            raise ParseError('Document missing "meta" attribute')
        if not isinstance(data['meta'], OrderedDict):
            raise ParseError('Document "meta" attribute should be an object but got %s' % type(data['meta']).__name__)
        if '_type' in data['meta']:
            raise ParseError('Document "meta" attribute should be a plain json object, not "_type": "%s"' % data['meta']['_type'])
        if 'error' in data['meta'] and not is_string(data['meta']['error']):
            raise ParseError('Document "meta.error" attribute should be a string, but got %s' % type(data['meta']['error']).__name__)
        if 'error' in data['meta']:
            raise DocumentError(data['meta']['error'])
        if 'url' not in data['meta']:
            raise ParseError('Document missing "meta.url" attribute')
        if not is_string(data['meta']['url']):
            raise ParseError('Document "meta.url" attribute should be a string, but got %s' % type(data['meta']['url']).__name__)

        # Ensure the meta.url attribute is valid.
        base_url = data['meta']['url']
        url_components = urlparse.urlparse(base_url)
        if base_url == '':
            raise ParseError('Document contained empty "meta.url" attribute')
        if url_components.scheme.lower() not in ['http', 'https']:
            raise ParseError('Document "meta.url" attribute should be "http" or "https", but got "%s"' % url_components.scheme)
        if not url_components.netloc:
            raise ParseError('Document "meta.url" attribute missing hostname')

        # Ignore 'title' and 'description' if they use non-string values.
        if not is_string(data['meta'].get('title', '')):
            data['meta'].pop('title')
        if not is_string(data['meta'].get('description', '')):
            data['meta'].pop('description')

        # Ignore anything in 'meta' that is not 'url', 'title', or 'description'
        for key in data['meta']:
            if key not in ('url', 'title', 'description'):
                data['meta'].pop(key)

        # Parse all the items in the document.
        data.pop('_type')
        parsed = OrderedDict()
        for key, value in data.items():
            parsed[key] = self._parse(value, base_url)

        # Return the document instance.
        return self._create_document(parsed)

    def _request(self, method, url, **opts):
        """
        Makes an HTTP request and returns the resulting `Document` object.
        """
        raise NotImplementedError('_request() method must be implemented')

    def _parse(self, data, base_url):
        """
        Given some parsed JSON data, returns the corresponding DocJSON objects.
        """
        if isinstance(data, OrderedDict) and data.get('_type') == 'link':
            if 'url' not in data:
                raise ParseError('Link missing "url" attribute')
            if not is_string(data['url']):
                raise ParseError('Link "url" should be a string, but got %s' % type(data['url']).__name__)
            if 'method' in data and not is_string(data['method']):
                raise ParseError('Link "method" should be a string, but got %s' % type(data['method']).__name__)
            if 'method' in data and data['method'].upper() not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'):
                raise ParseError('Link contained invalid method "%s"' % data['method'])
            if 'fields' in data and not isinstance(data['fields'], list):
                raise ParseError('Link "fields" should be a list, but got %s' % type(data['fields']).__name__)
            # TODO: Validate fields are dicts
            # TODO: Validate field names are strings
            # TODO: Validate field names match regex '[A-Za-z_][A-Za-z0-9_]*'
            # TODO: Validate field required is bool

            # Link objects
            url = data.get('url')
            method = data.get('method')
            fields = data.get('fields')
            return Link(url, method, fields, _base_url=base_url, _transport=self)


        elif isinstance(data, OrderedDict):
            # Any unknown types should be ignored and treaded as a regular object.
            data.pop('_type', None)

            # Parse all the items in the dict and wrap them in a `Object`.
            parsed = OrderedDict()
            for key, value in data.items():
                parsed[key] = self._parse(value, base_url)
            return Object(parsed)

        elif isinstance(data, list):
            # Parse all the items in the list and wrap them in a `List`.
            parsed = []
            for item in data:
                value = self._parse(item, base_url)
                # Ignore 'Link' objects contained in a list.
                if not isinstance(value, Link):
                    parsed.append(value)
            return List(parsed)

        return data

    def _create_document(self, parsed):
        """
        Given all the parsed elements, return a document instance.
        """
        # Note that this particular implementation updates documents in place.
        # Eg. doc.pages.next()
        #
        # A valid alternative would be to return a new document on each call.
        # Eg. doc = doc.pages.next()

        if not hasattr(self, 'doc'):
            # Create a new document the first time it is loaded
            self.doc = Document(_transport=self)

        # Update the document instance.
        self.doc.clear()
        self.doc.update(parsed)

        # If Python is running in interactive mode,
        # then display the title andURL of the loaded document
        if not hasattr(main, '__file__'):
            print(self.doc)

        return self.doc


class RequestsTransport(BaseTransport):
    """
    The default transport. Uses the `requests` library.
    """

    def _request(self, method, url, **opts):
        response = requests.request(method, url, **opts)
        return self.loads(response.content)


class MockTransport(BaseTransport):
    """
    A mock transport layer for testing purposes.

    Returns whatever is set in the `content` attribute, and stores
    the method, URL and request options used.
    """

    def __init__(self):
        super(MockTransport, self).__init__()
        self.content = None
        self.method = None
        self.url = None
        self.opts = None

    def _request(self, method, url, **opts):
        assert self.content is not None, 'Made request with `MockTransport` before setting `.content`'

        # Store the arguments so that they can be inspected for test purposes
        self.method = method
        self.url = url
        self.opts = opts

        # Return a document using the mock content provided
        return self.loads(self.content)


### DocJSON types

class List(list):
    """
    This class is mostly a standard list type, except that it prints the
    contained data using a nice indented representation.
    """
    def __repr__(self):
        return _indent_str(self)


class Object(OrderedDict):
    """
    This class is mostly a standard OrderedDict, except that it allows
    us to access the attributes as properties on the object.

    For example: `doc.author.name` will lookup doc['author']['name'].

    It also prints the contained data using a nice indented representation.
    """
    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("object has no attribute '%s'" % attr)

    def __repr__(self):
        return _indent_str(self)


class Document(OrderedDict):
    """
    A top-level DocJSON object.
    For example:

    {
        "_type": "document"
        "meta": {
            "url": "http://example.com",
            "title": "Example DocJSON API"
        },
        ...  # Other attributes
    }
    """

    def __init__(self, *args, **kwargs):
        self._transport = kwargs.get('_transport')
        return super(Document, self).__init__(*args, **kwargs)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("document has no attribute '%s'" % attr)

    def __str__(self):
        return "%s - %s" % (self.meta.get('title', '<no title>'), self.meta.url)

    def __repr__(self):
        return _indent_str(self)

    def refresh(self):
        self._transport.get(self.meta.url)


class Link(object):
    """
    An object that represents a DocJSON link.
    The following are examples of valid links.

    A link which makes a GET request:
    {
        '_type': 'link',
        'url': '/user_details/1234'
    }

    A link which makes a GET request, with an absolute URL:
    {
        '_type': 'link',
        'url': 'http://example.com/user_details/1234'
    }

    A link which makes a DELETE request:
    {
        '_type': 'link',
        'url': '/user_details/1234',
        'method': 'DELETE'
    }

    A link which makes a POST request, with various parameters:
    {
        '_type': 'link',
        'url': '/user_details/1234',
        'method': 'POST',
        'fields': [
            {'name': 'email', 'required': True},
            {'name': 'notes'}
        ]
    }
    """

    def __init__(self, url=None, method=None, fields=None, _base_url=None, _transport=None):
        self.url = url
        self.method = 'GET' if method is None else method.upper()
        self.fields = [] if fields is None else fields
        self._base_url = _base_url
        self._transport = _transport

    def _validate(self, **kwargs):
        """
        Ensure that arguments passed to the link are correct.

        Raises a `ValueError` if any arguments do not validate.
        """
        provided = set(kwargs.keys())

        # Get sets of field names for both required and optional fields.
        required = set([
            field.get('name') for field in self.fields
            if field.get('required', False)
        ])
        optional = set([
            field.get('name') for field in self.fields
            if not field.get('required', False)
        ])

        # Determine if any invalid field names supplied.
        unexpected = provided - (optional | required)
        unexpected = ['"' + item + '"' for item in sorted(unexpected)]
        if unexpected:
            prefix = len(unexpected) > 1 and 'parameters ' or 'parameter '
            raise ValueError('Unknown ' + prefix + ', '.join(unexpected))

        # Determine if any required field names not supplied.
        missing = required - provided
        missing = ['"' + item + '"' for item in sorted(missing)]
        if missing:
            prefix = len(missing) > 1 and 'parameters ' or 'parameter '
            raise ValueError('Missing required ' + prefix + ', '.join(missing))

    def _fields_as_string(self):
        """
        Return the fields as a string containing all the field names,
        indicating which fields are required and which are optional.

        For example: "text, [completed]"
        """
        def field_as_string(field):
            if field.get('required', False):
                return field.get('name')
            return '[' + field.get('name') + ']'

        return ', '.join([
            field_as_string(field) for field in self.fields
        ])

    def __call__(self, **kwargs):
        url = urlparse.urljoin(self._base_url, self.url)
        self._validate(**kwargs)
        if not kwargs:
            opts = {}
        elif self.method == 'GET':
            opts = {
                'params': kwargs
            }
        else:
            opts = {
                'data': json.dumps(kwargs),
                'headers': {'content-type': 'application/json'}
            }
        self._transport._request(self.method, url, **opts)

    def __repr__(self):
        return "<Link url='%s' method='%s' fields=(%s)>" % (
            self.url, self.method, self._fields_as_string()
        )


### Formatted printing of DocJSON documents.

def _indent_str(obj, indent=0):
    """
    Returns an indented string representation for a document.
    """
    if isinstance(obj, (Document, Object)):
        final_idx = len(obj) - 1
        ret = '{\n'
        for idx, (key, val) in enumerate(obj.items()):
            if isinstance(val, Link):
                ret += '    ' * (indent + 1) + key + '(' + val._fields_as_string() + ')'
            else:
                ret += '    ' * (indent + 1) + key + ': ' + _indent_str(val, indent + 1)
            ret += idx == final_idx and '\n' or ',\n'
        ret += '    ' * indent + '}'
        return ret

    elif isinstance(obj, List):
        final_idx = len(obj) - 1
        ret = '[\n'
        for idx, val in enumerate(obj):
            ret += '    ' * (indent + 1) + _indent_str(val, indent + 1)
            ret += idx == final_idx and '\n' or ',\n'
        ret += '    ' * indent + ']'
        return ret

    if is_string(obj):
       return "'" + str(obj) + "'"

    return str(obj)


### Encoding DocJSON documents to bytestrings.

class DocJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, Document):
            ret = OrderedDict()
            ret['_type'] = 'document'
            ret['meta'] = obj.get('meta', {})
            ret.update(obj)
            return super(DocJSONEncoder, self).encode(ret)
        return super(DocJSONEncoder, self).encode(obj)

    def default(self, obj):
        if isinstance(obj, Link):
            ret = OrderedDict()
            ret['_type'] = 'link'
            ret['url'] = obj.url
            if obj.method != 'GET':
                ret['method'] = obj.method
            if obj.fields:
                ret['fields'] = obj.fields
            return ret
        return super(DocJSONEncoder, self).default(obj)
