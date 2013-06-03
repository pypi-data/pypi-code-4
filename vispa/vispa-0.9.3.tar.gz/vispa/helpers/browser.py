# -*- coding: utf-8 -*-

# imports
import cherrypy


def set_cookie(key, value="", age=None, path="/", version=None):
    if key is None:
        return False
    cookie = cherrypy.response.cookie
    try:
        cookie[key] = value
        cookie[key]["path"] = path
        cookie[key]["max-age"] = age
        cookie[key]["version"] = version
        return True
    except:
        return False

def get_cookie(key):
    if key is None:
        return None
    cookie = cherrypy.request.cookie
    try:
        return cookie[key].value
    except:
        return None

def delete_cookie(key):
    if key is None:
        return False
    cookie = cherrypy.response.cookie
    try:
        cookie[key] = ""
        cookie[key]["expires"] = 0
        return True
    except:
        return False

def set_session_value(key, value=None):
    if key is None:
        return False
    if value is None:
        try:
            del cherrypy.session[key]
            return True
        except:
            return False
    else:
        cherrypy.session[key] = value
        return True

def append_to_session(key, value):
    """ Adds a value to a list in the session
    """
    if key is None:
        return False
    l = get_session_value(key)
    l = l or []
    if not isinstance(l, list):
        return False
    l.append(value)
    set_session_value(key, l)
    return True

def update_to_session(key, data):
    if key is None:
        return False
    d = get_session_value(key)
    d = d or {}
    if not isinstance(d, dict):
        return False
    d.update(data)
    set_session_value(key, d)
    return True

def get_session_value(key):
    if key is None:
        return None
    try:
        return cherrypy.session.get(key)
    except:
        return None

def has_session_value(key):
    if key is None:
        return False
    return key in cherrypy.session.keys()

def delete_session():
    try:
        cherrypy.lib.sessions.expire()
        return True
    except:
        return False

def client_agent():
    if "User-Agent" in cherrypy.request.headers.keys():
        return cherrypy.request.headers["User-Agent"]
    return ""

def client_ip():
    if "X-Forwarded-For" in cherrypy.request.headers.keys():
        return cherrypy.request.headers["X-Forwarded-For"]
    elif "Remote-Addr" in cherrypy.request.headers.keys():
        return cherrypy.request.headers["Remote-Addr"]
    return ""

def client_referer():
    if "Referer" in cherrypy.request.headers.keys():
        return cherrypy.request.headers["Referer"]
    return ""
