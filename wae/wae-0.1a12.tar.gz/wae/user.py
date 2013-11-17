#coding: utf-8

class User(object):
    "请求用户"

    def __init__(self, tenant_id, user_id, **kwargs):
        self.tenant_id = tenant_id
        self.user_id = user_id
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.ctx = None

    def set_context(self, ctx):
        self.ctx = ctx

