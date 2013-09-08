# -*- coding: utf-8 -*-

from pyramid.events import subscriber, NewRequest
from pyramid.security import authenticated_userid

from . import get_user_model


@subscriber(NewRequest)
def add_user(event):
    request = event.request

    UserModel = get_user_model(request.registry)

    userid = authenticated_userid(request)
    if userid:
        request.user = UserModel.query().filter_by(username=userid).first()
    else:
        request.user = None
