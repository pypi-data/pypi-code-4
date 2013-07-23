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


"""
Holds :py:class:`Album`.

"""


from lfm.package import Package


class Album(Package):
    """
    Represents the `API <http://www.last.fm/api>`_'s album package.
    
    """
    
    def add_tags(self, artist, album, tags):
        """
        Tag an album using a list of supplied tags. 
        
        :param artist:
            The album's artist.
            
        :type artist:
            string
            
        :param album:
            The name of the album.
            
        :type album:
            string
            
        :param tags:
            Tags the album will be tagged with.
            
        :type tags:
            :class:`list <python:list>` of :mod:`strings <python:string>`
        
        .. seealso:: `addTags on Last.fm <http://www.last.fm/api/show/album.addTags>`_
        
        """
        
        self.app.request_auto()
    
    
    def get_buy_links(self, country, artist = None, album = None, mbid = None, autocorrect = None):
        """
        Get a list of Buy Links for a particular Album. It is required that you supply either the artist and track params or the mbid param. 
        
artist (Required (unless mbid)] : The artist name
album (Required (unless mbid)] : The album
mbid (Optional) : The musicbrainz id for the album
autocorrect[0|1] (Optional) : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response.
country (Required) : A country name or two character country code, as defined by the ISO 3166-1 country names standard.
        
        """
        
        data = self.app.request_auto()
        return data["affiliations"]
    
    
    def get_info(self, artist = None, album = None, username = None, autocorrect = None, lang = None, mbid = None):
        data = self.app.request_auto()
        return data["album"]
    
    
    def get_shouts(self, artist = None, album = None, page = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["shouts"]
    
    
    def get_tags(self, artist = None, album = None, user = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["tags"]
    
    
    def get_top_tags(self, artist = None, album = None, autocorrect = None, mbid = None):
        data = self.app.request_auto()
        return data["toptags"]
    
    
    def remove_tag(self, tag, artist, album):
        self.app.request_auto()
    
    
    def search(self, album, page = None, limit = None):
        data = self.app.request_auto()
        return data["results"]
