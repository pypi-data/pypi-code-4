# -*- encoding: utf-8 -*-
#Python VDX - simple package for working with MS Visio files
#Copyright (C) 2013  Strata Tech Ltd (www.stratatech.ru)

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from bs4 import BeautifulSoup as Soup
from shapes import Point


def idIterator():
    id = 0
    while 1:
        id += 1
        yield id


class Connect(object):
    def __init__(self, connectLineShape):
        self.connectId = connectLineShape.id
        self.fromShapeId = connectLineShape.fromShape.id
        self.toShapeId = connectLineShape.toShape.id
        self.XB = connectLineShape.x_begin
        self.XE = connectLineShape.x_end

    def render(self):
        xml = """
<Connects>
    <Connect FromSheet="%(connectId)s" FromCell="BeginX" FromPart="9" ToSheet="%(fromShapeId)s" ToCell="Connections.%(XB)s" ToPart="3" />
    <Connect FromSheet="%(connectId)s" FromCell="EndX" FromPart="12" ToSheet="%(toShapeId)s" ToCell="Connections.%(XE)s" ToPart="3" />
</Connects>
        """
        params = {'connectId': self.connectId,
                  'fromShapeId': self.fromShapeId,
                  'toShapeId': self.toShapeId,
                  'XB': self.XB,
                  'XE': self.XE,
                  }
        return Soup(xml % params, 'xml')


class Diagramm(object):
    __diagramm = None
    __top = None

    def __init__(self, top=Point(1, 11)):
        template_file = os.path.join(os.path.dirname(__file__),
                                     'shapes/diagramm_body.xml')
        self.__diagramm = Soup(open(template_file), 'xml')
        self.__genId = idIterator()
        self.__shapes = []
        self.__top = top

    @property
    def top(self):
        return self.__top

    @top.setter
    def top(self, val):
        self.__top = val

    @property
    def diagramm(self):
        return self.__diagramm

    @property
    def genId(self):
        return self.__genId.next()

    @property
    def shapes(self):
        return self.__shapes

    def render(self):
        self.fill_shapes()
        self.fill_connects()
        return self.diagramm

    def fill_shapes(self):
        shapes_plase_on_dia = self.diagramm.findAll('Shapes')[-1]
        for shape in self.shapes:
            shapes_plase_on_dia.append(shape.render())

    def fill_connects(self):
        connects_plase_on_dia = self.diagramm.find('Connects')
        for shape in self.shapes:
            if self.isConnectShape(shape):
                self.append_connect(shape, connects_plase_on_dia)

    def isConnectShape(self, shape):
        return hasattr(shape, 'fromShape') and hasattr(shape, 'toShape')

    def append_connect(self, connectShape, connects_plase_on_dia):
        connectSoup = Connect(connectShape)
        for connect in connectSoup.render().findAll('Connect'):
            connects_plase_on_dia.append(connect)

    def append_shape(self, shape):
        shape.id = self.genId
        shape.startPoint = self.set_real_position(shape.startPoint)
        self.__shapes.append(shape)

    def set_real_position(self, shapePosition):
        return Point(self.top.x + shapePosition.x,
                     self.top.y + shapePosition.y)

    def save(self, fileName):
        with open(fileName, 'wb') as diagrammFile:
            diagrammFile.write(str(self.render()))
            diagrammFile.close()
