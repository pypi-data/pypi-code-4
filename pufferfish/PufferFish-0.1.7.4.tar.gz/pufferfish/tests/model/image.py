import logging
from elixir import Field, Unicode, Entity
from pufferfish import add_session_hooks
from pufferfish import FileSystemEntity

from exc import CreateThumbnailExc, RenameThumbnailExc

__session__ = None
log = logging.getLogger(__name__)

class Image(FileSystemEntity):
    add_session_hooks()

    def set_name(self, name):
        self.name = name
    
    def create_thumbnail(self, source):
        raise CreateThumbnailExc
    
    def rename_thumbnail(self, old_name, new_name):
        assert old_name != new_name
        raise RenameThumbnailExc
    
