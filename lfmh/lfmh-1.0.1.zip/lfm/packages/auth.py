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
from lfm.token import Token


class Auth(Package):
    def get_mobile_session(self, username, password):
        data = self.app.request_auto()
        return data["session"]
    
    
    def get_session(self, token):
        data = self.app.request_auto()
        return data["session"]
    
    
    def get_token(self):
        data = self.app.request_auto()
        token = Token(self.app, data["token"])
        
        return token
