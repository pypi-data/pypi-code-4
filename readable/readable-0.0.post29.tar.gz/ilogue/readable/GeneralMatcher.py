from ilogue.readable.matcher import Matcher


class GeneralMatcher(Matcher):

    def anything(self):
        return self

    def matchFor(self, other):
        match = MiniMatch()
        return match


class MiniMatch(object):
    successful = True
    message = 'no message'
    
    def __str__(self):
        return self.message

