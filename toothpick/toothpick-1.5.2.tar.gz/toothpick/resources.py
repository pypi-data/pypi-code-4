import toothpick

from toothpick import exceptions
from toothpick import logger

import json
import os

try:
    import requests
except ImportError:
    pass
try:
    import pymongo as mongo
except ImportError:
    pass


def option(key, options):
    try:
        if options and key in options:
            return options[key]
    except TypeError:
        return None



class Resource(object):
    '''
    A `Resource` is a CRUD interface to some data storage backend.  Resources
    are bound ("registered") to model classes via the `Resource.register()`
    decorator.

    Resources have several common parameters, as well as domain-specific
    parameters, which are defined by a specific `Resource` subclass.

    :param resource_name: how this resource should be referred to in calls to
    resource proxies, associations, and methods like `Base.find()`.

    :param config: an instantiated `Config` object that describes how this
    resource should connect to the backend.

    :param proxies: a dictionary of `{ action: resource_name }` to help control
    how documents fetched by this resource should be handled.

    :param options: a dictionary of options to control how this particular
    resource interacts with the rest of the toothpick framework.
    '''

    def __init__(self, resource_name, config, proxies, options=None):
        self.resource_name = resource_name
        self.config = config

        if proxies == toothpick.DEFAULT:
            proxies = {}
        self.proxies = proxies

        if not options:
            options = {}
        self.options = options

    def __repr__(self):
        return "%s(%s)[%s]" % (
            self.__class__.__name__,
            repr(self.config),
            self.resource_name
        )

    def create(self, query, attributes, options=None):
        raise NotImplementedError

    def read(self, query, options=None):
        raise NotImplementedError

    def update(self, query, attributes, options=None):
        raise NotImplementedError

    def delete(self, query, options=None):
        raise NotImplementedError

    def exists(self, query, options=None):
        raise NotImplementedError

    @classmethod
    def register(cls,
                 resource_name,
                 config,
                 proxies=toothpick.DEFAULT,
                 options=None,
                 **data):
        """
        Decorator for use on model classes.  This method instantiates a
        resource using the given parameters and registers it to the class that
        is decorated.  
        """

        def wrap(model_class):
            resource = cls(
                resource_name=resource_name,
                config=config,
                proxies=proxies,
                options=options,
                **data
            )
            model_class._resources[resource_name] = resource

            return model_class

        return wrap

class EmbeddedResource(Resource):
    @classmethod
    def register(cls,
                 resource_name,
                 config=None,
                 proxies=toothpick.DEFAULT,
                 options=None,
                 **data):
        return super(EmbeddedResource, cls).register(
            resource_name, config, proxies, options, **data
        )

