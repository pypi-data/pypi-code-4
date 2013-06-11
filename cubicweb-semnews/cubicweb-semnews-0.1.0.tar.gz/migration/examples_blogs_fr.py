# -*- coding: utf-8 -*-
# List of french political blogs

list_rss = (
    # http://c.asselin.free.fr/french/blogs_politiques.htm
    (u'Jean-Louis Borloo', u'http://borloo.hautetfort.com/index.rss', u'fr'),
    (u'Jean-François Copé', u'http://jeanfrancoiscope.fr/wordpress/feed/rss', u'fr'),
    (u'Xavier Darcos', u'http://desideesdabord.typepad.com/_/atom.xml', u'fr'),
    (u'Patrick Devedjian', u'http://www.blogdevedjian.com/index.rss', u'fr'),
    (u'Alain Juppé', u'http://www.al1jup.com/?feed=rss2', u'fr'),
    (u'Jean-Pierre Raffarin', u'http://www.carnetjpr.com/feed/', u'fr'),
    (u'Le Blog de Jean-Luc Mélenchon', u'http://www.jean-luc-melenchon.fr/feed/', u'fr'),
    (u'Variae', u'http://feeds.feedburner.com/Variae?format=xml', u'fr'),
    (u'Partageons mon avis', u'http://feeds.feedburner.com/PartageonsMonAvis?format=xml', u'fr'),
    (u'Sarkofrance', u'http://feeds.feedburner.com/Sarkofrance?format=xml', u'fr'),
    (u'Carnet de notes de Yann Savidan', u'http://feeds.feedburner.com/typepad/mLmu?format=xml', u'fr'),
    (u'Le Mal Pensant', u'http://www.lemalpensant.fr/feed/atom/', u'fr'),
    (u'A perdre la raison', u'http://perdre-la-raison.blogspot.fr/feeds/posts/default', u'fr'),
    (u'Intox2007.info', u'http://politeeks.info/?feed=rss2', u'fr'),
    (u'Les coulisses de Sarkofrance', u'http://sarkofrance.wordpress.com/feed/', u'fr'),
    (u'Le Kiosque aux Canards', u'http://www.lekiosqueauxcanards.com/rss-articles.xm', u'fr'),
    (u'François Desouche', u'http://www.fdesouche.com/feed', u'fr'),
    (u'Antenne-relais', u'http://antennerelais.canalblog.com/rss.xml', u'fr'),
    (u'Bah !', u'http://www.bahbycc.com/feeds/posts/default', u'fr'),
    (u'Lyonnitude(s)', u'http://feeds.feedburner.com/typepad/romainblachier/mon_weblog?format=xml', u'fr'),
    (u'MonPuteaux.com', u'http://feeds.feedburner.com/monputeaux?format=xml', u'fr'),
    # http://c.asselin.free.fr/french/blogs_politiques.htm
    (u'Didier HACQUART, Adjoint au Maire PS à Vitrolles ', u'http://didier-hacquart.over-blog.com/rss-articles.xml', u'fr'),
    (u'Nadine Jeanne, conseillère municpale PS de Puteaux', u'http://www.nadinejeanne.com/atom.xml', u'fr'),
    (u'Fabrice ROUSSEAU Conseiller du XVe Arrondissement de Paris - UMP', u'http://fabricerousseau15.hautetfort.com/index.rss', u'fr'),
    (u'Pierre Bédier, Député UMP et Président du Conseil Général des Yvelines', u'http://www.pierrebedier.net/?feed=rss2', u'fr'),
    (u'Frédéric Dutoit, député PCF de Marseille', u'http://www.dutoitfreeblog.com/blog_de_frederic_dutoit/atom.xml', u'fr'),
    (u"Alain Carignon, Ancien Ministre, Président de l'UMP Isère", u'http://alaincarignon.blogs.com/alaincarignon/atom.xml', u'fr'),
    # Institutions
    (u'Présidence de la République - Flux : Culture & Communication', u'http://www.elysee.fr/president/root/items/xml/rss_46.xml', u'fr'),
    (u'Présidence de la République - Flux : Etat & Institutions', u'http://www.elysee.fr/president/root/items/xml/rss_41.xml', u'fr'),
    (u'Présidence de la République - Flux : Industrie', u'http://www.elysee.fr/president/root/items/xml/rss_83.xml', u'fr'),
    (u'Assemblée Nationale - Publications parlementaires', u'http://www.assemblee-nationale.fr/rss/rss.xml', u'fr'),
    (u'Assemblée Nationale - Communiqués de la division de la presse', u'http://www.assemblee-nationale.fr/rss/rss_presse.xml', u'fr'),
    (u'Sénat - Derniers rapports', u'http://www.senat.fr/rss/rapports.xml', u'fr'),
    (u'Sénat - Derniers projets / propositions de loi et de résolution', u'http://www.senat.fr/rss/textes.xml', u'fr'),
    (u'Sénat - Derniers communiqués de presse', u'http://www.senat.fr/rss/presse.xml', u'fr'),
    (u'Gouvernement - Accueil', u'http://www.gouvernement.fr/accueil/rss', u'fr'),
    (u'Gouvernement - Premier Ministre', u'http://www.gouvernement.fr/premier-ministre/rss', u'fr'),
    (u'Gouvernement - Action', u'http://www.gouvernement.fr/gouvernement/rss', u'fr'),
    (u"Conseil d'Etat", u'http://www.conseil-etat.fr/fr/rapports-et-etudes.xml', u'fr'),
    (u"Conseil d'Etat - Communiqués", u'http://www.conseil-etat.fr/fr/communiques-de-presse.xml', u'fr'),
    (u'Conseil Constitutionnel', u'http://www.conseil-constitutionnel.fr/conseil-constitutionnel/root/items/xml/rss_2.xml', u'fr'),
            )


for (name, url, lang) in list_rss:
    session.create_entity('CWSource', name=name, type=u'datafeed',
                          parser=u'rss-parser', lang=lang, url=url,
                          config=u'synchronization-interval=120min')
