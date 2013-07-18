# -*- encoding: utf-8 -*-
"""
@authors: Sebastián Ortiz V. neoecos@gmail.com

@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Server is the web server of Caliope's Framework
Copyright (C) 2013 Infometrika

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#system, and standard library
import os
import json
import re
import mimetypes
import gzip
import StringIO

#flask
from flask import request, current_app

#werkezug
from werkzeug.datastructures import Headers
from werkzeug.wsgi import wrap_file
from werkzeug.exceptions import NotFound


def loadJSONFromFile(filename, root_path):
    if filename is not None:
        if not os.path.isabs(filename):
            filename = os.path.join(root_path, filename)
    if not os.path.isfile(filename):
        raise NotFound("JSON file" + filename + " not found")
    try:
        json_data = re.sub("(?:/\\*(?:[^*]|(?:\\*+[^*/]))*\\*+/)",
                           '', open(filename).read(), re.MULTILINE)
        json_data = json.loads(json_data)
    except IOError:
        json_data = {}
        print "Error: can\'t find file or read data"
    except ValueError:
        json_data = {}
        print "Error, is not a JSON" + filename
    else:
        return json_data


def send_from_memory(filename):
    """

    :param filename: Name of the file to be loaded.
    """
    if not os.path.isfile(filename):
        raise NotFound()
    if filename is not None:
        if not os.path.isabs(filename):
            filename = os.path.join(current_app.root_path, filename)
    mimetype = mimetypes.guess_type(filename)[0]
    if mimetype is None:
        mimetype = 'application/octet-stream'
    file = open(filename, 'rb')
    data = wrap_file(request.environ, file)
    headers = Headers()
    rv = current_app.response_class(data, mimetype=mimetype, headers=headers,
                                    direct_passthrough=False)
    return rv

#From
#https://github.com/elasticsales/Flask-gzip/blob/master/flask_gzip.py
class Gzip(object):
    def __init__(self, app, compress_level=6, minimum_size=500):
        self.app = app
        self.compress_level = compress_level
        self.minimum_size = minimum_size
        self.app.after_request(self.after_request)

    def after_request(self, response):
        accept_encoding = request.headers.get('Accept-Encoding', '')

        if 'gzip' not in accept_encoding.lower():
            return response

        if response.direct_passthrough:
            return response

        if (200 > response.status_code >= 300) or len(
                response.data) < self.minimum_size or 'Content-Encoding' in response.headers:
            return response

        gzip_buffer = StringIO.StringIO()
        gzip_file = gzip.GzipFile(mode='wb', compresslevel=self.compress_level, fileobj=gzip_buffer)
        gzip_file.write(response.data)
        gzip_file.close()
        response.data = gzip_buffer.getvalue()
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Content-Length'] = len(response.data)

        return response