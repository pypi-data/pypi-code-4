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
Holds :py:class:`App`.

"""

import  hashlib
import  inspect
import  json
from    lfm         import lfm
from    lfm         import exceptions   as e
from    lfm         import packages     as pkg
from    lfm.package import Package
import  requests
import  sqlite3
import  time


class App:
    """
    Represents a single Last.fm application.
    
    A Last.fm application is associated with an `API account <http://www.last.fm/api/account/create>`_.
    
    :param key:
        The key of an API account.
        
    :type key:
        string
    
    :param secret:
        The secret of an API account.
    
    :type secret:
        string
    
    :param db:
        The name of the file which will hold a :mod:`sqlite3 <python:sqlite3>` database
        tied to this application. The purpose of the database is to keep track of the
        number of requests made, so the application can comply to the
        point 4.4 of  `Last.fm's API Terms of Service <http://www.last.fm/api/tos>`_.
        If the parameter is *None*, the library will not limit the number of requests
        in any way, but the Last.fm servers probably will.
        
    :type db:
        string
    
    """
    
    album       = None
    artist      = None
    auth        = None
    chart       = None
    event       = None
    geo         = None
    group       = None
    library     = None
    playlist    = None
    radio       = None
    tag         = None
    tasteometer = None
    track       = None
    user        = None
    venue       = None
    
    key     = None
    secret  = None
    info    = None
    sk      = None
    
    db  = None
    dbc = None


    def __init__(self, key, secret, db_file = None, info = None):
        self.album       = pkg.Album(self)
        self.artist      = pkg.Artist(self)
        self.auth        = pkg.Auth(self)
        self.chart       = pkg.Chart(self)
        self.event       = pkg.Event(self)
        self.geo         = pkg.Geo(self)
        self.group       = pkg.Group(self)
        self.library     = pkg.Library(self)
        self.playlist    = pkg.Playlist(self)
        self.radio       = pkg.Radio(self)
        self.tag         = pkg.Tag(self)
        self.tasteometer = pkg.Tasteometer(self)
        self.track       = pkg.Track(self)
        self.user        = pkg.User(self)
        self.venue       = pkg.Venue(self)
        
        self.key    = key
        self.secret = secret
        self.info   = info
        
        if db_file is not None:
            self.db = sqlite3.connect(db_file)
            self.dbc = self.db.cursor()
            
            if not self.db_table_exists_timestamps():
                self.db_create_table_timestamps()
        

    def request(self, pkg, method, params):
        """
        Makes an API request.
        
        :param pkg:
            The name of the package in which the method resides.
            
        :type pkg:
            string
            
        :param method:
            The name of the method.
            
        :type method:
            string
            
        :param params:
            Parameters to be sent.
            
        :type params:
            dict
            
        :returns:
            The response.
            
        :rtype:
            :mod:`json object <python:json>`
        
        """
        
        if not self.can_request():
            raise e.RateLimitExceeded("Exceeded the limit of one request per five seconds over five minutes.")
    
    
        params.update({"api_key": self.key,
                       "method": pkg + "." + method,
                       "sk": self.sk,
                       "format": "json"})
    
        # Remove keys with a value of None.
        params = dict((key, params[key]) for key in params if params[key] is not None)
        
        # Convert all objects to strings, as expected by the API
        for key in params.copy():
            if isinstance(params[key], bool):
                if params[key]:
                    params[key] = "1"
                else:
                    params[key] = "0"
    
            elif not isinstance(params[key], str):
                try:
                    params[key] = ",".join(params[key])
    
                except TypeError:
                    params[key] = str(params[key])
        
        params["api_sig"] = self.sign_request(params)
        
        
        if self.info is None:
            info = ("unknown", "unknown")
        else:
            info = self.info
        
        user_agent = "{}/{} {}".format(info[0], info[1], lfm.USER_AGENT)
        headers =   {
                     "User-Agent": user_agent,
                     }
        
        resp = requests.post(lfm.API_ROOT, params, headers = headers)
        self.log_request()
        data = json.loads(resp.text)
        
        try:
            raise e.codes[data["error"]](data["message"])
        except KeyError:
            pass
        
        return data


    def request_auto(self, special_params = None, pkg = None, method = None):
        """
        An automated version of :py:func:`request`, designed to reduce repetitive code.
        
        It will generate the package, method and request parameters from its
        calling function's signature. If the caller is in a class, *self* is ignored.
        If the caller is in a class whose parent or ancestor is :py:class:`lfm.package.Package`, then the
        class' name is used as the name of the package. The caller's name, stripped of underscores,
        is used as the name of the method. Argument names are used as parameter keys, and argument
        values as parameter values. Argument names are stripped of trailing underscores,
        to permit use of keywords as parameter keys.
        
        :param special_params:
            Additional parameters merged with automatically generated ones.
            
        :type special_params:
            :class:`dict <python:dict>`
            
        :param pkg:
            The name of the package in which the method resides.
            
        :type pkg:
            :mod:`string <python:string>`
            
        :param method:
            The name of the method.
            
        :type method:
            :mod:`string <python:string>`
            
        :returns:
            The response.
            
        :rtype: :mod:`json object <python:json>`
        
        """
        
        frame_record = inspect.stack()[1]
    
        if(method is None):
            method = frame_record[3].replace("_", "").lower()
            
        args, _, _, locals_ = inspect.getargvalues(frame_record[0])
        params = dict((arg, locals_[arg]) for arg in args)
        
        for key, value in params.items():
            if key == "self":
                params[key] = None
                
                if isinstance(value, Package):
                    pkg = value.__class__.__name__.lower()
    
        if(special_params is not None):
            params.update(special_params)
    
        params = dict((key.rstrip('_'), params[key]) for key in params)
    
        return self.request(pkg, method, params)
    

    def sign_request(self, params):
        """
        Generates an API signature, which is needed for authorized API requests.
        
        :param params:
            All parameters intended to be sent with the request.
            
        :type params:
            dict
            
        :returns:
            The signature.
            
        :rtype:
            :mod:`string <python:string>`
        
        """
    
        # Parameters are alphabetically sorted by their key, and then concatenated
        # in a keyvalue manner. The application's secret is appended afterwards,
        # the whole thing is UTF-8 encoded, and then md5() hashed, hex digest of it
        # being the signature. Some parameters mustn't be included in the calculation.
    
        # Keys excluded from the calculation
        forbid_keys = ["format"]
    
        concat_params = ""
        for key in sorted(list(params)):
            if key not in forbid_keys:
                concat_params += key + params[key]
    
        concat_params += self.secret
    
        sig = hashlib.md5(concat_params.encode("utf-8")).hexdigest()
        
        return sig


    def can_request(self):
        if self.requests_logged() >= lfm.MAX_REQUESTS:
            return False
        else:
            return True
    
    
    def log_request(self):
        if self.db is None:
            return
        
        self.dbc.execute("insert into timestamps (timestamps) values (?)", (int(time.time()),))
        self.db.commit()
    
    
    def requests_logged(self):
        if self.db is None:
            return 0
        
        self.dbc.execute("delete from timestamps where timestamps < ?", (int(time.time()) - lfm.REQUEST_RATE_PERIOD,))
        self.dbc.execute("select count(timestamps) from timestamps")
        requests = self.dbc.fetchone()[0]
        self.db.commit()
        
        return requests
    
    
    def db_table_exists_timestamps(self):
        self.dbc.execute("select exists(select * from sqlite_master " \
                         "where type = \"table\" and name = \"timestamps\")")
        return self.dbc.fetchone()[0]
    
    
    def db_create_table_timestamps(self):
        self.dbc.execute("create table timestamps (timestamps integer)")
        self.db.commit()
    