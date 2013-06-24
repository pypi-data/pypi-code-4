from utils.peti import send
from utils.errors import *


class SouchDoc(object):

    def __init__(self, db, options, field):
        self.db = db
        self.options = options
        if type(field).__name__ == "dict" and len(field) == 1:
            self.options.update(field)
            self.field_key = field.keys()[0]
            self.field_value = field[self.field_key]
        else:
            self.options['type'] = field
            self.field_key = 'type'
            self.field_value = field

    def get(self, id, cb):
        self.options['path'] = "/%s/%s" % (self.db, id)
        self.options['method'] = "GET"
        return send(self.options, cb)

    def post(self, data, cb):
        self.options['method'] = "POST"
        self.options['path'] = "/%s" % (self.db)
        data[self.field_key] = self.field_value
        return send(self.options, data, cb)

    def delete(self, id, cb):
        get = self.get(id, lambda x: "")
        fullPathId = str(get['_id'] + "?rev=" + get['_rev'])
        self.options['path'] = "/%s/%s" % (self.db, fullPathId)
        self.options['method'] = "DELETE"
        return send(self.options, cb)

    def put(self, id, data, ins, cb):
        if ins is False:
            get = self.get(id, lambda x: "")
            fullPathId = str(get['_id'] + "?rev=" + get['_rev'])
            self.options['path'] = "/%s/%s" % (self.db, fullPathId)
            self.options['method'] = "PUT"
            data[self.field_key] = self.field_value
            return send(self.options, data, cb)
        elif ins is True:
            self.options['path'] = "/%s/%s" % (self.db, id)
            self.options['method'] = "PUT"
            data[self.field_key] = self.field_value
            return send(self.options, data, cb)
        else:
            raise CouchDBOff("ins must be a boolean not a ", type(ins).__name__, "FAIL")
