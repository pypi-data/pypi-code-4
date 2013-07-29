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


class Artist(Package):
    def add_tags(self, artist, tags):
        self.app.request_auto()
    
    
    def get_corrections(self, artist):
        data = self.app.request_auto()
        return data["corrections"]
    
    
    def get_events(self, artist = None, page = None, limit = None, autocorrect = None, festivalsonly = None, mbid = None):
        data = self.app.request_auto()
        return data["events"]
    
    
    def get_info(self, artist = None, username = None, autocorrect = None, lang = None, mbid = None):
        data = self.app.request_auto()
        return data["artist"]
    
    
    def get_past_events(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["events"]
    
    
    def get_podcast(self, artist = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["rss"]
    
    
    def get_shouts(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    
    def get_similar(self, artist = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["similarartists"]
    
    
    def get_tags(self, artist = None, user = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["tags"]
    
    
    def get_top_albums(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["topalbums"]
    
    
    def get_top_fans(self, artist = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["topfans"]
    
    
    def get_top_tags(self, artist = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    
    def get_top_tracks(self, artist = None, page = None, limit = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    
    def remove_tag(self, artist, tag):
        self.app.request_auto()
    
    
    def search(self, artist, page, limit):
        data = self.app.request_auto()
        return data["results"]
    
    
    def share(self, artist, recipient, message = None, public = None):
        self.app.request_auto()
    
    
    def shout(self, artist, message):
        self.app.request_auto()
