class RouteNotFound(RuntimeError):
    pass


class EngineNotFound(RuntimeError):
    def __init__(self, engine_name, ext):
        self.ext = ext
        self.engine = engine_name

    def __str__(self):
        return ('There is no {} engine associated with {}'
                ' extension'.format(self.engine,
                                    self.ext))
