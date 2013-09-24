from ilogue.readable.matcher import Matcher
from bs4 import BeautifulSoup


class FormMatcher(Matcher):

    def __init__(self):
        self.targetSubmitLabel = None


    def withSubmitButtonLabeled(self, label):
        self.targetSubmitLabel = label
        return self

    def matchFor(self, other):
        soup = BeautifulSoup(other)
        if self.targetSubmitLabel:
            submitLabelMatch = self.matchSubmitLabel(soup)
            if not submitLabelMatch.successful:
                return submitLabelMatch
        return FormMatch()

    def matchSubmitLabel(self,otherSoup):
        submit = otherSoup.find('input',type='submit')
        match = FormMatch()
        if submit is None:
            return match.missingSubmit()
        elif not submit['value'] == self.targetSubmitLabel:
            return match.wrongSubmitLabel(self.targetSubmitLabel,submit['value'])
        return match



class FormMatch(object):
    successful = True
    _msg = 'Successful Form match.'

    def __str__(self):
        return self._msg

    def missingSubmit(self):
        self.successful = False
        self._msg = 'No submit element.'
        return self

    def wrongSubmitLabel(self, target, actual):
        self.successful = False
        tmp = 'Submit input element value "{0}", expected "{1}".'
        self._msg = tmp.format(actual, target)
        return self

