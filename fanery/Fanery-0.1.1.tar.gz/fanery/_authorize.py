from functools import wraps

from fanery.crypto import gen_token, digest, encrypt, decrypt
from fanery.terms import (
    parse_term, is_string, is_sequence,
    is_subclass, hict, get_timestamp,
)
from fanery import service, store

# Default authorization models
Profile = 'Profile'
Session = 'Session'
BaseAcl = 'BaseAcl'

# Default roles
Admin = 'admin'
User = 'user'

# Default storage for authorization models (testing purpose only)
from fanery.dbms.SimpleMemoryDB import SimpleMemoryDB
store.join(SimpleMemoryDB(), Profile, Session, BaseAcl)

# Profile constraints
store.set_definition(Profile,
    role        = store.data.NotEmptyAlpha(is_required = True),
    login       = store.data.UniqueAlpha(),
    password    = store.data.Password())

# BaseAcl constraints
store.set_definition(BaseAcl,
    rtype   = store.data.NotEmptyAlpha(is_key = True, is_required = True,
                validators = [lambda term: term in store.models or 'unknown-model']),
    rid     = store.data.UUID(is_key = True))

class authorize(object):
    '''Default session authorization implementation.'''

    # in seconds (2 hours)
    SESSION_TIMEOUT = 7200

    # define single session check
    ALLOW_MULTIPLE_SESSIONS_PER_USER = False

    class Unauthorized(AssertionError):
        pass

    class SessionActive(AssertionError):
        pass

    class SessionTimeout(AssertionError):
        pass

    class InvalidCredentials(AssertionError):
        pass

    def __init__(self):
        self.validators = dict(
            users = lambda users: service.state.user.login in users,
            roles = lambda roles: service.state.role in roles,
            grant = lambda grant: check_permission('call', grant))

    def __call__(self, *args, **argd):
        '''Authorization decorator.

        Must be used before @service decorator, like this:

            @service()
            @authorize()
            def auth_only(*args, **argd):
                """Safe and auth protected service.

                Encrypted service call allowed only to authenticated users.
                """
                do something
        '''
        params = hict((k, set(v) if is_sequence(v) else v)
                      for k, v in argd.items())
        if args and not params.roles:
            params.roles = set(args)

        validators = self.validators

        def decorator(func):

            func_name = '%s.%s' % (func.__module__, func.__name__)

            @wraps(func)
            def wrapper(*args, **argd):
                user = service.state.user
                if user is None:
                    raise self.Unauthorized(func_name, user)
                for k, v in params.items():
                    if k in validators and validators[k](v) is False:
                        raise self.Unauthorized(func_name, (user.login, user.role), (k, v))
                return func(*args, **argd)

            return wrapper

        return decorator

    def add_validator(self, name, validator):
        '''Plug new authorization validator.

        name      - the decorator argument associated with validator.
        validator - callable object (must return False to raise Unauthorized).
        '''
        assert callable(validator)
        self.validators[name] = validator

    @staticmethod
    def timed_out(session):
        '''Return True if session timed out (see authorize.SESSION_TIMEOUT).'''
        return (session.tstamp + authorize.SESSION_TIMEOUT) < get_timestamp()

@service(ssl = False, safe = False, auto_parse = False)
def login(username, nonce, tstamp, enc_token, force = False, **argd):
    '''Encrypted user login (default session authorization).'''
    with store() as db:
        user = db.fetch(Profile, login = username, fail = None,
                        **(parse_term(argd) if argd else argd))
        if user is None:
            raise authorize.InvalidCredentials('username')
        try:
            key = digest('%s%s%f' % (nonce, user.password, parse_term(tstamp)))
        except:
            raise AssertionError()
        msg = digest('%s%s%s' % (user.login, nonce, user.password))
        if encrypt(key, msg) != enc_token:
            raise authorize.InvalidCredentials('password',
                    '%s%s%s' % (user.login, nonce, user.password),
                    key, msg, user.login, argd)
        session = None if authorize.ALLOW_MULTIPLE_SESSIONS_PER_USER \
                  else db.fetch(Session, uid = user._uuid, fail = None)
        if session and not (force is True or authorize.timed_out(session)): \
            raise authorize.SessionActive()
        elif session is None:
            session = db.insert(Session, uid = user._uuid, role = user.role,
                                token = gen_token(), tstamp = get_timestamp(),
                                data = dict(), **argd)
        else:
            session.tstamp = get_timestamp()
            session.token = gen_token()
            db.update(session)
    return encrypt(key, dict(sid = session._uuid, token = session.token,
                             user = dict((k,v) for k,v in user._fields.items()
                                         if k[0] != '_' and k != 'password')))

