__all__ = ['service', 'static']

from _term import parse_term, parse_json, to_simple, to_json, to_str, is_str
from _auth import load_state, store_state, get_state, hooks
from _crypto import AES, hmac, gen_token

from os.path import splitext
from functools import wraps
import logging
import cgitb
import sys

registry = dict()

def decrypt(enc):
    assert enc and is_str(enc) and enc.count('|') == 1, ('bad-format', enc)
    sid, enc = enc.split('|', 1)
    sid = parse_term(sid)
    _state_ = load_state(sid)
    assert _state_.token, ('null-token', sid, _state_)
    aes = AES(_state_.token)
    sign, json = aes.decrypt(enc).split('|', 1)
    assert sign == hmac(_state_.token, json), ('bad-signature', sid)
    return _state_, parse_json(json)

def encrypt(_state_, term):
    assert _state_.token, ('null-token', _state_.sid)
    token, json = _state_.token, to_json(to_simple(term))
    new_token = gen_token() if hooks.ONE_TIME_TOKEN else token
    sign = hmac(token, '|'.join((new_token, str(_state_.sid), json)))
    aes = AES(token)
    enc = aes.encrypt('|'.join((sign, new_token, json)))
    _state_.token = new_token
    if _state_.expires > 0:
        store_state(_state_)
    return enc

def service(urlpath = None, auto_parse = True, static = False, cache = False, \
            force_download = False, safe = True, ssl = True, log_exc = True, \
            _REMOVE_force = False, **filters):

    assert urlpath not in registry or force, ('already-defined', urlpath)

    filters.setdefault('json', to_json)
    filters.setdefault('txt', to_str)
    filters.setdefault('raw', repr)

    def decorator(f):
        key = (urlpath or f.__name__).strip('/')
        for k, v in filters.iteritems():
            assert k and k.isalnum() and callable(v), ('bad-filter', k, v)

        @wraps(f)
        def wrapper(*args, **argd):
            _state_ = get_state()
            if ssl is True:
                assert _state_.ssl, ('ssl-required', urlpath)
            if safe is True:
                enc = args[0] if args else argd.pop('enc', None)
                state, params = decrypt(enc)
                _state_.update(state)
                argd.update(params)
            if auto_parse is True:
                args = parse_term(args) if args else args
                argd = parse_term(argd) if argd else argd
            try:
                ret = f(*args, **argd)
            except Exception, e:
                if log_exc is True:
                    logging.error(cgitb.text(sys.exc_info()))
                if safe is True:
                    return encrypt(_state_, dict(exc = e.args))
                else:
                    raise
            else:
                return encrypt(_state_, ret) if safe is True else ret

        wrapper.ssl = ssl
        wrapper.safe = safe
        wrapper.urlpath = key
        wrapper.cache = cache
        wrapper.static = static
        wrapper.log_exc = log_exc
        wrapper.filters = filters
        wrapper.auto_parse = auto_parse
        wrapper.force_download = force_download

        return registry.setdefault(key, wrapper)

    return decorator

def static(urlpath, root, index = None, **argd):

    from os.path import normpath, realpath, isdir, isfile, join

    root = join(realpath(normpath(root)), '')
    assert isdir(root), ('no-such-directory', root)

    @service(urlpath, auto_parse = False, static = True, safe = False, **argd)
    def serve_file(*args, **argd):
        filepath = realpath(normpath(join(root, *args)))
        if isdir(filepath) and index:
            filepath = join(filepath, index)
        assert isfile(filepath) and filepath.startswith(root), \
                ('not-found', filepath)
        return filepath

    return serve_file

acl_rules = dict(role = lambda s, roles, *args, **argd: s.role in roles,
                 user = lambda s, users, *args, **argd: s.login in users)

def set_acl_rule(name, func):
    acl_rules[name] = func

def acl(**rules):

    for k, v in rules.iteritems():
        validator = acl_rules.get(k, v)
        assert callable(validator), ('invalid-acl', k)
        rules[k] = (v, validator)

    def decorator(f):
        assert hasattr(f, 'urlpath'), ('not-a-service', f)

        @wraps(f)
        def wrapper(*args, **argd):
            _state_ = get_state()
            for k, (v, valid) in rules.iteritems():
                assert valid(_state_, v, *args, **argd), ('unauthorized', k, v)
            return f(*args, **argd)

        return wrapper

    return decorator

def lookup(urlpath):

    path, ext = splitext(urlpath.strip().strip('/'))
    args = []

    while path not in registry:
        try:
            path, arg = path.rsplit('/', 1)
            args.append(arg)
        except ValueError:
            break

    fun = registry.get(path, None)

    if not fun:
        try:
            prefix, urlpath = urlpath.split('/', 1)
            return lookup(urlpath)
        except ValueError:
            pass

    out = fun.filters.get(ext[1:], False) if ext and fun else None

    if args:
        args.reverse()
        if fun and fun.static is True:
            args[-1] += ext

    return fun, args, ext, out

def consume(_state_, urlpath, *args, **argd):
    fun, argv, ext, out = lookup(urlpath)

    assert callable(fun), ('not-found', urlpath)
    if ext and not fun.static:
        assert callable(out), ('bad-format', ext)

    argv.extend(args)
    ret = fun(*argv, **argd)
    return fun, ext, out(ret) if ext else ret
