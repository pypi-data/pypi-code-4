from pecan import expose


class RootController(object):

    @expose()
    def index(self):
        return 'Root Index'
