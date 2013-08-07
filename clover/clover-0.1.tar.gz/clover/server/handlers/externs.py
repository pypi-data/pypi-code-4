from clover.server.handlers.base import Base
from clover.server.handlers.compile import CACHE

class Handler(Base):
    def get(self, id):
        config = self.get_config(id)
        self.data['config'] = config
        
        if id in CACHE:
            self.response.write(CACHE[id].externs)
        else:
            # TODO: notify that compilation is required
            return