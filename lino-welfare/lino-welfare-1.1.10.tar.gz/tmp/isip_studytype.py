# -*- coding: UTF-8 -*-
# all objects() from table isip_studytype:
loader.save(create_isip_studytype(1,[u'School', u'\xc9cole', u'Schule', u'']))
loader.save(create_isip_studytype(2,[u'Special school', u'\xc9cole sp\xe9ciale', u'Sonderschule', u'']))
loader.save(create_isip_studytype(3,[u'Schooling', u'Formation', u'Ausbildung', u'']))
loader.save(create_isip_studytype(4,[u'Apprenticeship', u'Apprentissage', u'Lehre', u'']))
loader.save(create_isip_studytype(5,[u'Highschool', u'\xc9cole sup\xe9rieure', u'Hochschule', u'']))
loader.save(create_isip_studytype(6,[u'University', u'Universit\xe9', u'Universit\xe4t', u'']))
loader.save(create_isip_studytype(7,[u'Part-time study', u'Cours \xe0 temps partiel', u'Teilzeitunterricht', u'']))
loader.save(create_isip_studytype(8,[u'Remote study', u'Cours \xe0 distance', u'Fernkurs', u'']))

loader.flush_deferred_objects()
