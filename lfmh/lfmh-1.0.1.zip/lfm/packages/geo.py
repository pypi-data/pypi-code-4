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


class Geo(Package):
    def get_events(self, tag = None, page = None, limit = None, long = None,
                   lat = None, location = None, distance = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    
    def get_metro_artist_chart(self, metro, country, page = None, limit = None,
                               start = None, end = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    
    def get_metro_hype_artist_chart(self, metro, country, page = None, limit = None,
                                    start = None, end = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    
    def get_metro_hype_track_chart(self, metro, country, page = None, limit = None,
                                   start = None, end = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    
    def get_metro_track_chart(self, metro, country, page = None, limit = None,
                              start = None, end = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    
    def get_metro_unique_artist_chart(self, metro, country, page = None, limit = None,
                                      start = None, end = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    
    def get_metro_unique_track_chart(self, metro, country, page = None, limit = None,
                                     start = None, end = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    
    def get_metro_weekly_chart_list(self, metro):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    
    def get_metros(self, country = None):
        data = self.app.request_auto()
        return data["metros"]
    
    
    def get_top_artists(self, country, page = None, limit = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    
    def get_top_tracks(self, country, page = None, limit = None, location = None):
        data = self.app.request_auto()
        return data["toptracks"]
