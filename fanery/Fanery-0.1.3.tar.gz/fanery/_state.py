"""
Handle sessions in execution stack.
"""
__all__ = ['get_state']

from time import time as timestamp
from inspect import currentframe

from _term import Hict

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
    _state_ = hooks.load_state(sid)
    if _state_:
        assert _state_.expires > timestamp(), 'session-timeout: %s' % sid
        _state_.user = auth_hooks.get_user(_state_.user)
    else:
        default = dict(origin = None, domain = 'localhost', sid = sid,
                       user = None, role = None, data = State(),
                       expires = timestamp() + hooks.SESSION_TIMEOUT,
                       token = None, timeout = hooks.SESSION_TIMEOUT)
        default.update(data)
        _state_ = State(default)
        store_state(_state_)
    return _state_

def store_state(state):
    state.expires = timestamp() + hooks.SESSION_TIMEOUT
    state = State(state)
    state.user = getattr(state.user, '_uuid', None)
    hooks.store_state(state)

def clear_state(state):
    state.data.clear()
    state.expires = 0

def user_sessions(uid):
    return hooks.user_sessions(uid)

sessions = dict()

hooks = Hict(load_state = lambda sid: sessions.get(sid, None),
             store_state = lambda state: sessions.__setitem__(state.sid, state)\
                        if state.expires else sessions.__delitem__(state.sid),
             user_sessions = lambda uid: sum(v.user == uid for v in
                                             sessions.itervalues()),
             SESSION_TIMEOUT = 900)

from _auth import hooks as auth_hooks
