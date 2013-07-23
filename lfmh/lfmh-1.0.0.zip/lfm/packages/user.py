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


class User(Package):
    def get_artist_tracks(self, user, artist, page = None, starttimestamp = None, endtimestamp = None):
        data = self.app.request_auto()
        return data["artisttracks"]
    
    
    def get_banned_tracks(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["bannedtracks"]
    
    
    def get_events(self, user, page = None, limit = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    
    def get_friends(self, user, page = None, limit = None, recenttracks = None):
        data = self.app.request_auto()
        return data["friends"]
    
    
    def get_info(self, user = None):
        data = self.app.request_auto()
        return data["user"]
    
    
    def get_loved_tracks(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["lovedtracks"]
    
    
    def get_neighbours(self, user, limit = None):
        data = self.app.request_auto()
        return data["neighbours"]
    
    
    def get_new_releases(self, user, userecs = None):
        data = self.app.request_auto()
        return data["albums"]
    
    
    def get_past_events(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["events"]
    
    
    def get_personal_tags(self, user, tag, taggingtype, page = None, limit = None):
        data = self.app.request_auto()
        return data["taggings"]
    
    
    def get_playlists(self, user):
        data = self.app.request_auto()
        return data["playlists"]
    
    
    def get_recent_stations(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["recentstations"]
    
    
    def get_recent_tracks(self, user, extended = None, page = None, limit = None, from_ = None, to = None):
        data = self.app.request_auto()
        return data["recenttracks"]
    
    
    def get_recommended_artists(self, page = None, limit = None):
        data = self.app.request_auto()
        return data["recommendations"]
    
    
    def get_recommended_events(self, page = None, limit = None, latitude = None, longitude = None, festivalsonly = None):
        data = self.app.request_auto()
        return data["events"]
    
    
    def get_shouts(self, user, page = None, limit = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    
    def get_top_albums(self, user, period = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["topalbums"]
    
    
    def get_top_artists(self, user, period = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["topartists"]
    
    
    def get_top_tags(self, user, limit = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    
    def get_top_tracks(self, user, period = None, page = None, limit = None):
        data = self.app.request_auto()
        return data["toptracks"]
    
    
    def get_weekly_album_chart(self, user, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyalbumchart"]
    
    
    def get_weekly_artist_chart(self, user, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    
    def get_weekly_chart_list(self, user):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    
    def get_weekly_track_chart(self, user, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklytrackchart"]
    
    
    def shout(self, user, message):
        self.app.request_auto()
