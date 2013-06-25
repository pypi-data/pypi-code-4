import xml.etree.ElementTree as ET


class CaliopeXMLForms:
  def __init__(self, name=None, version=None, language=None ):
    self._dict = {}
    self.name = name
    self.version = version
    self.language = language
  
  def readfromXML(self,filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    self.name = root.find('name').text
    self.version = root.find('version').text
    self.language = root.find('language').text

    for field in root.iter('field'):
      field_id = field.attrib.get('id',None)
      
      if field_id is None:
        continue
      else:
        for options in field:
          print options.tag, options.attrib

   
form = CaliopeXMLForms()
form.readfromXML('person.xml')

print form.name
print form.version
print form.language