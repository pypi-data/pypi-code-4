# http://mbtiles.org/

import mimetypes
import sqlite3
from hashlib import sha1

from tilecloud import Bounds, BoundingPyramid, Tile, TileCoord, TileStore
from tilecloud.lib.sqlite3_ import SQLiteDict, query
from tilecloud.store.mbtiles import Metadata


class Images(SQLiteDict):
    """A dict facade for the images table"""

    CREATE_TABLE_SQL = 'CREATE TABLE IF NOT EXISTS images (tile_data BLOB, tile_hash BLOB, tile_id INTEGER PRIMARY KEY AUTOINCREMENT)'
    CONTAINS_SQL = 'SELECT COUNT(*) FROM images WHERE tile_hash = ?'
    DELITEM_SQL = 'DELETE FROM images WHERE tile_hash = ?'
    GETITEM_SQL = 'SELECT tile_data FROM images WHERE tile_hash = ?'
    ITER_SQL = 'SELECT tile_hash FROM images'
    ITERITEMS_SQL = 'SELECT tile_hash, tile_data FROM images'
    ITERVALUES_SQL = 'SELECT tile_data FROM images'
    LEN_SQL = 'SELECT COUNT(*) FROM images'
    SETITEM_SQL = 'INSERT OR REPLACE INTO images (tile_id, tile_data) VALUES (?, ?)'

    def __init__(self, *args, **kwargs):
        SQLiteDict.__init__(self, *args, **kwargs)

class Map(SQLiteDict):
    """A dict facade for the tiles table"""

    CREATE_TABLE_SQL = 'CREATE TABLE IF NOT EXISTS map (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_id integer, PRIMARY KEY (zoom_level, tile_column, tile_row))'
    CONTAINS_SQL = 'SELECT COUNT(*) FROM map WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    DELITEM_SQL = 'DELETE FROM map WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    GETITEM_SQL = 'SELECT tile_id FROM map WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    ITER_SQL = 'SELECT zoom_level, tile_column, tile_row FROM map'
    ITERITEMS_SQL = 'SELECT zoom_level, tile_column, tile_row, tile_id FROM map'
    ITERVALUES_SQL = 'SELECT tile_id FROM map'
    LEN_SQL = 'SELECT COUNT(*) FROM map'
    SETITEM_SQL = 'INSERT OR REPLACE INTO map (zoom_level, tile_column, tile_row, tile_id) VALUES (?, ?, ?, ?)'

    def __init__(self, tilecoord_in_topleft, *args, **kwargs):
        self.tilecoord_in_topleft = tilecoord_in_topleft
        SQLiteDict.__init__(self, *args, **kwargs)

    def _packitem(self, key, value):
        y = key.y if self.tilecoord_in_topleft else (1 << key.z) - key.y - 1
        return (key.z, key.x, y, sqlite3.Binary(value) if value is not None else None)

    def _packkey(self, key):
        y = key.y if self.tilecoord_in_topleft else (1 << key.z) - key.y - 1
        return (key.z, key.x, y)

    def _unpackitem(self, row):
        z, x, y, data = row
        y = y if self.tilecoord_in_topleft else (1 << z) - y - 1
        return (TileCoord(z, x, y), data)

    def _unpackkey(self, row):
        z, x, y = row
        y = y if self.tilecoord_in_topleft else (1 << z) - y - 1
        return TileCoord(z, x, y)


class TilesView(SQLiteDict):
    """A dict facade for the tiles table"""

    CREATE_TABLE_SQL = 'CREATE VIEW IF NOT EXISTS tiles AS SELECT map.zoom_level AS zoom_level, map.tile_column AS tile_column, map.tile_row AS tile_row, images.tile_data AS tile_data FROM map JOIN images ON images.tile_id = map.tile_id'
    CONTAINS_SQL = 'SELECT COUNT(*) FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    GETITEM_SQL = 'SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?'
    ITER_SQL = 'SELECT zoom_level, tile_column, tile_row FROM tiles'
    ITERITEMS_SQL = 'SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles'
    ITERVALUES_SQL = 'SELECT tile_data FROM tiles'
    LEN_SQL = 'SELECT COUNT(*) FROM tiles'

    def __init__(self, tilecoord_in_topleft, *args, **kwargs):
        self.tilecoord_in_topleft = tilecoord_in_topleft
        SQLiteDict.__init__(self, *args, **kwargs)

    def _packitem(self, key, value):
        y = key.y if self.tilecoord_in_topleft else (1 << key.z) - key.y - 1
        return (key.z, key.x, y, sqlite3.Binary(value) if value is not None else None)

    def _packkey(self, key):
        y = key.y if self.tilecoord_in_topleft else (1 << key.z) - key.y - 1
        return (key.z, key.x, y)


class MBTilesViewIdTileStore(TileStore):
    """A MBTiles tile store"""

    BOUNDING_PYRAMID_SQL = 'SELECT zoom_level, MIN(tile_column), MAX(tile_column) + 1, MIN((1 << zoom_level) - tile_row - 1), MAX((1 << zoom_level) - tile_row - 1) + 1 FROM tiles GROUP BY zoom_level ORDER BY zoom_level'
    SET_METADATA_ZOOMS_SQL = 'SELECT MIN(zoom_level), MAX(zoom_level) FROM tiles'

    def __init__(self, tilecoord_in_topleft, connection, commit=True, **kwargs):
        self.connection = connection
        self.metadata = Metadata(self.connection, commit)
        self.images = Images(self.connection, commit)
        self.tiles_images_map = Map(tilecoord_in_topleft, self.connection, commit)
        self.tiles = TilesView(tilecoord_in_topleft, self.connection, commit)
        if 'content_type' not in kwargs and 'format' in self.metadata:
            kwargs['content_type'] = mimetypes.types_map.get('.' + self.metadata['format'], None)
        TileStore.__init__(self, **kwargs)

    def __contains__(self, tile):
        return tile and tile.tilecoord in self.tiles

    def __len__(self):
        return len(self.tiles)

    def delete_one(self, tile):
        del self.tiles_images_map[tile.tilecoord]
        return tile

    def get_all(self):
        for tilecoord, data in self.tiles.iteritems():
            tile = Tile(tilecoord, data=str(data))
            if self.content_type is not None:
                tile.content_type = self.content_type
            yield tile

    def get_cheap_bounding_pyramid(self):
        bounds = {}
        for z, xstart, xstop, ystart, ystop in query(self.connection, self.BOUNDING_PYRAMID_SQL):
            bounds[z] = (Bounds(xstart, xstop), Bounds(ystart, ystop))
        return BoundingPyramid(bounds)

    def get_one(self, tile):
        try:
            tile.data = str(self.tiles[tile.tilecoord])
        except KeyError:
            return None
        if self.content_type is not None:
            tile.content_type = self.content_type
        return tile

    def list(self):
        return (Tile(tilecoord) for tilecoord in self.tiles)

    def put_one(self, tile):
        data = getattr(tile, 'data', None)
        if data is not None:
            sha_one = buffer(sha1(data).digest())
            self.images[sha_one] = buffer(data)
            self.tiles_images_map[tile.tilecoord] = self.images[sha_one].tile_id
        return tile

    def set_metadata_zooms(self):
        for minzoom, maxzoom in query(self.connection, self.SET_METADATA_ZOOMS_SQL):
            self.metadata['minzoom'] = minzoom
            self.metadata['maxzoom'] = maxzoom
