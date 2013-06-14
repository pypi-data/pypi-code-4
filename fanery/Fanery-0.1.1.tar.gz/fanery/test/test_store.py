from fanery import store, service, Profile

def test_single_txn():
    session = service.state
    with store() as db:
        state = service.state
        assert state is session, (session, state)
        assert state.txn, state
        with store() as db1:
            assert service.state is state
            assert service.state.txn is state.txn, (service.state, state)

def test_data_terms():
    fields = ((store.data.Term('term'), False, False, False, 0),
              (store.data.Link(model = Profile), False, False, False, 1),
              (store.data.Links(model = Profile), False, False, False, 1),
              (store.data.Boolean(), False, False, False, 1),
              (store.data.Number(), False, False, False, 1),
              (store.data.UUID(), False, False, False, 1),
              (store.data.Date(), False, False, False, 1),
              (store.data.Dict(), False, False, False, 1),
              (store.data.File(), False, False, False, 1),
              (store.data.List(), False, False, False, 1),
              (store.data.String(), False, False, False, 1),
              (store.data.Timestamp(), False, True, True, 1),
              (store.data.NotEmptyString(), False, False, True, 2),
              (store.data.NotEmptyAlpha(name = 'nealpha'), False, False, True, 3),
              (store.data.UniqueString(name = 'ustr'), True, True, True, 2),
              (store.data.UniqueAlpha(name = 'ualpha'), True, True, True, 3),
              (store.data.Password(), False, True, True, 4))
    for field, unique, required, not_null, vlen in fields:
        name = field.get('name', field.basetype)
        assert isinstance(name, basestring), name
        assert field.is_unique is unique, (name, field, unique)
        assert field.is_required is required, (name, field, required)
        assert field.not_null is not_null, (name, field, not_null)
        assert isinstance(field.validators, tuple), (name, field)
        assert len(field.validators) == vlen, (name, field.validators, vlen)

