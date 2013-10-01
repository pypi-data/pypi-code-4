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


class Point(object):
    __x = None
    __y = None

    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __eq__(self, other_point):
        return isinstance(other_point, Point) and \
            other_point.x == self.x and other_point.y == self.y

    def __str__(self):
        return "(x=%s, y=%s)" % (self.x, self.y)


class Line(object):
    __start = None
    __end = None

    def __init__(self, start, end):
        if not isinstance(start, Point) or\
           not isinstance(end, Point):
                raise TypeError('Start and End points \
                       must be instansed from Point()')
        self.__start = start
        self.__end = end

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end


class Shape(object):
    template_file = None
    name_u = None
    __startPoint = None
    __shapeXML = None
    __width = None
    __height = None
    __label = None
    __id = None

    def __init__(self, id=0, startPoint=Point(0, 0),
            width=2, height=2, label=''):
        self.id = id
        self.__startPoint = startPoint
        self.__width = width
        self.__height = height
        self.__label = label

        tmpl_file = os.path.join(os.path.dirname(__file__),
                                 self.template_file)
        self.__shapeXML = Soup(open(tmpl_file), 'xml')

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, val):
        if not isinstance(val, int):
            raise TypeError("ID can be only integer (val=%s" % val)
        self.__id = val

    @property
    def nameU(self):
        return "%s.%s" % (self.name_u, self.id)

    @property
    def startPoint(self):
        return self.__startPoint

    @startPoint.setter
    def startPoint(self, val):
        if not isinstance(val, Point):
            raise TypeError("StartPoisition can be only Point")
        self.__startPoint = val

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def label(self):
        return self.__label

    @property
    def shapeXML(self):
        return self.__shapeXML

    @property
    def locposition(self):
        return Point(self.width / 2.0, self.height / 2.0)

    def render(self):
        self.fill_id()
        self.fill_nameU()
        self.fill_position()
        self.fill_label()
        self.fill_width_height()
        self.fill_loc_position()
        return self.shapeXML.Shape

    def fill_id(self):
        self.shapeXML.Shape.attrs['ID'] = self.id

    def fill_nameU(self):
        self.shapeXML.Shape.attrs['NameU'] = self.nameU

    def fill_position(self):
        xForm = self.shapeXML.find('XForm')
        xForm.PinX.clear()
        xForm.PinY.clear()
        xForm.PinX.append(str(self.startPoint.x))
        xForm.PinY.append(str(self.startPoint.y))

    def fill_label(self):
        text = self.shapeXML.find('Text')
        text.clear()
        text.append(self.label)

    def fill_width_height(self):
        xForm = self.shapeXML.find('XForm')
        xForm.Width.clear()
        xForm.Height.clear()
        xForm.Width.append(str(self.width))
        xForm.Height.append(str(self.height))

    def fill_loc_position(self):
        xForm = self.shapeXML.find('XForm')
        xForm.LocPinX.clear()
        xForm.LocPinY.clear()
        xForm.LocPinX.append(str(self.locposition.x))
        xForm.LocPinY.append(str(self.locposition.y))


class EPCObject(Shape):
    template_file = None 
    name_u = None 
    __startPoint = None
    __shapeXML = None
    __width = None
    __height = None
    __color = None
    __label = None
    __id = None

    def __init__(self, id=0, startPoint=Point(0, 0), width=2, height=2, \
            color='#FFFFFF', label=''):
        super(EPCObject, self).__init__(id=id, startPoint=startPoint,
                width=width, height=height, label=label)
        self.__color = color

    @property
    def color(self):
        return self.__color

    @property
    def startAnchor(self):
        return Point(self.startPoint.x + self.locposition.x,
                     self.startPoint.y - self.height)

    @property
    def endAnchor(self):
        return Point(self.startPoint.x + self.locposition.x,
                     self.startPoint.y)

    def render(self):
        super(EPCObject, self).render()
        self.fill_connections()
        self.fill_color()
        return self.shapeXML.Shape

    def fill_connections(self):
        connection = self.shapeXML.find('Connection', IX='0')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append(str(self.locposition.x))
        connection.Y.append('0')

        connection = self.shapeXML.find('Connection', IX='1')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append(str(self.locposition.x))
        connection.Y.append(str(self.height))

        connection = self.shapeXML.find('Connection', IX='2')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append('0')
        connection.Y.append(str(self.locposition.y))

        connection = self.shapeXML.find('Connection', IX='3')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append(str(self.width))
        connection.Y.append(str(self.locposition.y))

    def fill_color(self):
        fill_bkg = self.shapeXML.find('FillBkgnd')
        fill_bkg.clear()
        fill_bkg.append(self.color)


class EPCFunction(EPCObject):
    template_file = 'shapes/Function.xml'
    name_u = 'Function'


class EPCEvent(EPCObject):
    template_file = 'shapes/Event.xml'
    name_u = 'Event'


class EPCOrganizationUnit(EPCObject):
    template_file = 'shapes/OrganizationalUnit.xml'
    name_u = 'Organizational unit'


