# -*- coding: utf8 -*-
class Hanzi(object):
    character = u''
    pinyin = u''
    readings = set()

    def __init__(self, character=None, readings=set()):
        super(Hanzi, self).__init__()
        self.character = character
        self.readings = readings

    def __str__(self):
        return self.character or 'None'

    def __unicode__(self):
        return self.character

    def __repr__(self):
        return self.character

    @property
    def hsk_level(self):
        hsk_level = 6  # assume highest level
        for reading in self.readings:
            if reading.hsk_level < hsk_level:
                hsk_level = reading.hsk_level
        return hsk_level

    @hsk_level.setter
    def hsk_level(self, value):
        self._hsk_level = value

class Reading(object):
    pinyin = u''
    meanings = set()
    hsk_level = None

    def __init__(self, pinyin='', meanings=set()):
        super(Hanzi.Reading, self).__init__()
        self.pinyin = pinyin
        self.meanings = meanings

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.pinyin

class Word(object):
    characters = u''
    readings = set()

    def __init__(self, characters):
        super(Word, self).__init__()
        self.characters = characters

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return self.characters

    @property
    def hsk_level(self):
        hsk_level = 6  # assume highest level
        for reading in self.readings():
            if reading.hsk_level < hsk_level:
                hsk_level = reading.hsk_level

        return hsk_level


