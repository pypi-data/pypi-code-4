from algoliasearch import algoliasearch
# -*- coding: utf-8 -*-
import pprint
import json
import time
import datetime

client = algoliasearch.Client("NUO9D6YJZA", '14400fd2786ae8771a1e520d1d635bd6')
print client.copyIndex("contacts", "contacts2")
print client.moveIndex("contacts2", "contacts3")
#print client.getLogs(0, 100)
