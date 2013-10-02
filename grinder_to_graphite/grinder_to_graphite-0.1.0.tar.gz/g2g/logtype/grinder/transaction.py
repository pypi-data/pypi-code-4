# Copyright (C) 2013-2013, Travis Bear
# All rights reserved.
#
# This file is part of Grinder to Graphite.
#
# Grinder to Graphite is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Grinder to Graphite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Grinder to Graphite; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from g2g.logtype.grinder import column_map


class NonHTTPTest(object):
    def __init__(self, words):
        self.time = float(words[column_map.TEST_TIME])
        self.errors = float(words[column_map.ERRORS])


class HTTPTest(NonHTTPTest):
    def __init__(self, words):
        NonHTTPTest.__init__(self, words)
        self.http_rc = int(words[column_map.HTTP_RESPONSE_CODE])
        self.http_response_length = float(words[column_map.HTTP_RESPONSE_LENGTH])
        self.http_response_errors = float(words[column_map.HTTP_RESPONSE_ERRORS])
        self.resolve_host_time = float(words[column_map.RESOLVE_HOST_TIME])
        self.establish_connect_time = float(words[column_map.ESTABLISH_CONNECTION_TIME])
        self.first_byte_time = float(words[column_map.FIRST_BYTE_TIME])
        self.new_connections = float(words[column_map.NEW_CONNECTIONS])
