from fanery import (
        service, authorize, store, Profile, BaseAcl, Admin,
        add_profile, check_permission, has_permission,
        grant_permission, fetch_record, select_records,
        insert_record, update_record, delete_record
)
from fanery.librand import randpasswd
from fanery.clients import PyClient, WSGIClient
from fanery.crypto import digest

@service(safe = False, ssl = False)
def anonymous():
    return True

@service(ssl = False)
@authorize()
def authenticated():
    return True

@service(ssl = False)
@authorize('admin')
def admin_only():
    return True

@service(ssl = False)
@authorize('user')
def user_only():
    return True

def init_db():
    with store() as db:
        db.insert(Profile, login = 'admin', role = 'admin', password = 'my-secret')
        db.insert(Profile, login = 'user', role = 'user', password = 'my-secret')

def test_authorize():
    init_db()

    for Client in (PyClient, WSGIClient):
        client = Client()
        assert client.call('anonymous') == True
        try:
            client.safe_call('authenticated')
            raise Exception('should have raised authorize.Unauthorized')
        except authorize.Unauthorized:
            client.login('user', 'my-secret')
            assert client.safe_call('authenticated') == True
            assert client.call('anonymous') == True
            client.logout()

        try:
            client.safe_call('admin_only')
            raise Exception('should have raised authorize.Unauthorized')
        except authorize.Unauthorized:
            pass

        client.login('user', 'my-secret')
        try:
            client.safe_call('admin_only')
            raise Exception('should have raised authorize.Unauthorized')
        except authorize.Unauthorized:
            assert client.call('anonymous') == True
            client.logout()
            client.login('admin', 'my-secret')
            assert client.safe_call('admin_only') == True

        try:
            client.safe_call('user_only')
            raise Exception('should have raised authorize.Unauthorized')
        except authorize.Unauthorized:
            assert client.call('anonymous') == True
            client.logout()
            client.login('user', 'my-secret')
            assert client.safe_call('user_only') == True
            client.logout()

def test_add_profile():
    with store() as db:
        db.clearAll()
    user = Admin
    name = 'Administrator'
    passwd = randpasswd()
    admin = add_profile(user, passwd, name = name, is_admin = True)
    assert admin.login == user
    assert admin.role == Admin
    assert admin.name == name
    assert admin.password == digest(passwd)
    # no permission for unauthenticated user
    for term in (admin, Profile, BaseAcl):
        assert not has_permission('select', term)
        assert not has_permission('insert', term)
        assert not has_permission('update', term)
        assert not has_permission('delete', term)
    # authenticated user
    service.state.update(user = admin, role = admin.role)
    assert has_permission('select', admin)
    assert has_permission('update', admin)
    assert not has_permission('insert', admin)
    assert not has_permission('delete', admin)
    for model in (Profile, BaseAcl):
        assert has_permission('select', model)
        assert has_permission('update', model)
        assert has_permission('insert', model)
        assert has_permission('delete', model)
    return admin

if __name__ == '__main__':
    test_authorize()
