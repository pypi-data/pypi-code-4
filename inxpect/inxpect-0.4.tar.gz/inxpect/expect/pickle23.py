#-*- coding: utf8 -*-
import jsonpickle
jsonpickle.set_preferred_backend('yajl')


def dumps(data):
    return jsonpickle.encode(data)
def loads(data):
    return jsonpickle.decode(data)
