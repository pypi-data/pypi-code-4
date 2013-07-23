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


class Event(Package):
    def attend(self, event, status):
        self.app.request_auto()
    
    
    def get_attendees(self, event, page = None, limit = None):
        data = self.app.request_auto()
        return data["attendees"]
    
    
    def get_info(self, event):
        data = self.app.request_auto()
        return data["event"]
    
    
    def get_shouts(self, event, page = None, limit = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    
    def share(self, event, recipient, message = None, public = None):
        self.app.request_auto()
    
    
    def shout(self, event, message):
        self.app.request_auto()