class RESTfulResource(Resource):
    '''
    Connection adapter for use with resources that send and recieve data
    as documents via a RESTful HTTP interface.

    This resource takes a `HTTPConfig` configuration object
    '''

    def __init__(self, resource_name, config, proxies, path, options=None):
        super(RESTfulResource, self).__init__(
            resource_name, config, proxies, options
        )

        try:
            requests
        except NameError:
            raise RuntimeError("Couldn't import required library: 'requests'")

        self.path = path

    def url(self, query):
        if '%' in self.path:
            try:
                # query can be a tuple, if path has multiple interpolations
                full_query = self.path % query
            except TypeError, e:
                raise exceptions.ToothpickError("\n".join(
                    ["Wrong number of arguments for resource:",
                     "  path: %s" % repr(self.path),
                     "  query: %s" % repr(query)]
                ))
        else:
            full_query = self.path
        return "/".join([self.config.base_url, full_query])

    def create(self, query, attributes, options=None):
        headers = self.default_create_headers()
        if option('headers', options):
            headers.update(option('headers', options))

        body = self.serialize(attributes)
        response = requests.post(self.url(query),
                                 data=body,
                                 headers=headers,
                                 auth=self.auth())

        self.handle_response(response)
        return self.deserialize(response.content)

    def read(self, query, options=None):
        headers = self.default_read_headers()
        if option('headers', options):
            headers.update(option('headers', options))

        response = requests.get(self.url(query),
                                headers=headers, 
                                auth=self.auth())

        self.handle_response(response)
        return self.deserialize(response.content)

    def update(self, query, attributes, options=None):
        headers = self.default_update_headers()
        if option('headers', options):
            headers.update(option('headers', options))

        body = self.serialize(attributes)
        response = requests.put(self.url(query),
                                data=body,
                                headers=headers,
                                auth=self.auth())

        self.handle_response(response)
        return attributes

    def delete(self, query, options=None):
        headers = self.default_delete_headers()
        if option('headers', options):
            headers.update(option('headers', options))

        response = requests.delete(self.url(query),
                                   headers=headers, 
                                   auth=self.auth())

        self.handle_response(response)
        return

    def exists(self, query, options = None):
        headers = self.default_exists_headers()
        if option('headers', options):
            headers.update(option('headers', options))

        response = requests.head(self.url(query),
                                 headers=headers, 
                                 auth=self.auth())

        try:
            self.handle_response(response)
            # TODO: what if the response is an empty list? - not done yet
            return True
        except exceptions.ResponseError, e:
            return False

    
    def handle_response(self, response):
        '''
        Takes a response object, and either returns it, or raises
        an appropriate exception based on the status code of the
        response.
        '''
        logger.info("Parsing data from URL: %s %s" % (
            response.request.method,
            response.request.url
        ))

        if response.status_code in range(200, 400):
            # then we cool
            return response

        # if we're here, it's an exception
        logger.error("URL returned an error: %s %s (%s)" % (
            response.request.method,
            response.request.url,
            response
        ))


        # seriously, python, no switch statement?
        if response.status_code == 400:
            raise exceptions.BadRequest(response)
        elif response.status_code == 401:
            raise exceptions.Unauthorized(response)
        elif response.status_code == 403:
            raise exceptions.Forbidden(response)
        elif response.status_code == 404:
            raise exceptions.NotFound(response)
        elif response.status_code == 405:
            raise exceptions.MethodNotAllowed(response)
        elif response.status_code == 409:
            raise exceptions.Conflict(response)
        elif response.status_code == 422:
            raise exceptions.Invalid(response)
        elif response.status_code in range(400, 500):
            raise exceptions.ClientError(response)
        elif response.status_code in range(500, 600):
            raise exceptions.ServerError(response)
        else:
            raise exceptions.ResponseError(
                response,
                "Unhandled status code: %s" % response.status_code
            )

    def default_create_headers(self):
        return {}

    def default_read_headers(self):
        return {}

    def default_update_headers(self):
        return {}

    def default_delete_headers(self):
        return {}

    def default_exists_headers(self):
        return {}

    def serialize(self, data):
        '''
        Serialized data is passed as the request body in PUT and POST
        requests.
        '''
        return data

    def deserialize(self, data):
        '''
        Response data is deserialized before being used by the object
        that requested it (GET).
        '''
        return data

    def auth(self):
        ''' Convenience method for pulling auth params out of config. '''
        if self.config.username or self.config.password:
            return (self.config.username, self.config.password)
        return None

class JSONSerializer(object):
    def serialize(self, data):
        return json.dumps(data)

    def deserialize(self, data):
        return json.loads(data)


class JSONResource(JSONSerializer, RESTfulResource):

    def default_create_headers(self):
        return {'content-type': 'application/json'}

    def default_update_headers(self):
        return {'content-type': 'application/json'}

class TSVResource(RESTfulResource):

    data_delimiter = '\t'
    line_delimiter = '\n'

    def serialize(self, data):
        ''' Turn the given list of dictionaries into a TSV string, with
        each given dictionary translating to one row of TSV data. Note 
        that any information about column ordering contained in the original
        TSV string is lost. '''
        
        if type(data) is dict:
            data = [data]

        rows = []

        # Get all the properties that any of our data objects have
        properties = set()
        for element in data:
            for (key, value) in element.items():
                properties.add(key)
        rows.append(self.data_delimiter.join(properties))

        for element in data:
            row = []
            for prop in properties:
                if element.has_key(prop):
                    row.append(element[prop])
                else:
                    row.append("")
            rows.append(self.data_delimiter.join(row))

        return self.line_delimiter.join(rows)

    def deserialize(self, data):
        ''' Turn TSV data into a list of objects, properties defined by the 
        first row in the data.  If the data has fewer than two lines, 
        we didn't get any objects back and will return []. '''

        items = []
        rows = [row.split(self.data_delimiter) for row in \
                                    (data.split(self.line_delimiter))]
        properties = rows[0]
        for row_num in range(1, len(rows)):
            row = rows[row_num]

            # If this row contains no data, skip it
            for i in row:
                if i: break
            else: continue

            item = {}
            for i in range(len(properties)):
                key = properties[i]
                if not key:
                    continue
                # If row[i] is null, should we not set the property?
                # Or should we set it to None? Or to ""? Same questions
                # for cases where this row has fewer elements than the 
                # properties row.
                item[key] = row[i] if i < len(row) else ""
            items.append(item)

        return items

