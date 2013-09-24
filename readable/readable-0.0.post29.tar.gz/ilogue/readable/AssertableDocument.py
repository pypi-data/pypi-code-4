from bs4 import BeautifulSoup
from ilogue.readable import FormInteraction


class AssertableDocument(object):


    def __init__(self, contents):
        self.contents = contents
        self.soup = BeautifulSoup(self.contents)

    def hasLink(self, name):
        links = self.soup.findAll("a", text=name)
        if not links:
            raise AssertionError('Link with name "{0}" not found.'.format(name))

    def hasA(self, target):
        forms = self.soup.findAll("form")
        mismatches = []
        for form in forms:
            match = target.matchFor(str(form))
            if match.successful:
                break
            else:
                mismatches.append(match)
        else:
            raise AssertionError(("No form matched. failures: {0}".
                    format([str(m) for m in mismatches])))
        return FormInteraction(str(form))

    def containsText(self, text):
        if not text in self.contents:
            raise AssertionError('Target text "{0}" not found.'.format(text))