class EPCInformationMaterial(EPCObject):
    template_file = 'shapes/InformationMaterial.xml'
    name_u = 'Information/ Material'


class EPCMainProcess(EPCObject):
    template_file = 'shapes/MainProcess.xml'
    name_u = 'Main process'


class EPCComponent(EPCObject):
    template_file = 'shapes/Component.xml'
    name_u = 'Component'


class EPCEnterpriseArea(EPCObject):
    template_file = 'shapes/EnterpriseArea.xml'
    name_u = 'Enterprise area'

    def fill_connections(self):
        connection = self.shapeXML.find('Connection', IX='0')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append(str(self.locposition.x))
        connection.Y.append(str(self.height))

        connection = self.shapeXML.find('Connection', IX='1')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append('0')
        connection.Y.append(str(self.locposition.y))

        connection = self.shapeXML.find('Connection', IX='2')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append(str(self.width))
        connection.Y.append(str(self.locposition.y))

        connection = self.shapeXML.find('Connection', IX='3')
        connection.X.clear()
        connection.Y.clear()
        connection.X.append(str(self.locposition.x))
        connection.Y.append('0')

    @property
    def startAnchor(self):
        return Point(self.startPoint.x + self.width,
                     self.startPoint.y - self.locposition.y)

    @property
    def endAnchor(self):
        return Point(self.startPoint.x,
                     self.startPoint.y - self.locposition.y)


class EPCProcessGroup(EPCObject):
    template_file = 'shapes/ProcessGroup.xml'
    name_u = 'Process group'

    def fill_connections(self):
        pass

    def fill_color(self):
        pass


class EPCXOR(EPCObject):
    template_file = 'shapes/XOR.xml'
    name_u = 'XOR'

    def fill_label(self):
        pass


class EPCOR(EPCXOR):
    template_file = 'shapes/OR.xml'
    name_u = 'OR'


class EPCAND(EPCXOR):
    template_file = 'shapes/AND.xml'
    name_u = 'AND'


class EPCDynamicConnector(Shape):
    template_file = 'shapes/DinamicConnection.xml'
    name_u = 'Dynamic connector'
    __fromShape = None
    __toShape = None
    __label = None
    __id = None
    __x_begin = 'X1'
    __x_end = 'X2'

    def __init__(self, fromShape, toShape, id=0, label=None, \
            x_begin='X1', x_end='X2'):
        super(EPCDynamicConnector, self).__init__(id=id, label=label,
                                              startPoint=fromShape.startAnchor)
        self.__fromShape = fromShape
        self.__toShape = toShape
        self.x_begin = x_begin
        self.x_end = x_end

    @property
    def x_begin(self):
        return self.__x_begin

    @x_begin.setter
    def x_begin(self, val):
        self.__x_begin = val

    @property
    def x_end(self):
        return self.__x_end

    @x_end.setter
    def x_end(self, val):
        self.__x_end = val

    @property
    def width(self):
        return ''

    @property
    def height(self):
        #return self.endXY.y - self.beginXY.y
        return ''

    @property
    def locposition(self):
        return Point(0, 0)

    @property
    def beginXY(self):
        return self.startPoint

    @property
    def endXY(self):
        return self.toShape.endAnchor

    @property
    def fromShape(self):
        return self.__fromShape

    @property
    def toShape(self):
        return self.__toShape

    def render(self):
        super(EPCDynamicConnector, self).render()
        self.fill_begin_end_XY()
        return self.shapeXML.Shape

    def fill_begin_end_XY(self):
        self.fill_begin_end_XY_formula()
        self.fill_begin_end_XY_coords()

    def fill_begin_end_XY_formula(self):
        xForm1D = self.shapeXML.find('XForm1D')
        xForm1D.BeginX.attrs['F'] = "_WALKGLUE(EndTrigger,BegTrigger,WalkPreference)"
        xForm1D.BeginY.attrs['F'] = "_WALKGLUE(EndTrigger,BegTrigger,WalkPreference)"

        xForm1D.EndX.attrs['F'] = "_WALKGLUE(EndTrigger,BegTrigger,WalkPreference)"
        xForm1D.EndY.attrs['F'] = "_WALKGLUE(EndTrigger,BegTrigger,WalkPreference)"

        misc = self.shapeXML.find('Misc')
        misc.BegTrigger.attrs['F'] = "_XFTRIGGER(%s!EventXFMod)" \
                % self.fromShape.nameU
        misc.EndTrigger.attrs['F'] = "_XFTRIGGER(%s!EventXFMod)" \
                % self.toShape.nameU

    def fill_begin_end_XY_coords(self):
        xForm1D = self.shapeXML.find('XForm1D')

        xForm1D.BeginX.clear()
        xForm1D.BeginY.clear()
        xForm1D.BeginX.append('')
        xForm1D.BeginY.append('')

        xForm1D.EndX.clear()
        xForm1D.EndY.clear()
        xForm1D.EndX.append('')
        xForm1D.EndY.append('')
