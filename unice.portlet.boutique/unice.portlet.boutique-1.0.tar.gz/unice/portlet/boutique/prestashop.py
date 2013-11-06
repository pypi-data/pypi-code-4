#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import urllib2
import xml.etree.ElementTree as XML
import re

class Prestashop:

    def __init__(self, serveur, dossier, cle):
        self.serveur = serveur
        self.dossier = dossier
        self.cle = cle

        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.serveur, self.cle, '')
        handler = urllib2.HTTPBasicAuthHandler(password_mgr)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)

    def requete(self, params, display, xpath):
        url = '%s/%s/api/%s?display=[%s]' % (self.serveur, self.dossier, '/'.join(params), ','.join(display))
        #print url
        f = urllib2.urlopen(url)
        return XML.fromstring(f.read()).findall(xpath)

    def produits(self):
        display = ['id', 'name', 'description', 'price', 'id_default_image', 'active']
        nodes = self.requete(['products'], display, './products/product')
        items = []
        for child in nodes:
            item = {}
            for key in display:
                keyNode = child.find(key)
                item[key] = keyNode.text if len(keyNode) == 0 else keyNode[0].text

                if key == 'id_default_image':
                    item['image'] = '%s/%s/img/p/%s/%s-thickbox_default.jpg' % (self.serveur, self.dossier, '/'.join(list(item[key])), item[key])

                if key == 'description':
                    item['desc'] = re.sub('<[^<]+?>', '', item['description']) if item['description'] else None

            items.append(item)
        return items


"""serveur = 'http://boutique-uns.com'
dossier = 'uns'
cle = '8MMGXQX2WCG10DU7KAXZ1LCHPAFV9YO6'

prestashop = Prestashop(serveur, dossier, cle)
pp.pprint(prestashop.produits())"""
