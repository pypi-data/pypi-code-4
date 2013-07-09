# -*- coding: utf-8 -*-
# postcreate script. You could setup a workflow here for example

for login in (u'alf', u'syt', u'nico', u'jphc', u'ocy', u'auc', u'katia',
              u'graz', u'dede', u'juj', u'ludal', u'steph', u'arthur',
              u'david', u'joel', u'gaston', u'adim'):
    rql('INSERT CWUser E: E login %(login)s, E upassword %(login)s, E in_group G '
        'WHERE G name "users"', {'login' : login})
    rql('INSERT PaidByAccount P: P label %(label)s, P associated_to U WHERE U login %(login)s',
        {'label' : u"refund account - %s" % login, 'login': login})
    rql('INSERT PaidForAccount P: P label %(label)s', {'label' : u"charge account - %s" % login})


for label in (u'Logilab - CB Nicolas', u'Logilab - CB Alexandre', u'Logilab - CB Olivier',
              u'Logilab - Espèces'):
    rql('INSERT PaidByAccount P: P label %(label)s', {'label' : label})
