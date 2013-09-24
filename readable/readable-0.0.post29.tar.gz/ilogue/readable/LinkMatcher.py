from ilogue.readable.matcher import Matcher
from bs4 import BeautifulSoup


class LinkMatcher(Matcher):
    name = None

    def matchFor(self, other):
        match = MiniMatch()
        soup = BeautifulSoup(other)
        links = soup.findAll("html:a")
        if not links:
            match.successful = False
            match.message = ('No links found in [{0}].'.format(other))
            return match
        elif len(links) > 1:
            match.successful = False
            match.message = ('Found multiple links, only expecting one: [{0}].'.format(other))
            return match
        link = links[0]
        if not link.contents[0] == self.name:
            match.successful = False
            match.message = ('Link is not named "{0}":{1}'.format(self.name ,link))
            return match
        self.exportedLink.address = link['href']
        return match

    def named(self, name):
        self.name = name
        return self

    def exportAddress(self, exportedLink):
        self.exportedLink = exportedLink
        return self

class Link(object):
    name = ''
    address = ''

class MiniMatch(object):
    successful = True
    message = 'no message'
    
    def __str__(self):
        return self.message

