import json

from splicer import Schema
from splicer.ast import LoadOp, SelectionOp

from discodb import DiscoDB


_key        = str
_value      = json.dumps
_load_key   = int
_load_value = json.loads

def create(path, schema, records):
  if isinstance(schema, dict):
    schema = Schema(**schema)

  return DiscoDB(index(schema, records))


def index(schema, records):
  yield "__schema__", _value(dict(fields=[
    f.to_dict()
    for f in schema.fields
  ]))

  for doc_id, record in enumerate(records):
    doc_id = _key(doc_id+1)
    yield doc_id, _value(record)
    for field in schema.fields:
      value = record[field.name]
      yield "{}:{}".format(field.name, value), doc_id
      yield field.name, "{}:{}".format(field.name, value)


  yield '__count__', doc_id


class DiscoDBServer(object):
  capabilities = [SelectionOp]

  def __init__(self, **tables):
    # {'name': DiscoDB}
    self._tables = {}
    for name, path_or_db in tables.items():
      if isinstance(path_or_db, DiscoDB):
        db = path_or_db
      else:
        db = DiscoDB.load(open(path_or_db))
      self._tables[name] = DiscoTable(self, name, db)

  def has(self, table_name):
    return table_name in self._tables


  @property
  def relations(self):
    return [
      (name, relation.schema)
      for name, relation in self._tables.items()
    ]


  def get_relation(self, name):
    return self._tables.get(name)

  def evaluate(self, operation):
    if isinstance(operation, LoadOp):
      relation_name = operation.name
    elif isinstance(operation, SelectionOp):
      relation_name = operation.relation.name
      # todo build discodb query

    return self._tables[relation_name]


class DiscoTable(object):
  def __init__(self, server, name, db, range=None):
    self.server = server
    self.name   = name
    schema      = _load_value(list(db['__schema__'])[0])
    self.schema = Schema(**schema)
    self.db     = db

    self.record_count  = _load_value(list(db['__count__'])[0])
    if range:
      self.range = range

  def range(self):
    return ( str(x+1) for x in xrange(0, self.record_count))

  def __iter__(self):
    db = self.db
    fields = self.schema.fields
    def to_tuple(doc):
      return tuple(doc.get(f.name) for f in fields)

    return (
      to_tuple(_load_value(row))
      for row_id in self.range()
      for row in db[row_id]
    )

def compile(query):
  """Return a function for generating the row id's from the given query."""
   