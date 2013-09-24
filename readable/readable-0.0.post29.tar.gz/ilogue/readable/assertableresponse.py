from webtest import TestResponse
from xml.etree import ElementTree
from xml.etree.ElementTree import ParseError
from ilogue.readable.formmatcher import FormMatcher
from ilogue.readable.PageSection import PageSection
from ilogue.readable.PageList import PageList



class AssertableResponse(object):

    def __init__(self, response, content = None):
        if response is None and content is None:
            raise ValueError(
                'Requires either a response or a content argument.')
        if response:
            self.isTestappBased = True
            content = response.body
        else:
            response = TestResponse(body=content)
            self.isTestappBased = False

        self.content = content
        self.response = response
        try:
            self.root = ElementTree.fromstring(self.content)
            self.containsXml = True
        except ParseError as error:
            if 'no element found' in str(error): #fail unless no elements at all
                self.containsXml = False
            else:
                raise AssertionError(str(error) + '\n' + self.content)
        if self.containsXml:
            self.registerNamespace()

    def hasForm(self):
        forms = self.response.forms
        if len(forms) == 0:
            raise AssertionError("Did not find any Form.")
        else:
            return FormMatcher(forms, testappBased=self.isTestappBased)

    def registerNamespace(self):
        if '{' in self.root.tag:
            self.namespace = self.root.tag.split('}')[0][1:]
        else:
            self.namespace = None

    def _wrapNamespace(self, tag):
        if self.namespace:
            return '{' + self.namespace + '}' + tag
        else:
            return tag

    def hasSection(self, sectionLabel):
        MSG = "Page does not have a section called '{0}'."
        fieldsetPath = './/' + self._wrapNamespace('fieldset')
        sections = self.root.findall(fieldsetPath)
        assert sections, "Page has no sections."
        for section in sections:
            labelElement = section.find(self._wrapNamespace('legend'))
            if labelElement is not None:
                if labelElement.text == sectionLabel:
                    break
        else:
            raise AssertionError(MSG.format(sectionLabel))
        return PageSection(section)

    def hasList(self):
        listPath = './/' + self._wrapNamespace('ul')
        lists = self.root.findall(listPath)
        if not lists:
            raise AssertionError("Page has no list." + '\n\n' + self.content)
        return PageList(ElementTree.tostring(lists[0]))

    def containsTextSomewhere(self,text):
        MSG = 'Response does not contain text "{0}":'
        msg = self._appendContents(MSG.format(text))
        if not (text in self.content):
            raise AssertionError(msg)

    def _appendContents(self,message):
        if self.containsXml:
            message += '\n\n' + str(ElementTree.tostring(self.root))
        message = message.rstrip()
        return message

