#
# A Last.fm API interface.
# Copyright (C) 2013  Никола "hauzer" Вукосављевић
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from lfm.package import Package
from lfm.util import to_array, to_arrays


class Library(Package):
    def add_album(self, albums):
        params = to_arrays(albums, ["artist", "album"])
        albums = None
    
        data = self.app.request_auto(params)
        return data["albums"]
    
    
    def add_artist(self, artists):
        params = to_array(artists, "artist")
        artists = None
    
        data = self.app.request_auto(params)
        return data["artists"]
    
    
    def add_track(self, artist, track):
        self.app.request_auto()
    
    
    def get_albums(self, user, artist, limit = None, page = None):
        data = self.app.request_auto()
        return data["albums"]
    
    
    def get_artists(self, user, limit = None, page = None):
        data = self.app.request_auto()
        return data["artists"]
    
    
    def get_tracks(self, user, artist, album, limit = None, page = None):
        data = self.app.request_auto()
        return data["tracks"]
    
    
    def remove_album(self, artist, album):
        self.app.request_auto()
    
    
    def remove_artist(self, artist):
        self.app.request_auto()
    
    
    def remove_scrobble(self, artist, track, timestamp):
        self.app.request_auto()
    
    
    def remove_track(self, artist, track):
        self.app.request_auto()
