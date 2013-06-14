from fanery.filelib import joinpath, files, tempdir, savefile, filename, filesize
from fanery import service, static, store, authorize, crypto, dbms

store.register(dbms.DummyMemoryDB(), store.models_names)

Session = authorize.Session.model_name
Profile = authorize.Profile.model_name

@service(safe = False, _log_exc = False)
def login(username, nonce, tstamp, enc_token, force = False, **argd):
    with store() as db:
        user = db.fetch(Profile, login = username, fail = None, **argd)
        assert user is not None, 'username'
        key = '%s%s%s' % (nonce, user.password, tstamp)
        msg = crypto.digest('%s%s%s' % (user.login, nonce, user.password))
        assert crypto.encrypt(key, msg) == enc_token, 'enc_token'
        session = None if authorize.allow_multiple_sessions_per_user \
                  else db.fetch(Session, uid = user._uuid, fail = None)
        assert not session or force or authorize.timed_out(session), 'active'
        if session is None:
            session = db.insert(Session, uid = user._uuid, data = dict(),
                                         token = gen_token(), **argd)
        else:
            session.token = gen_token()
            db.update(session)
    return crypto.encrypt(key, dict(sid = session._uuid,
                                    name = user.full_name,
                                    token = session.token))

@service(safe = False, _log_exc = False)
def safe_call(sid, enc_call, **params):
    with store() as db:
        session = db.get(Session, sid, fail = None)
        user = db.get(Profile, session.uid, fail = None) if session else None
        assert user and not authorize.timed_out(session), 'expired'
        token, session.token = session.token, gen_token()
        call, args, argd = crypto.decrypt(token, enc_call)
        if params: argd.update(params)
        service.state.update(user = user, data = session.data)
        answer = dict(data = service.consume(call, args, argd, False),
                      token = session.token)
        db.update(session)
        return crypto.encrypt(token, answer)

@service()
def logout(_log_exc = False):
    service.state.clear()
    return True

@service(safe = False, auto_parse = False)
def arguments(*args, **argd):
    return dict(args = args, argd = argd)

@service(safe = False, auto_parse = True)
def params(*args, **argd):
    return dict(args = args, argd = argd)

@static(root = tempdir(), force_download = True)
@authorize()
def download(*path):
    return joinpath(*path)

@service()
@authorize()
def upload(*args, **argd):
    return [dict(name = filename(fh),
                 size = filesize(savefile(fh, tempdir())))
            for fh in files(*args, **argd)]

@service()
@authorize()
def find(*args, **argd):
    with store() as db:
        return db.select(*args, **argd)

@service()
@authorize()
def add(*args, **argd):
    with store() as db:
        return db.insert(*args, **argd)

@service()
@authorize()
def store(*args, **argd):
    with store() as db:
        return db.update(*args, **argd)

@service()
@authorize()
def remove(*args, **argd):
    with store() as db:
        return db.delete(*args, **argd)