@service(log_exc = True, ssl = False, safe = False, auto_parse = False)
def safe_call(sid, enc_call, **params):
    '''Encrypted call (using default session authorization).'''
    with store() as db:
        session = db.get(Session, parse_term(sid), fail = None)
        if session is None:
            raise authorize.Unauthorized('session')
        elif authorize.timed_out(session):
            raise authorize.SessionTimeout()
        user = db.get(Profile, session.uid, fail = None) if session else None
        if user is None:
            raise authorize.Unauthorized('user')
        token = session.token
        try:
            call, args, argd = decrypt(token, enc_call)
        except:
            raise authorize.Unauthorized('token')
        state = service.state.update(safe = True, user = user,
                        role = session.role, data = session.data)
        if params:
            argd.update(params)
        # consume service and update session token unless static
        call, _, _, ret = service._consume(call, *args, **argd)
        if call.static is True:
            return ret
        elif state.user:
            if call.one_time_pad is True:
                session.token = new_token = gen_token()
            else:
                session.token = new_token = token
            session.tstamp = get_timestamp()
            db.update(session)
        else:
            db.delete(session)
            new_token = None
        return encrypt(token, dict(data = ret, token = new_token))

@service(ssl = False, auto_parse = False)
def logout():
    '''Secure logout.'''
    service.state.clear()
    return True

def grant_permission(*terms, **rules):
    disable = rules.pop('disable', False)
    replace = rules.pop('replace', False)
    merge = rules.pop('merge', False)
    rules = hict(rules)
    for action, action_rules in rules.items():
        if isinstance(action_rules, dict):
            rules[action] = hict((getattr(t, '_uuid', t), bool(b))
                                 for t,b in action_rules.items())
        elif isinstance(action_rules, bool):
            rules[action] = {'*': action_rules}
        else:
            raise TypeError('dict or bool rules expected: %r' % action_rules)
    with store() as db:
        for term in terms:
            if isinstance(term, store.Record):
                rtype = term._model
                rid = term._uuid
            elif is_string(term):
                rtype = term
                rid = None
            else:
                raise TypeError('Record or model name expected: %r' % term)
            acl = db.fetch(BaseAcl, rtype = rtype, rid = rid, fail = None)
            if acl:
                check_permission('update', acl)
                if replace:
                    acl.rules.update(rules)
                else:
                    for action, action_rules in rules.items():
                        actual_rules = acl.rules[action]
                        if merge:
                            actual_rules.merge(action_rules)
                        else:
                            actual_rules.update(action_rules)
                acl.disabled = disable
                db.update(acl)
            else:
                user = service.state.user
                if user:
                    check_permission('insert', BaseAcl)
                    allow = {Admin: True, user._uuid: True}
                else:
                    allow = {Admin: True}
                acl = db.insert(BaseAcl, rtype = rtype, rid = rid,
                                rules = rules, disabled = disable)
                db.insert(BaseAcl, rtype = BaseAcl, rid = acl._uuid, disabled = False,
                                   rules = dict(select = allow,
                                                insert = {'*': False},
                                                update = allow,
                                                delete = allow))

def check_permission(action, term, uuid = None, fail = authorize.Unauthorized):
    state = service.state
    role = state.get('role', None)
    user = getattr(state.get('user', None), '_uuid', None)
    if isinstance(term, store.Record):
        term, uuid = term._model, term._uuid
    if action == 'insert' and uuid:
        rules = False
    else:
        with store() as db:
            acl = db.fetch(BaseAcl, rtype = term, rid = uuid, fail = None)
            rules = acl.rules.get(action, None) if acl and not acl.disabled else None
            if uuid and not (rules is False or (rules and (role in rules or user in rules))):
                acl = db.fetch(BaseAcl, rtype = term, rid = None, fail = None)
                rules = (role == Admin) if not acl else (acl.rules.get(action, False) \
                                                         if not acl.disabled else False)
    if not (rules and rules.get(user, rules.get(role, rules.get('*', False)))):
        if is_subclass(fail, Exception):
            raise fail(role, action, term, uuid, role, rules)
        else:
            return fail
    else:
        return True

def has_permission(*args, **argd):
    argd.setdefault('fail', False)
    return check_permission(*args, **argd)

def add_profile(login, password, role = None, is_admin = False, **extra):
    role = role or (Admin if is_admin else User)
    is_admin = bool(role == Admin)
    with store() as db:
        grant_permission(BaseAcl, Profile, select = {role: True},
                                           insert = {role: True},
                                           update = {role: is_admin},
                                           delete = {role: is_admin})
        user = db.insert(Profile, role = role, login = login,
                                  password = password, **extra)
        grant_permission(user, select = {user: True},
                               insert = False,
                               update = {user: True},
                               delete = {user: False})
        return user

def fetch_record(model, *args, **argd):
    with store() as db:
        record = db.get(model, *args) if args else db.fetch(model, **argd)
        check_permission('select', record)
        return record

def select_records(model, **argd):
    check_permission('select', model)
    with store() as db:
        for record in db.select(model, **argd):
            if has_permission('select', record):
                yield record

def insert_record(model, **data):
    check_permission('insert', model)
    with store() as db:
        return db.insert(model, **data)

def update_record(model, uuid, vsn, **data):
    check_permission('update', model, uuid)
    with store() as db:
        record = db.get(model, uuid)
        if vsn != record._vsn:
            raise store.VersioningMismatch()
        for field, value in data.items():
            setattr(record, field, value)
        return db.update(record)

def delete_record(model, uuid):
    check_permission('delete', model, uuid)
    with store() as db:
        record = db.get(model, uuid)
        db.delete(record)
        return True
