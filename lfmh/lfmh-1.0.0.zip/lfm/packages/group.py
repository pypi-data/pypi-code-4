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


class Group(Package):
    def get_hype(self, group):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    
    def get_members(self, group, page = None, limit = None):
        data = self.app.request_auto()
        return data["members"]
    
    
    def get_weekly_album_chart(self, group, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyalbumchart"]
    
    
    def get_weekly_artist_chart(self, group, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklyartistchart"]
    
    
    def get_weekly_chart_list(self, group):
        data = self.app.request_auto()
        return data["weeklychartlist"]
    
    
    def get_weekly_track_chart(self, group, from_ = None, to = None):
        data = self.app.request_auto()
        return data["weeklytrackchart"]
