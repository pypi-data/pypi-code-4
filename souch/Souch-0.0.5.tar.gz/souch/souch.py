from utils.peti import send, comprobar
from utils.errors import CouchDBOff
import urllib
import base64
from souchdoc import SouchDoc


class Souch(object):
    def __init__(self, db, options, create=False):
        self.options = options
        if type(self.options).__name__ != 'dict':
            raise CouchDBOff('Options must be a dictionary not a ', type(self.options).__name__, "WARNING")
        if not 'host' in self.options:
            self.options['host'] = "localhost"
        if not 'port' in self.options:
            self.options['port'] = "5984"
        self.db = str(db).strip()
        if 'username' in self.options and 'password' in self.options:
            base64string = base64.encodestring('%s:%s' % (self.options['username'], self.options['password'])).replace('\n', '')
            b64s = "Basic %s" % base64string
            self.options.update({'headers': {'Authorization': b64s}})
        if len(self.db) == 0:
            raise CouchDBOff('Database name does not must be empty', "", "WARNING")
        elif len(self.db) != 0 and create is False:
            exists = self.exists_db(self.db)
            if exists is False:
                raise CouchDBOff("Are you sure that database exists?", "Try changing create to True", "WARNING")
        elif len(self.db) != 0 and create is True:
            exists = self.exists_db(self.db)
            def cb(parameter):
                pass
            if exists is False:
                self.create_db(self.db, cb)
            elif exists is True:
                pass
        comprobar(self.options['host'], self.options['port'])

    def exists_db(self, db):
        def cb(p):
            pass
        cb = cb
        if len(str(db).strip()) == 0:
            raise CouchDBOff('The name of the database does not must be empty', "", "WARNING")
        self.options['path'] = '/_all_dbs'
        self.options['method'] = "GET"
        bases = send(self.options, cb)
        if str(db).strip() in bases:
            return True
        else:
            return False

    def create_db(self, name, cb):
        if len(str(name).strip()) == 0:
            raise CouchDBOff('The name of the database does not must be empty', "", "WARNING")
        self.options['method'] = "PUT"
        self.options['path'] = "/%s" % name
        return send(self.options, cb)

    def newDoc(self, type_):
        return SouchDoc(self.db, self.options, type_)

    def design(self, name, options_design, cb):
            if type(options_design).__name__ != 'dict':
                raise CouchDBOff('Options must be a dictionary not a ', type(self.options).__name__, "WARNING")
            params = urllib.urlencode({p: json.dumps(options_design['params'][p]) for p in options_design['params']})
            if 'type' in options_design:
                type_ = options_design['type']
            else:
                type_ = "view"
            self.options['path'] = '/%s/_design/%s/_%s/%s?%s' % (self.db, name, type_,
                                                                 options_design['name'], params
                                                                 )
            self.options['method'] = "GET"
            return send(self.options, cb)

#couch = Souch('hello-world', {'host': 'localhost', 'port': 5984, 'username': 'root', 'password': 'root'}, True)
#users = couch.newDoc({'_type': 'products'})
#products = couch.newDoc('productos')


#def cb(p):
    #print p
    #for i in p['rows']:
        # print "Key>>>", i['key']
        # print "Name>>>", i['value'][0]
        # print "Price >>>>", i['value'][1]
#couch.exists_db('database_name')
#couch.create_db('hoho', cb)
# options = {'name': 'precios', 'params': {'descending': False, 'startkey': 'Mexico', 'endkey': 'Mexico'}}
# couch.design('precios', options, cb)
#products.get('mangos', lambda parameter: "I'm the result of the callback" + str(parameter))
#data = {"_id": "mangos_updated", "item": "mango_update", "prices": {"Mecouchico": 10.98, 'USA': 10}}
#data2 = {"_id": "mangasoscons2", "item": "mango_updates2", "prices": {"Mexicanos putos": 10.98, 'USA': 10}, 'new_field': 'some'}
# data3 = {'yes': 'yes'}
#products.post(data2, cb)
# products.put('mangasoscons3', data3, True, cb)
#couch.put('mangosaa', data2, True, cb)
# products.delete("mangasoscons", cb)
#couch.delete("mangoos", cb)
