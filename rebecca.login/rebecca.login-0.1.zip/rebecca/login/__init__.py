#
from pyramid.security import authenticated_userid
from rebecca.repository import get_repository


def authenticated_user(request):
    userid = authenticated_userid(request)
    users = get_repository(request, 'users')
    user = users.get(userid)
    return user


def login(request, user_name, password):
    users = get_repository(request, "users")
    user = users.get(user_name)
    if not user:
        return None

    if not user.validate_password(password):
        return None

    return user_name
