# -*- coding: utf-8 -*-
"""
    odisea.utils.StorageUtils
    ~~~~~~~~~~~~~~

    Este módulo contiene funciones y clases que son utilizadas por
    el módelo de almacenamiento.

    :author: Sebastián Ortiz <neoecos@gmail.com>
    :copyright: (c) 2013 por Fundación CorreLibre
    :license:  GNU AFFERO GENERAL PUBLIC LICENSE

Caliope Storage is the base of Caliope's Framework
Copyright (C) 2013  Fundación Correlibre

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

import uuid
import json
from datetime import datetime
from pytz import utc


#: uuid version 4
def uuidGenerator():
    return str(uuid.uuid4()).decode('utf-8')


#: All timestamps should be in UTC
def timeStampGenerator():
    return datetime.now(utc)


def getBase64():
    pass


