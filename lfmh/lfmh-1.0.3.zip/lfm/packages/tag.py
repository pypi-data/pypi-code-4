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


class Tag(Package):
    def get_info(self, tag = None, lang = None):
        data = self.app.request_auto()
        return data["tag"]
    
    
    def get_similar(self, tag):
        data = self.app.request_auto()
        return data["similartags"]
    
    
    def get_top_albums(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["topalbums"]
    
    
    def get_top_artists(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    
    def get_top_tags(self, ):
        data = self.app.request_auto()
        return data["toptags"]
    
    
    def get_top_tracks(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    
    def get_weekly_artist_chart(self, tag, limit = None, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    
    def get_weekly_chart_list(self, tag):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    
    def get_search(self, tag, page = None, limit = None):
        data = self.app.request_auto()
        return data["results"]
