
User = 'User'

class MemDictStore(object):

    transactional = False

    def __init__(self, auth_hooks = None):
        self._models = dict()
        self._sessions = dict()
        if isinstance(auth_hooks, dict):
            auth_hooks.update(load_state = self.load_state,
                              store_state = self.store_state,
                              destroy_state = self.destroy_state,
                              user_sessions = self.user_sessions,
                              fetch_user = self.fetch_user,
                              get_user = self.get_user)

    def add_model(self, model, indexer):
        self._models[model] = dict()

    def upsert(self, txn, record):
        self._models[record._model][record._uuid] = record
    insert = update = upsert

    def delete(self, txn, record):
        del self._models[record._model][record._uuid]

    def fetch(self, model, uuid, vsn = None, txn = None):
        record = self._models[model][uuid]
        assert not vsn or record._vsn == vsn
        assert not txn or record._txn == txn
        return record._vsn, record._txn, record._dct

    def query(self, model, fun, score = None):
        for record in filter(fun, self._models[model].itervalues()):
            uuid, vsn, txn = record._uuid, record._vsn, record._txn
            yield score is not None and (uuid, vsn, txn, score) \
                                     or (uuid, vsn, txn)

    def search(self, model, fun):
        return self.query(model, fun, 1)

    def select(self, model, fun):
        return self.query(model, fun)

    def get_user(self, uuid):
        return self._models[User][uuid]

    def user_sessions(self, uuid):
        return len(self._sessions.get(uuid, None) or {})

    def fetch_user(self, uid, **extra):
        for record in self._models[User].itervalues():
            if record.login == uid:
                if not extra:
                    return record
                else:
                    dct = record._dct
                    for k, v in extra.iteritems():
                        if k in dct and dct[k] == v:
                            continue
                        else:
                            break
                    else:
                        return record

    def load_state(self, sid):
        return self._sessions.get(sid, None) or {}

    def store_state(self, state):
        self._sessions[state.sid] = state

    def destroy_state(self, state):
        del self._sessions[state.sid]

