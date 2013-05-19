# -*- coding: utf-8 -*- 
import DictionaryServices
import os

import defaults as d

def get_text_definition(word):
  return DictionaryServices.DCSCopyTextDefinition(None, word, (0,len(word)))

def definition_using_dictionary(dict_path, word):
  current_dicts = d.SwapUserDictPreferences([dict_path])
  definition = get_text_definition(word)
  d.SwapUserDictPreferences(current_dicts)
  return definition

def list_dictionaries():
  return os.listdir('/Library/Dictionaries/')

def parse_def_output(definition):
  '''Take definition and parse it into Python dictionary containing the
  part-of-speech, definition, and pronunciation of a word'''
  pass

def print_dictionaries():
  for d in list_dictionaries():
    print d.split('.')[0]

def dictionary(word):
  return definition_using_dictionary(
      "/Library/Dictionaries/%s" % (list_dictionaries()[4]),
      word
  )


def thesaurus(word):
  return definition_using_dictionary(
      "/Library/Dictionaries/%s" % (list_dictionaries()[5]),
      word
  )

