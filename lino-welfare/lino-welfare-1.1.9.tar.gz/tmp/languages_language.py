# -*- coding: UTF-8 -*-
# all objects() from table languages_language:
loader.save(create_languages_language([u'Dutch', u'N\xe9erlandais', u'Niederl\xe4ndisch', u'Nederlands'],u'dut',u''))
loader.save(create_languages_language([u'English', u'Anglais', u'Englisch', u'Engels'],u'eng',u''))
loader.save(create_languages_language([u'Estonian', u'Estonien', u'Estnisch', u''],u'est',u''))
loader.save(create_languages_language([u'French', u'Fran\xe7ais', u'Franz\xf6sisch', u'Frans'],u'fre',u''))
loader.save(create_languages_language([u'German', u'Allemand', u'Deutsch', u'Duits'],u'ger',u''))

loader.flush_deferred_objects()
