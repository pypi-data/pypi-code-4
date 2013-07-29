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


VERSION     = "1.0.3"
USER_AGENT  = "lfm/{}".format(VERSION)

API_ROOT                = "https://ws.audioscrobbler.com/2.0/"
REQUEST_RATE_PERIOD     = 300
REQUEST_RATE_INTERVAL   = 5
MAX_REQUESTS            = REQUEST_RATE_PERIOD / REQUEST_RATE_INTERVAL
