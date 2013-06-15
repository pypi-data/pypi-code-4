'''
Copyright 2012 Alexey Kravets  <mr.kayrick@gmail.com>

This file is part of PythonMindmeister.

PythonMindmeister is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PythonMindmeister is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PythonMindmeister.  If not, see <http://www.gnu.org/licenses/>.

This file implements key->value interface to the settings storage. 
Settings must be stored in XML file specified in the 
constructor of the settings class.

This product uses the MindMeister API but is not endorsed or certified
by MindMeister.
'''


from lxml import etree

schema = \
'''\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.w3.org/2001/XMLSchema" targetNamespace="http://www.example.org/schema" xmlns:tns="http://www.example.org/schema" elementFormDefault="qualified">
  <element name="config">
    <complexType>
      <sequence>
        <element minOccurs="1" maxOccurs="unbounded" name="value">
          <complexType>
            <simpleContent>
              <extension base="string">
                <attribute name="key" type="string" use="required"/>
               </extension>
            </simpleContent>
          </complexType>
        </element>
      </sequence>
    </complexType>
  </element>
</schema>
'''


class SettingsStorage:
    '''
    This class implements key->value interface to the settings storage.
    Settings are loaded from the file specified in constructor.
    '''
    def __init__(self, filename):
        rawXML = open(filename).read()
        etreeSchema = etree.XMLSchema(etree.XML(schema))
        parser = etree.XMLParser(schema = etreeSchema)
        root = etree.fromstring(rawXML, parser)
        self.data = {}
        for item in root:
            key = item.attrib['key']
            value = item.text
            self.data[key] = value
    def store(self):
        pass
