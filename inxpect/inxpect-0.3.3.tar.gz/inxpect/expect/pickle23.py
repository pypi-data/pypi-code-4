#-*- coding: utf8 -*-
import jsonpickle

def dumps(data):
    return jsonpickle.encode(data)
def loads(data):
    return jsonpickle.decode(data)
