from rawes.elastic_exception import ElasticException
from rawes import Elastic

from fanery.terms import parse_term, to_simple, to_json, is_dict
from fanery import store, service

default_params = dict()

class Model(object):

    def __init__(self, name, es):
        self.name = name
        self.es = es.es

    @property
    def _index(self):
        try:
            return self.__index
        except AttributeError:
            index = service.state.domain or 'local'
            es = self.es
            try:
                es.get('%s/_status' % index)
            except ElasticException:
                es.put(index)
            finally:
                self.__index = idx = (es, '%s/%s' % (index, self.name))
                return idx

    def get(self, uuid):
        es, path = self._index
        rs = es.get('%s/%s' % (path, uuid))
        if rs['exists']:
            return parse_term(rs['_source'])
        else:
            return None

    def fetch(self, **argd):
        record = None
        for idx, record in enumerate(self.select(**argd)):
            if idx > 0:
                raise store.MultipleRecordsFound()
        return record

    def select(self, **argd):
        fields = dict((k, argd.pop(k)) for k,v in argd.items() if not is_dict(v))
        if fields:
            query = ' AND '.join('%s:%s' % (f, to_json(v)) if v is not None \
                                 else '_missing_:%s' % f for f,v in fields.items())
            if query:
                argd['data'] = {'query': {'query_string': {'query': query}}}
        es, path = self._index
        for hit in es.get('%s/_search' % path, **argd)['hits']['hits']:
            yield parse_term(hit['_source'])

    def insert(self, record):
        es, path = self._index
        es.put('%s/%s' % (path, record._uuid),
               data = to_simple(record.dump()),
               params = default_params)

    def update(self, record):
        es, path = self._index
        es.put('%s/%s?version=%d' % (path, record._uuid, record._vsn-1),
               data = to_simple(record.dump()),
               params = default_params)

    def delete(self, record):
        es, path = self._index
        es.delete('%s/%s?version=%d' % (path, record._uuid, abs(record._vsn)),
                  params = default_params)

    def clear(self):
        es, path = self._index
        try:
            es.delete(path, params = default_params)
        except ElasticException:
            pass

class ElasticSearch(object):

    def __init__(self, *args, **argd):
        argd.setdefault('except_on_error', True)
        self.es = Elastic(*args, **argd)

    def begin(self, txn):
        pass

    def prepare_commit(self, txn):
        pass

    def commit(self, txn):
        pass

    def rollback(self, txn):
        pass

    def model(self, name):
        return Model(name, self)
