from flask import request


class PJAX(object):

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.context_processor(self.pjax_processor)
        app.config.setdefault('PJAX_BASE_TEMPLATE', 'pjax.html')
        self.app = app

    def pjax_processor(self):
        def get_template(base, pjax=None):
            pjax = pjax or self.app.config.get('PJAX_BASE_TEMPLATE')
            if "X-PJAX" in request.headers:
                return pjax
            else:
                return base
        return dict(pjax=get_template)
