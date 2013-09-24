# -*- coding: UTF-8 -*-
# all objects() from table countries_country:
loader.save(create_countries_country([u'Estonia', u'Estonie', u'Estland', u'Estland'],u'EE',u'',u'',u'136'))
loader.save(create_countries_country([u'Belgium', u'Belgique', u'Belgien', u'Belgie'],u'BE',u'B',u'',u'150'))
loader.save(create_countries_country([u'Germany', u'Allemagne', u'Deutschland', u'Duitsland'],u'DE',u'D',u'',u'173'))
loader.save(create_countries_country([u'France', u'France', u'Frankreich', u'Frankrijk'],u'FR',u'F',u'',u'111'))
loader.save(create_countries_country([u'Netherlands', u'Pays-Bas', u'Niederlande', u'Nederlande'],u'NL',u'',u'',u'129'))
loader.save(create_countries_country([u'Maroc', u'Maroc', u'Marokko', u'Marocco'],u'MA',u'',u'',u'354'))
loader.save(create_countries_country([u'Russia', u'Russie', u'Russland', u'Rusland'],u'RU',u'',u'',u'145'))
loader.save(create_countries_country([u'Congo (Democratic Republic)', u'Congo (R\xe9publique D\xe9mocratique)', u'Kongo (Demokratische Republik)', u'Congo (Democratische Republiek)'],u'CD',u'',u'',u''))

loader.flush_deferred_objects()
