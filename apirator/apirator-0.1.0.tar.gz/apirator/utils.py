# -*- coding: utf-8 -*-

import functools
import inspect
import logging

from django.http import HttpResponse, Http404
from django.views.generic.base import View
from django.views.decorators.csrf import csrf_exempt

from django.utils.importlib import import_module


encoders = {}
decoders = {}


try:
    import json
    decoders["application/json"] = json.loads
    encoders["application/json"] = lambda x: json.dumps(x, ensure_ascii=True)
except ImportError:
    pass

try:
    import plistlib
    encoders["application/xml"] = plistlib.writePlistToString
    decoders["application/xml"] = plistlib.readPlistFromString
except ImportError:
    pass

try:
    import yaml
    encoders["application/x-yaml"] = yaml.safe_dump
    decoders["application/x-yaml"] = yaml.safe_load
except ImportError:
    pass

try:
    import msgpack
    encoders["application/x-msgpack"] = msgpack.dumps
    decoders["application/x-msgpack"] = msgpack.loads
except ImportError:
    pass


class ValidationError(Exception):

    pass


def type_validator(type_):
    validator = lambda x: isinstance(x, type_)
    validator.__name__ = "is %s" % type_.__name__
    return validator


class Endpoint(object):

    def __init__(self, name, method, fun, validators):
        self.name = name
        self.method = method
        self.fun = fun
        self.validators = {}
        self.known_keys = []
        self.required_keys = []
        spec = inspect.getargspec(fun)
        for index, arg in enumerate(spec.args):
            self.known_keys.append(arg)
            if index < len(validators):
                validator = validators[index]
                if isinstance(validator, type):
                    validator = type_validator(validator)
                self.validators[arg] = validator
            if len(spec.defaults or []) < len(spec.args) - index:
                self.required_keys.append(arg)

    def validate(self, data):
        for key in data:
            if key not in self.known_keys:
                raise ValidationError("unknown key %r" % key)
        for key in self.required_keys:
            if key not in data:
                raise ValidationError("value for %r is not provided" % key)
        for key, validator in self.validators.items():
            if key in data:
                if not validator(data[key]):
                    raise ValidationError("bad value for key %r" % key)


class ApiRouter(View):

    endpoints = None
    module = None
    logger = logging.getLogger("apirator.router")

    def _error_response(self, code, message):
        return HttpResponse(encoders[self.response_encoding]({"error": message}),
                            status=code,
                            mimetype=self.response_encoding)

    def _accept_error(self):
        return HttpResponse("bad Accept header value, possible values are:\n" +
                            ", ".join(encoders.keys()),
                            status=406,
                            mimetype="text/plain")

    @csrf_exempt
    def dispatch(self, request, path):
        self.request = request

        self.response_encoding = request.META.get("HTTP_ACCEPT")
        if self.response_encoding == "*/*":
            self.response_encoding = "application/json"
        if self.response_encoding not in encoders:
            return self._accept_error()

        if request.body:
            self.request_encoding = request.META.get("CONTENT_TYPE").split(";")[0]
            if self.request_encoding not in decoders:
                return self._error_response(415, "supported content types are: " +
                                            ", ".join(decoders.keys()))

        if path not in self.endpoints:
            return self._error_response(404, "endpoint '%s' not found" % path)

        ep = self.endpoints[path]

        if request.method != ep.method:
            resp = self._error_response(405, "only %s allowed" % ep.method)
            resp["Allow"] = ep.method
            return resp

        payload = {}
        if request.body:
            try:
                payload = decoders[self.request_encoding](request.body)
            except:
                return self._error_response(400, "can not decode request body")

        try:
            ep.validate(payload)
        except ValidationError as err:
            self.logger.error("apirator %s '%s#%s' as %s failed validation: %s",
                              request.method, self.module, path, self.response_encoding,
                              err.message)
            return self._error_response(400, err.message)

        self.logger.info("apirator %s '%s#%s' as %s", request.method,
                         self.module, path, self.response_encoding)

        try:
            result = ep.fun(**payload)
        except:
            return self._error_response(500, "internal error")

        return HttpResponse(encoders[self.response_encoding](result),
                            mimetype=self.response_encoding)


def expose(endpoint=None, method="GET", *validators):
    def wrapper(fun):
        return Endpoint(endpoint or fun.__name__,
                        method, fun, validators)
    return wrapper


def router(module):
    mod = import_module(module)
    endpoints = {}
    for name in dir(mod):
        val = getattr(mod, name)
        if isinstance(val, Endpoint):
            endpoints[val.name] = val
    return ApiRouter.as_view(endpoints=endpoints, module=module)
