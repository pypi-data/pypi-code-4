from ilogue.readable.matcher import Matcher
from xml.etree import ElementTree
from bs4 import BeautifulSoup

class PageSection():

    def __init__(self, sectionElement):
        self.section = sectionElement

    def WithPropertyAndValue(self, name, expValue):
        MSG = "Section does not contain property named '{0}'."
        MSGVAL = "Property '{0}' value is '{1}' not '{2}'."

        prop = self.findProperty(name)
        if prop is not None:
            #print(prop.getchildren())
            #print(ElementTree.tostring(prop))
            actualValue = self.propertyValue(prop)
            #print(actualValue)
            if isinstance(expValue, Matcher):
                if not expValue.matches(actualValue):
                    raise AssertionError(str(expValue.matchFor(actualValue)))
            elif not actualValue == expValue:
                raise AssertionError(MSGVAL.format(name, actualValue, expValue))
        else:
            raise AssertionError(self.appendContents(MSG.format(name)))
        return self

    def appendContents(self,message):
        message += '\n\n' + ElementTree.tostring(self.section)
        message = message.rstrip()
        return message

    def findProperty(self, name):
        props = self.section.findall(".//*[@class='property']")
        for prop in props:
            labelElement = prop.find(".//*[@class='label']")
            if labelElement.text == name:
                return prop

    def propertyValue(self, propertyElement):
        #labelElement = propertyElement.find(".//*[@class='label']")
        #return labelElement.tail.strip()
        valueElement = propertyElement.find(".//*[@class='propval']")
        #if valueElement.text is not None:
        #    return valueElement.text
        #else:
        stringValTag = ElementTree.tostring(valueElement)
        valTagSoup = BeautifulSoup(stringValTag)
        valTag = valTagSoup.findAll('html:span')[0]
        val = ''
        for c in valTag.contents:
            val += str(c)
        return val
