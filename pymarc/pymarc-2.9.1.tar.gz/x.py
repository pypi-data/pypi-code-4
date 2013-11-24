#!/usr/bin/env python

from pymarc import Record, Field, MARCReader

r1 = Record(force_utf8=True)

a = '0' * 9994
f = Field('100', "##")
f.add_subfield('a', a)
r1.add_ordered_field(f)
r1.add_ordered_field(f)

marc21 = r1.as_marc()
r2 = MARCReader(marc21).next()

 
 
