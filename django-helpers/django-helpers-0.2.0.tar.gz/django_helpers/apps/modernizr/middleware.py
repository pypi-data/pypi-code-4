# coding=utf-8
from json import loads

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.utils.crypto import get_random_string


__author__ = 'ajumell'

_no = '__no_js_data__'
_key = '__check_js_key__'
_name = '__check_js_name__'
_sess_name = "js_data"

# TODO: Make this in to a app.
# TODO: Add Modernizr data to request.
# TODO: Set data to session from request if session is flushed.


class CheckJsMiddleware:
    def process_request(self, request):
        """
        Provides Modernizr information in the django side of the app.
        @param request: The current http request object.
        @type request:django.http.HttpRequest
        @return: None
        """
        method = request.method
        session = request.session
        js_data = session.get(_sess_name, _no)
        if js_data == _no:
            if method == "POST":
                post = request.POST

                name = session.get(_name)
                key = session.get(_key)

                if name is None:
                    raise Exception('Name not found')

                if key is None:
                    raise Exception('Key not found')

                if name not in post:
                    raise Exception('Name "%s" is not in POST' % name)

                if key not in post:
                    raise Exception('Key "%s" is not in POST' % name)

                js_str = post.get(name, _no)
                if js_str == _no:
                    # Hack attempt
                    raise

                if js_str == name:
                    js_data = False
                else:
                    try:
                        js_data = loads(js_str)
                    except Exception:
                        raise Exception('%s != %s' % (name, js_str))
                session[_sess_name] = js_data
                return HttpResponseRedirect(request.get_full_path())
            else:
                key = session.get(_key) or get_random_string(12)
                name = session.get(_name) or get_random_string(12)

                session[_key] = key
                session[_name] = name

                return render(request, 'modernizr/detect-js.html', {
                    "key": key,
                    "name": name
                })
        else:
            request.Modernizr = js_data
