from clover.server.handlers.base import Base

class Index(Base):
    def get(self):
        self.data['configs'] = self.get_configs()
        
        return self.render_template('templates/list_configs.jinja')