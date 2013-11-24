# -*- coding: utf-8 -*-

from django.conf import settings
import sys
import traceback
import django.db.models.base
import django.core.serializers
import django.core.serializers.base
import django.http
import django.utils.simplejson
from StringIO import StringIO
from django.db.models.query import QuerySet
import datetime
import dateutil
import django.utils.functional
import logging

class JsonDecodeRegistry(object):
    registry = {}

    def __init__(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

    @classmethod
    def register(cls, class_hint):
        def register(fn):
            cls.registry[class_hint] = fn
        return register

    def objectify(self, obj):
        if "__jsonclass__" in obj and len(obj["__jsonclass__"]) and obj["__jsonclass__"][0] in self.registry:
            return self.registry[obj["__jsonclass__"][0]](self, obj)
        return obj

class JsonEncodeRegistry(object):
    registry = []

    def __init__(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

    @classmethod
    def register(cls, instof=None, test=None):
        if test is None:
            def test(self, obj):
                return isinstance(obj, instof)
        def register(fn):
            cls.registry[0:0] = [(test, fn)]
        return register

    def jsonify(self, obj):
        for test, conv in self.registry:
            if test(self, obj):
                return conv(self, obj)
        return obj

@JsonEncodeRegistry.register(django.db.models.base.Model)
def modelconv(self, obj):
    return type(obj).objects.values().get(id=obj.id)

@JsonEncodeRegistry.register(QuerySet)
def modelconv(self, obj):
    return list(obj.values())

@JsonEncodeRegistry.register(datetime.date)
def modelconv(self, obj):
    return {"__jsonclass__": ["datetime.date"], "value": obj.isoformat()}

@JsonDecodeRegistry.register("datetime.date")
def modelconv(self, obj):
    return dateutil.parser.parse(obj['value']).date()

@JsonEncodeRegistry.register(datetime.datetime)
def modelconv(self, obj):
    return {"__jsonclass__": ["datetime.datetime"], "value": obj.isoformat()}

@JsonDecodeRegistry.register("datetime.datetime")
def modelconv(self, obj):
    return dateutil.parser.parse(obj['value'])

@JsonEncodeRegistry.register(datetime.timedelta)
def modelconv(self, obj):
    return {"__jsonclass__": ["datetime.timedelta"], "value": {"days":obj.days, "seconds": obj.seconds, "microseconds":obj.microseconds}}

@JsonDecodeRegistry.register("datetime.timedelta")
def modelconv(self, obj):
    return datetime.timedelta(obj['value']["days"], obj['value']["seconds"], obj['value']["microseconds"])

class DeserializedException(Exception):
    def __init__(self, type, description, traceback = None):
        self.type = type
        self.description = description
        self.traceback = traceback
    def __str__(self):
        return "DeserializedException: %s\n%s\n%s" % (self.type, self.description, self.traceback or "")

@JsonEncodeRegistry.register(Exception)
def modelconv(self, obj):
    if not isinstance(obj, DeserializedException):
        obj = DeserializedException(
            sys.modules[type(obj).__module__].__name__ + "." + type(obj).__name__,
            str(obj),
            getattr(obj, 'traceback', None))
    value = {'type': obj.type,
             'description': obj.description}
    tb = getattr(obj, 'traceback', None)
    if tb is not None:
        value['traceback'] = tb
    return {"__jsonclass__": ["Exception"], "value": value}

@JsonDecodeRegistry.register("Exception")
def modelconv(self, obj):
    return DeserializedException(obj['value']['type'], obj['value']['description'], obj['value'].get('traceback', None))

def modeltest(self, obj):
    # GAH, Django hides the class for lazy translation strings. I HATE IT SO MUCH!!!
    return type(obj).__name__ == '__proxy__' and type(obj).__module__ =='django.utils.functional'
@JsonEncodeRegistry.register(test=modeltest)
def modelconv(self, obj):
    return obj.encode("utf-8")

def from_json(jsonstr, **kw):
    # Special case, but this is what you generally want...
    if not jsonstr.strip(): return None
    reg = JsonDecodeRegistry(**kw)
    return django.utils.simplejson.loads(jsonstr, object_hook=reg.objectify)

def to_json(obj, **kw):
    reg = JsonEncodeRegistry(**kw)
    return django.utils.simplejson.dumps(obj, default=reg.jsonify)

def json_view(fn):
    """View decorator for views that return pure JSON"""
    def jsonify(request, *arg, **kw):
        status = 200
        try:
            res = fn(request, *arg, **kw)
            if res is None:
                res = {}
        except django.core.servers.basehttp.WSGIServerException:
            raise
        except Exception, e:
            status = 500
            traceback.print_exc()
            res = {'error': {'type': sys.modules[type(e).__module__].__name__ + "." + type(e).__name__,
                             'description': str(e)}}
            if settings.DEBUG == True:
                res['traceback'] = traceback.format_exc()

            logging.error("%s: %s" % (str(e), res['error']['type']))

        if isinstance(res, (django.http.HttpResponse, django.http.StreamingHttpResponse)):
            return res

        res = django.utils.simplejson.dumps(res, default=JsonEncodeRegistry(**getattr(request, 'json_params', {})).jsonify)

        if 'callback' in request.GET:
            res = "%s(%s);" % (request.GET['callback'], res)

        return django.http.HttpResponse(res,
                                        mimetype="text/plain",
                                        status=status)
    return jsonify

def get_foreign_objects(obj, path):
    foreign = getattr(obj, path[0])
    path = path[1:]

    if hasattr(foreign, "all"):
        foreign = foreign.all()
    else:
        foreign = [foreign]

    for obj in foreign:
        if path:
            for res in get_f|oreign_objects(obj, path):
                yield res
        else:
            yield obj

def expand_foreign_key(objs, foreign_key_col):
    res = {}
    if isinstance(objs, django.db.models.base.Model):
        objs = [objs]
    elif isinstance(objs, QuerySet):
        objs = objs.all()
    for obj in objs:
        for foreign in get_foreign_objects(obj, foreign_key_col.split("__")):
            if foreign is not None:
                res[foreign.pk] = foreign
    return res

def expand_foreign_keys(objs, follow_foreign_keys={}):
    res = {}
    for foreign_key_name, foreign_key_col in follow_foreign_keys.iteritems():
        res[foreign_key_name] = expand_foreign_key(objs, foreign_key_col)
    return res

def get_view(name, cls, follow_foreign_keys={}):
    @json_view
    def get_view(request, *arg, **kw):
        logging.info("Get " + name)
        if 'filter' in request.GET:
            selfs = cls.objects.filter(**django.utils.simplejson.loads(request.GET['filter']))
        else:
            selfs = cls.objects.all()
        if 'order_by' in request.GET:
            selfs = selfs.order_by(*django.utils.simplejson.loads(request.GET['order_by']))

        res = {name: selfs}
        res.update(expand_foreign_keys(selfs, follow_foreign_keys))
        return res
    return get_view
