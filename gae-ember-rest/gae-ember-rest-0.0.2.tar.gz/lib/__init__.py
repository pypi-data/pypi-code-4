import re
import logging
import webapp2 as webapp
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine._internal.django.utils import simplejson as json

logger = logging.getLogger(__name__)

class BaseView(webapp.RequestHandler):
    pass

class BaseItemsView(BaseView):

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        def get_items_json():
            items = self.api.model.query().fetch(100)
            for item in items:
                is_readable = self.api.__is_readable__(self, item)
                if not isinstance(is_readable, int):
                    yield self.api.item_to_JSON(item)
        json_data = {}
        json_data[self.api.plural_name] = [
            i for i in get_items_json()
        ]
        self.response.out.write(json.dumps(json_data))

    def post(self):
        body = self.request.body
        if json.loads(body).get('query', None):
            return self.query()
        self.create()

    def create(self):
        self.response.headers['Content-Type'] = 'application/json'
        item = self.api.model()
        self.api.update_item(self, item)
        is_creatable = self.api.__is_creatable__(self, item)
        if isinstance(is_creatable, int):
            self.error(is_creatable)
            return
        item.put()
        json_data = {}
        json_data[self.api.name] = self.api.item_to_JSON(item)
        self.response.out.write(json.dumps(json_data))

    def query(self):
        body = self.request.body
        query = json.loads(body)['query']
        if query == 'count':
            count = '%s' % self.api.model.query().count(100)
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write(count)
            return
        self.response.headers['Content-Type'] = 'application/json'
        def values():
            for value in query['values']:
                if isinstance(value, dict):
                    kind = value['kind']
                    id = int(value['value'])
                    value = ndb.Key(kind, id)
                yield value
        items = self.api.model\
            .gql(query['string'], *[i for i in values()])#\
            #.fetch(1000)
        def get_items_json():
            for item in items:
                is_readable = self.api.__is_readable__(self, item)
                if not isinstance(is_readable, int):
                    yield self.api.item_to_JSON(item)
        json_data = {}
        json_data[self.api.plural_name] = [
            i for i in get_items_json()
        ]
        self.response.out.write(json.dumps(json_data))

class BaseItemView(BaseView):

    def get(self, id):
        self.response.headers['Content-Type'] = 'application/json'
        item = self.api.model.get_by_id(int(id))
        is_readable = self.api.__is_readable__(self, item)
        if isinstance(is_readable, int):
            self.error(is_readable)
            return
        json_data = {}
        json_data[self.api.name] = self.api.item_to_JSON(item)
        self.response.out.write(json.dumps(json_data))

    def put(self, id):
        self.response.headers['Content-Type'] = 'application/json'
        item = self.api.model.get_by_id(int(id))
        self.api.update_item(self, item)
        is_updatable = self.api.__is_updatable__(self, item)
        if isinstance(is_updatable, int):
            self.error(is_updatable)
            return
        item.put()
        json_data = {}
        json_data[self.api.name] = self.api.item_to_JSON(item)
        self.response.out.write(json.dumps(json_data))

    def delete(self, id):
        self.response.headers['Content-Type'] = 'application/json'
        item = self.api.model.get_by_id(int(id))
        is_removable = self.api.__is_removable__(self, item)
        if isinstance(is_removable, int):
            self.error(is_removable)
            return
        item.key.delete()

        for label, prop in self.api.model._properties.iteritems():
            if isinstance(prop, ndb.KeyProperty):
                key = getattr(item, label)
                if key:
                    key.delete()

        return

class Utils:

    # return `string` underscored e.g.
    # bigData -> big_data
    # big data -> big_data
    def get_underscored_string(self, string):
        return re\
            .sub('(?!^)([A-Z]+)', r'_\1', string)\
            .replace(' ', '_')\
            .lower()


class Field(Utils):

    def __init__(self, name, field):
        self.name = name
        self.field = field

    @property
    def underscored_name(self):
        return self.get_underscored_string(self.name)

    @property
    def belongs_to_name(self):
        return self.underscored_name + '_id'

    @property
    def model(self):
        return self.field._kind

class Api(Utils):
    def __init__(self):
        for attr in [
            '__is_creatable__',
            '__is_readable__',
            '__is_updatable__',
            '__is_removable__'
        ]:
            if not getattr(self, attr, None):
                opts = (self.__class__, attr)
                e = 'please implement %s.%s(self, req, item)' % opts
                raise Exception(e)

    @property
    def name(self):
        return self.get_underscored_string(self.model.__name__)

    @property
    def plural_name(self):
        return self.name + 's'

    @property
    def field_list(self):
        for field_name in self.fields:
            field = self.model._properties[field_name]
            yield Field(field_name, field)

    @property
    def urls(self):
        class ItemsView(BaseItemsView):
            api = self
        class ItemView(BaseItemView):
            api = self
        return [
            ( '/' + self.plural_name + '/', ItemsView),
            ( '/' + self.plural_name + '/(\w+)/', ItemView),
        ]

    def item_to_JSON(self, item):
        data = {}
        data['id'] = unicode(item.key.id())
        for field in self.field_list:
            value = getattr(item, field.name)
            if not value:
                continue
            elif isinstance(field.field, ndb.KeyProperty):
                value = unicode(value.id())
                data[field.belongs_to_name] = value
            elif isinstance(field.field, ndb.UserProperty):
                value = unicode(value.email())
                data[field.name] = value
            else:
                data[field.name] = value
        return data

    def update_item(self, view, item):
        data = json.loads(view.request.body)[self.name]
        for field in self.field_list:
            value = None
            if isinstance(field.field, ndb.KeyProperty):
                id = data.get(field.belongs_to_name, None)
                if id:
                    id = int(id)
                    kind = field.model
                    key = ndb.Key(kind, id)
                    value = key
            elif isinstance(field.field, ndb.UserProperty):
                email = data.get(field.underscored_name, None)
                if email:
                    value = users.User(email)
            else:
                value = data.get(field.underscored_name, None)
            if value:
                setattr(item, field.name, value)

class Apis(list):

    def __init__(self, *args):
        super(list, self).__init__()
        for cls in args:
            api = cls()
            for url in api.urls:
                self.append(url)

    @property
    def urls(self):
        return patterns('',
            *self
        )
