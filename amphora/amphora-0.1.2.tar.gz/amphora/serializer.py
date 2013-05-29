# -*- coding: utf-8 -*-
import json
from .exception import WrongRequest, WrongResult, RemoteException


class AbstractRpcSerializer(object):
    @staticmethod
    def serialize_call(func, args, kwargs):
        raise NotImplementedError

    @staticmethod
    def deserialize_call(obj):
        raise NotImplementedError

    @staticmethod
    def serialize_result(obj):
        raise NotImplementedError

    @staticmethod
    def deserialize_result(data):
        raise NotImplementedError


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super(CustomJSONEncoder, self).default(obj)
        except TypeError:
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            elif hasattr(obj, '__unicode__'):
                return unicode(obj).encode('utf-8')
            elif hasattr(obj, '__str__'):
                return str(obj)
            else:
                raise


class RpcJsonSerializer(AbstractRpcSerializer):
    @staticmethod
    def serialize_call(func, args, kwargs):
        return json.dumps({
            'func': func,
            'args': args,
            'kwargs': kwargs
        }, cls=CustomJSONEncoder)

    @staticmethod
    def deserialize_call(obj):
        try:
            data = json.loads(obj)
            func, args, kwargs = data['func'], data['args'], data['kwargs']
        except (ValueError, LookupError, AssertionError, TypeError):
            raise WrongRequest(obj)
        else:
            return (func, args, kwargs)

    @staticmethod
    def serialize_result(obj):
        result = {}
        if isinstance(obj, Exception):
            result['exception'] = {
                'type': obj.__class__.__name__,
                'args': obj.args
                }
        else:
            result['result'] = obj
        return json.dumps(result, cls=CustomJSONEncoder)

    @staticmethod
    def deserialize_result(data):
        try:
            result = json.loads(data)
        except ValueError:
            pass
        else:
            if 'result' in result:
                return result['result']
            elif 'exception' in 'exception':
                exception = result['exception']
                typ, args = exception.get('type'), exception.get('args')
                if typ == 'WrongRequest':
                    raise WrongRequest(*args)
                raise RemoteException(typ, args)
        raise WrongResult(data)
