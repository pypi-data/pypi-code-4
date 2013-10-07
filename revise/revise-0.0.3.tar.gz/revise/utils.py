import functools
from flask import request, abort, jsonify


def validate_model(model):
    model = model

    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.json:
                abort(400)
            m = model(request.json)
            if not m.validate():
                resp = jsonify({
                    "message": "Validation Failed",
                    "errors": m.errors
                })
                resp.status_code = 422
                return resp
            #ToDo: Pass Data
            return f(*args, **kwargs)
        return decorated_function
    return decorator
