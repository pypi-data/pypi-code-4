# -*- encoding: utf-8 -*-
'''
@author: Andrés Felipe Calderón andres.calderon@correlibre.org
@license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Storage is the base of Caliope's Framework
Copyright (C) 2013 Fundación Correlibre

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
'''
#system, and standard library
import os

#gevent
from gevent import sleep

#flask
from flask import Blueprint, Response


server_notifications = Blueprint('server_notifications', __name__,
                                 template_folder='')


def event_stream():
    count = 0
    while True:
        sleep(3)
        f = os.popen('fortune')
        yield 'data: %s\n\n' % f.read()
        f.close()
        # yield 'data: %s\n\n' % count
        count += 1


@server_notifications.route('/')
def sse_request():
    return Response(
        event_stream(),
        mimetype='text/event-stream')
