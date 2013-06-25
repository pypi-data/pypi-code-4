# -*- encoding: utf-8 -*-
'''
Created on 30/05/2013

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

class CaliopeField():
    db_type = ''
  
class IntegerField(CaliopeField):
    db_type = 'int'

class RealField(CaliopeField):
    db_type = 'real'
    
class TextField(CaliopeField):
    db_type = 'text'
    
class ByteArrayField(CaliopeField):
    db_type = 'bytearray'

class TimeStampField(CaliopeField):
    db_type = 'timestamp'
    
    
class CaliopeNode(object):   
    __isfrozen = False

    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.values = {}


    def __setattr__(self, key, value):     
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError( "%r is a frozen CaliopeNode class" % self )
        if key in self.__dict__:
            if (isinstance(self.__dict__[key],CaliopeField)):
                self.values[key]=value
        else:
            object.__setattr__(self, key, value)


    #def __getattribute__(self, name):
        #print "__getattribute__" + name
        #if name in self.__dict__:
            #if (isinstance(self.__dict__[name],CaliopeField)):
                #self.values[name]
            #else:
                #return self.__dict__[key]
        #return object.__getattribute__(self, name)


    def _freeze(self):
        self.__isfrozen = True


    def ShowFields(self):
        print self.name  + " " + self.version
        for field in  self.__dict__:
            if (isinstance(self.__dict__[field],CaliopeField)):
                print "'" + field + "' is " + self.__dict__[field].db_type 
                if field in self.values:
                    print "'" + field + "' value = " + str(self.values[field])
                    
        
class CaliopeEdge:   
    def __init__(self, name):
        self.name = name

    def ShowAttributes(self):
        print self.name
        for field in  self.__dict__:
            if (isinstance(self.__dict__[field],CaliopeField)):
                print "'" + field + "' is " + self.__dict__[field].db_type