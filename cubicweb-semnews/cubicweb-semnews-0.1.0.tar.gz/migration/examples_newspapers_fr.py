# -*- coding: utf-8 -*-

list_rss = ((u'Les Echos - Politique', u'http://syndication.lesechos.fr/rss/rss_politique.xml', u'fr'),
            ##(u'Le Parisien - Politique', u'http://www.leparisien.fr/politique/rss.xml', u'fr'),
            (u"L'Express - Politique", u'http://www.lexpress.fr/rss/politique.xml', u'fr'),
            (u"Le Figaro - Politique", u'http://www.lefigaro.fr/rss/figaro_politique.xml', u'fr'),
            (u"Le Monde - Politique", u'http://www.lemonde.fr/rss/tag/politique.xml', u'fr'),
            (u"Le Nouvel Observateur - Politique", u'http://rss.nouvelobs.com/c/32262/fe.ed/tempsreel.nouvelobs.com/politique/rss.xml', u'fr'),
            (u"Liberation - Politique", u'http://rss.liberation.fr/rss/11/', u'fr'),
            (u"RMC - Politique", u'http://rss.feedsportal.com/c/603/f/502288/index.rss', u'fr'),
            (u'Politis', u'http://www.politis.fr/spip.php?page=backend', u'fr'),
            (u'20 Minutes - La une', u'http://www.20min.ch/rss/rss.tmpl?type=channel&get=6', u'fr'),
            (u'Rue 89 - Politique', u'http://rue89.feedsportal.com/c/33822/f/608955/index.rss', u'fr'),
            ## (u'France 2 - ', u'', u'fr'),
            (u'Public Senat', u'http://www.publicsenat.fr/lcp/politique/flux/accueil', u'fr'),
            (u'France Info - Actu', u'http://www.franceinfo.fr/rss/tag/1', u'fr'),
            )


for (name, url, lang) in list_rss:
    session.create_entity('CWSource', name=name, type=u'datafeed',
                          parser=u'rss-parser', lang=lang, url=url,
                          config=u'synchronization-interval=120min')
