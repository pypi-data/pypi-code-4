# -*- coding: UTF-8 -*-
# all objects() from table jobs_contracttype:
loader.save(create_jobs_contracttype(1,[u'social economy', u'\xe9conomie sociale', u'Sozial\xf6konomie', u''],u'appypdf',u'art60-7.odt',u'art60-7a',3))
loader.save(create_jobs_contracttype(2,[u'social economy - increased', u'\xe9conomie sociale - major\xe9', u'Sozial\xf6konomie - major\xe9', u''],u'appypdf',u'art60-7.odt',u'art60-7b',3))
loader.save(create_jobs_contracttype(3,[u'social economy with refund', u'avec remboursement', u'mit R\xfcckerstattung', u''],u'appypdf',u'art60-7.odt',u'art60-7c',3))
loader.save(create_jobs_contracttype(4,[u'social economy school', u'avec remboursement \xe9cole', u'mit R\xfcckerstattung Schule', u''],u'appypdf',u'art60-7.odt',u'art60-7d',3))
loader.save(create_jobs_contracttype(5,[u'town', u"ville d'Eupen", u'Stadt Eupen', u''],u'appypdf',u'art60-7.odt',u'art60-7e',3))

loader.flush_deferred_objects()
