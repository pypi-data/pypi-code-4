__all__ = ['login', 'logout', 'get_state', 'User']

from time import time as timestamp
from inspect import currentframe

from _term import Hict, gen_uuid, to_json, to_simple
from _crypto import AES, gen_token

class State(Hict): pass

def get_state():
    frame = current = currentframe()
    while frame:
        _state_ = frame.f_locals.get('_state_', None)
        if isinstance(_state_, State):
            if current is not frame:
                current.f_locals['_state_'] = _state_
            return _state_
        else:
            frame = frame.f_back
    return current.f_locals.setdefault('_state_', State())

def load_state(sid, **data):
    _state_ = State(hooks.load_state(sid))
    if _state_:
        assert _state_.expires > timestamp(), 'session-timeout: %s' % sid
        _state_.user = hooks.get_user(_state_.user)
    else:
        default = dict(origin = None, domain = 'localhost', sid = sid,
                       user = None, role = None, data = State(),
                       expires = timestamp() + hooks.SESSION_TIMEOUT,
                       token = None, timeout = hooks.SESSION_TIMEOUT)
        default.update(data)
        _state_.update(default)
        store_state(_state_)
    return _state_

def store_state(state):
    state.expires = timestamp() + hooks.SESSION_TIMEOUT
    state.user = getattr(state.user, '_uuid', None)
    hooks.store_state(state)

def _undefined(msg):
    def undefined(*args, **argd):
        raise AssertionError(msg)
    return undefined

hooks = Hict(load_state = _undefined('undefined auth.hooks.load_state'),
             store_state = _undefined('undefined auth.hooks.store_state'),
             destroy_state = _undefined('undefined auth.hooks.destroy_state'),
             user_sessions = _undefined('undefined auth.hooks.user_sessions'),
             fetch_user = _undefined('undefined auth.hooks.fetch_user'),
             get_user = _undefined('undefined auth.hooks.get_user'),
             MAX_ACTIVE_USER_SESSIONS = 1,
             SESSION_TIMEOUT = 900,
             ONE_TIME_TOKEN = True)

from _service import service

@service(safe = False, ssl = False, auto_parse = False, log_exc = False)
def login(uid, nonce, enc, force = False, **extra):
    user = hooks.fetch_user(uid, **extra)
    assert user, ('invalid-uid', uid)
    data = AES(nonce + user.password).decrypt(enc)
    assert data.count('|') == 2, ('bad-format', data)
    tstamp, _nonce, client_token = data.split('|', 2)
    assert tstamp.isdigit() and (timestamp() - int(tstamp)) < 1800, \
            ('invalid-timestamp', tstamp)
    assert _nonce == nonce, ('invalid-password', uid)
    if force is not True:
        active_user_sessions = hooks.user_sessions(user._uuid)
        assert active_user_sessions < hooks.MAX_ACTIVE_USER_SESSIONS, \
                ('active-sessions', active_user_sessions, user._uuid, sessions)
    sid, token = gen_uuid(), gen_token()
    _state_ = load_state(sid)
    assert not _state_.token, 'unexpected-state'
    _state_.update(user = user, role = user.role or user.login, token = token)
    _state_.data.update(extra)
    store_state(_state_)
    answer = dict(sid = sid, token = token, role = _state_.role)
    return AES(client_token).encrypt(to_json(to_simple(answer)))

@service(ssl = False, auto_parse = False, log_exc = True)
def logout(*args, **argd):
    _state_ = get_state()
    _state_.expires = 0
    hooks.destroy_state(_state_)
    return True
