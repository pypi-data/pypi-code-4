import httplib
import logging
import bsddb

from tilecloud import Tile, TileStore
from tilecloud.layout.template import TemplateTileLayout


logger = logging.getLogger(__name__)


class BerkeleyDbTileStore(TileStore):
    """Tiles stored in Berkeley DB"""

    def __init__(self, file_name, tilelayout=None, dbOpenType=bsddb.hashopen, **kwargs):
        self.db = bsddb.hashopen(file_name, 'c')
        self.tilelayout = tilelayout if tilelayout is not None else
                TemplateTileLayout('%(z)d/%(y)d/%(x)d')
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile):
        if not tile:
            return False
        key_name = self.tilelayout.filename(tile.tilecoord)
        return self.db.has_key(key_name)

    def delete_one(self, tile):
        key_name = self.tilelayout.filename(tile.tilecoord)
        self.db.db.remove(key_name)
        return tile

    def get_one(self, tile):
        key_name = self.tilelayout.filename(tile.tilecoord)
        tile.data = self.db.get(key_name)
        return tile

    def list(self):
        cursor = self.db.cursor()
        record = cursor.first()
        while record:
            tilecoord = self.tilelayout.tilecoord(record[0])
            yield Tile(tilecoord, data=record[1])

    def put_one(self, tile):
        assert tile.data is not None
        key_name = self.tilelayout.filename(tile.tilecoord)
        seld.db.db.put(key_name, tile.data)
        return tile
