#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mosql.util import star
from mosql.json import dumps

from person import Person
Person.dump_sql = True
from detail import Detail
Detail.dump_sql = True
#Detail.dry_run = True

print dumps(Detail.where(person_id='mosky'))

import sys; sys.exit()

print Person.delete({'person_id': 'tina'}, returning=star)
print Person.insert({'person_id': 'tina'})
print Person.update({'person_id': 'tina'}, {'person_id': 'tina'}, returning=star)

import sys; sys.exit()

d = Detail.where(person_id='andy2', key='email')
print d
d.add(val='andy2@hi.com')
d.save()


Person.insert({'person_id': 'dara'})


d = Detail.new(person_id='dara', key='email')
d.add(val='dara@gmail.com')
d.add(val='dara@ymail.com')
d.save()
print d

d.person_id = 'andy'
d.save()
print d

d.clear()
d.save()
print d