class MongoResource(Resource):

    def __init__(self, resource_name, config, proxies, collection,
                 bson=toothpick.DEFAULT, options=None):
        super(MongoResource, self).__init__(
            resource_name, config, proxies, options
        )
        try:
            mongo
        except NameError:
            raise RuntimeError("Couldn't import a python mongo driver")

        self.collection_name = collection
        self.queryify = bson
        if self.queryify == toothpick.DEFAULT or not self.queryify:
            self.queryify = lambda x:x
        
        self._client = None # initialized at time of first query

    @property
    def client(self):
        if not self._client:
            self._client = mongo.MongoClient(self.config.host,  
                                             self.config.port,  
                                             auto_start_request=False)
        return self._client

    @property
    def collection(self):
        self.database = self.client[self.config.database]

        if self.config.username and self.config.password:
            self.database.authenticate(self.config.username,
                                       self.config.password)

        return self.database[self.collection_name]


    def create(self, query, attributes, options=None):
        with self.client.start_request():
            result = self.collection.insert(attributes, safe=True)
            # result is an ObjectId object, so we want that in the document under
            # the field name '_id'
            return { '_id': result }


    def read(self, query, options=None):
        if not options:
            options = {}

        with self.client.start_request():
            # special case for 'fields' option - fields need to be passed to
            # collection#find
            fields = options.pop('fields', None)
            cursor = self.collection.find(self.queryify(query), fields=fields)

            # treat options as chaining cursor operations
            for operation, value in options.items():
                if hasattr(cursor, operation):
                    getattr(cursor, operation)(value)

            # collection#find returns a cursor, but we need to actually
            # fetch the documents
            results = list(cursor)
            return results

    def update(self, query, attributes, options=None):
        with self.client.start_request():
            self.collection.update(self.queryify(query), attributes, safe=True)

    def delete(self, query, options=None):
        with self.client.start_request():
            deleted = self.collection.remove(self.queryify(query), safe=True)
            return deleted

    def exists(self, query, options=None):
        with self.client.start_request():
            exists = self.collection.find(self.queryify(query)).count() > 0
            return exists


class FileResource(Resource):
    '''
    FileResource is used to point at documents on the filesystem as resources
    for toothpick models.  Note that each operation results in the file being
    opened and closed - the files are not kept open.  This resource also does
    not distinguish between create and update operations - in both cases, the
    entire file is written.

    This class must be subclassed to implement deserialize in order to be
    useful. See JSONFileResource for simple deserialization.

    This resource takes a FileConfig object.
    '''
    def __init__(self, resource_name, config, proxies, path, options=None):
        super(FileResource, self).__init__(
            resource_name, config, proxies, options
        )
        self.path = path

    def exists(self, query, options=None):
        # no shortcuts for exists on the filesystem - even if we check that the
        # file exists, it could still have badly serialized data, resulting in
        # exists => true, read => exception
        try:
            self.read(query, options)
            return True
        except:
            return False

    def read(self, query, options=None):
        with open(self.resolve_path(query)) as fin:
            file_contents = fin.read()
            return self.deserialize(file_contents)

    def create(self, query, attributes, options=None):
        with open(self.resolve_path(query), 'w') as f:
            f.write(self.serialize(attributes))
            return {}
    def update(self, query, attributes, options=None):
        self.create(query, attributes, options)
        return attributes

    def delete(self, query, options):
        os.remove(self.resolve_path(query))

    def resolve_path(self, query):
        if '%' in self.path:
            try:
                # query can be a tuple, if path has multiple interpolations
                full_query = self.path % query
            except TypeError, e:
                raise exceptions.ToothpickError("\n".join(
                    ["Wrong number of arguments for resource:",
                     "  path: %s" % repr(self.path),
                     "  query: %s" % repr(query)]
                ))
        else:
            full_query = self.path
        return os.path.join(self.config.abspath, full_query)

    def deserialize(self, data):
        raise NotImplementedError
    def serialize(self, data):
        raise NotImplementedError


class JSONFileResource(JSONSerializer, FileResource):
    '''
    Loads file contents into memory once per instantiation (startup).
    '''

