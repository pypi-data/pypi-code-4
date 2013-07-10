"""
Python wrapper for lkd.to API.
@author Karan Goel
@email karan@goel.im

Copyright (C) 2013  Karan Goel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import requests

class lkd:
    def __init__(self, user):
        """
        Initialize a new lkd object for the passed user.
        """
        self.user = user
        self.data = self.get_json()
        if self.data['about'] == False:
            raise Exception('Invalid username.')
        
    def get_json(self):
        """
        Returns the json response for the user.
        """
        url = 'http://lkd.to/api/' + self.user
        response = requests.get(url)
        return response.json()

    def about(self):
        """
        Returns a dictionary with details about the user. Contains:
        id, username, email, realname, bio, status, added, updated,
        theme
        """
        return self.data['about']

    def links(self):
        """
        Returns a dictionary with user's social links
        """
        links = {}
        data = self.data['links']
        for key in data:
            links[key] = data[key]['url']
        return links

    def vcf(self):
        """
        Downloads the vcf card for the user in current directory.
        """
        name = self.user + '.vcf'
        url = 'http://lkd.to/api/' + name
        r = requests.get(url)
        with open(name, 'wb') as code:
            code.write(r.content)
