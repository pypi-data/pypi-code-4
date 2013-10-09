from clover.server.handlers.base import Base

class Handler(Base):
    def get(self, id):
        config = self.get_config(id)
        self.data['config_id'] = id
        self.data['config'] = config 
        manifest = config.get_build_manifest()
        sources = manifest.all_sourcefiles
        self.data['sources'] = sorted(sources)
        return self.render_template('templates/list_sources.jinja')