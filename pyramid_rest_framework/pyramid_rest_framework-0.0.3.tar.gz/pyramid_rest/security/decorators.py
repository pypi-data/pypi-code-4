#-*- coding: utf-8 -*-
from pyramid_rest.exceptions import Forbidden
import transaction
from pyramid_rest.security.models import Sessions
from pyramid_rest.autotests import AutoTestManager
from pprint import pformat, pprint
from pyramid_rest.helpers import get_class_that_defined_method


class AllowToGroups:
    """
        Декоратор на resource-представления. Разрешает доступ только тем юзерам, группа которых попадает в **groups**.
        
        Проверяет наличие переданной куки SID в :class:`pyramid_rest.security.models.UserSessions`
        Устанавливает параметр текущего :class:`pyramid_rest.request.Request` request.userid в id текущего юзера.
        
        Если передан параметр cls != None, то метод участвует в автотестах. Параметр cls - имя класса-ресурса.
    """
    def __init__(self, *groups, **kwargs):
        self.groups = groups
        self.cls = kwargs.get("cls", None)
    
    def __call__(self, resource_view):
        def _callback(self_resource):
            request = getattr(self_resource, "request", None) or self_resource
            with transaction.manager:
                SID = Sessions._get(sid = request.cookies.get("SID", None))
                if SID is None or SID.user is None:
                    raise Forbidden(info = {"allowed_groups": self.groups,
                                            "your_group": None})
                else:
                    db_user = SID.user
                    if not db_user:
                        raise Forbidden(info = {"allowed_groups": self.groups,
                                                "your_group": None})
                    
                    request.set_attr("userid", db_user.id)
                    request.set_attr("sid", SID.sid)
                    
                    if self.groups[0] == "all":
                        return resource_view(self_resource)
                    
                    if db_user.group not in self.groups:
                        raise Forbidden(info = {"allowed_groups": self.groups,
                                                "your_group": db_user.group})
                    
                    
                return resource_view(self_resource)
        
        if AutoTestManager().search(view_name = resource_view.__name__, 
                                             resource = self.cls) == []:
            AutoTestManager().META += [{"resource": self.cls,
                                        "method": resource_view.__name__,
                                        "url": None,
                                        "view": _callback,
                                        "auth_required": True,
                                        "auth_groups":self.groups,
                                        "view_name": resource_view.__name__}]
        
        for item in AutoTestManager().search(view_name = resource_view.__name__, 
                                             resource = self.cls):
            item["auth_required"] = True
            item["auth_groups"] = self.groups
        
        _callback.__doc__ = resource_view.__doc__ or ""
        _callback.__name__ = resource_view.__name__
        _callback.__module__ = resource_view.__module__
        
        _callback.__doc__ += u"""
        
.. warning::

    Метод требует авторизации. Разрешенные группы::

        %s
        
        """%pformat(self.groups)
        
        return _callback