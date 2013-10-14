# -*- coding: utf-8 -*-

from zope.interface import implements
from OFS.SimpleItem import SimpleItem

from interfaces import IJalonIntracursus
from jalon.intracursus import contentMessageFactory as _

import json
import urllib
import urllib2


class JalonIntracursus(SimpleItem):

    implements(IJalonIntracursus)
    _urlConnexion = ""
    _loginConnexion = ""
    _passwordConnexion = ""

    def __init__(self, *args, **kwargs):
        super(JalonIntracursus, self).__init__(*args, **kwargs)

    #-------------------------------------#
    # Gestion des variables du connecteur #
    #-------------------------------------#
    def getUrlConnexion(self):
        return self._urlConnexion

    def setUrlConnexion(self, urlConnexion):
        self._urlConnexion = urlConnexion

    def getLoginConnexion(self):
        return self._loginConnexion

    def setLoginConnexion(self, loginConnexion):
        self._loginConnexion = loginConnexion

    def getPasswordConnexion(self):
        return self._passwordConnexion

    def setPasswordConnexion(self, passwordConnexion):
        self._passwordConnexion = passwordConnexion

    def getVariablesIntracursus(self):
        return {"urlConnexion":      self._urlConnexion,
                "loginConnexion":    self._loginConnexion,
                "passwordConnexion": self._passwordConnexion
                }

    def setVariablesIntracursus(self, variablesIntracursus):
        # s'il n'y a aucun type renseigné ou alors aucune url de connexion
        if (variablesIntracursus["urlConnexion"] == '' or variablesIntracursus["loginConnexion"] == '' or variablesIntracursus["passwordConnexion"] == ""):
            return 0
        self._urlConnexion = variablesIntracursus["urlConnexion"]
        self._loginConnexion = variablesIntracursus["loginConnexion"]
        self._passwordConnexion = variablesIntracursus["passwordConnexion"]
        return 1

    #-----------------------#
    # Fonctions Intracursus #
    #-----------------------#

    def verifierConnexionIntracursus(self):
        connexion = self.verifIdentifiantServer()
        if (connexion["status"] == "REUSSITE"):
            return 3
        else:
            return 2

    # appellerServer : fonction d'appel generique des jobs du chemin du server d'intracursus
    def appellerServer(self, param):
        data = urllib.urlencode(param)
        #print "requete Intracursus envoyee : %s" '\n' % data
        #print "url : %s?%s" '\n' % (self._urlConnexion, data)
        try:
            req = urllib2.Request(self._urlConnexion, data)
            handle = urllib2.urlopen(req, timeout=10)
            rep = handle.read()

        except IOError, e:
            rep = '{"status":"ERROR"'
            #--- Erreur HTTP ---
            if hasattr(e, 'reason'):
                print 'URLError ', e.reason
                # URLError peut survenir en cas de "Time out" Cela peut aussi bien provenir du client (modifier alors la valeur dans urlopen ci-dessus) que du serveur appelé.
                rep = '%s,"type":"URLError","message":"%s"}' % (rep, e.reason)
            elif hasattr(e, 'code'):
                #-- HTTPError --
                # L'erreur HTTP 450 survient souvent lors de parenthese mal fermées detectées par le server
                rep = '%s,"type":"HTTPError","message":"%s","error_code":"%s"}' % (rep, json.string_for_json(e.read()), e.code)
        rep = rep.decode("utf-8")
        return rep.encode("utf-8")

    #fonction qui permet de verifier si le login et le mot de passe son correct
    def verifIdentifiantServer(self):
        param = {"action": "authentification",
                 "login":  self._loginConnexion,
                 "password": self._passwordConnexion}
        retour = self.appellerServer(param)
        retour = json.loads(retour)
        return retour

    def verifListSeanceIntracursus(self, codeMatiere):
        listeSeance = self.listerSeanceServer(codeMatiere)
        if (listeSeance["status"] == "REUSSITE"):
            return 4
        else:
            return 5

    def listerSeanceServer(self, codeMatiere):
        param = {"action": "ListerSeance",
                 "codematiere": codeMatiere}
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour

    def verifCreationSeanceIntracursus(self, codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient):
        creerSeance = self.creationSeanceServer(codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient)
        if (creerSeance["status"] == "REUSSITE"):
            return 7
        else:
            return 8

    #fonction qui permet de donner les informations a infracursus pour la création de séance
    def creationSeanceServer(self, codeMatiere, annee, periode, publiable, intitule, typeseance, dateseance, heureseance, dureeseance, avecnote, coefficient):
        param = {"action": "CreationSeance",
                 "codematiere": codeMatiere,
                 "annee": annee,
                 "periode": periode,
                 "publiable": publiable,
                 "intitule": intitule,
                 "typeseance": typeseance,
                 "dateseance": dateseance,
                 "heureseance": heureseance,
                 "dureeseance": dureeseance,
                 "avecnote": avecnote,
                 "coefficient": coefficient
                }  
        jsonRetour=json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour 

    def verifCreationPresenceIntracursus(self, numero, nom, prenom, idseance, statut, note, appreciation, datepresence):
        creerPresence = self.creationPresenceServer(numero, nom, prenom, idseance, statut, note, appreciation, datepresence)
        if (creerPresence["status"] == "REUSSITE"):
            return 9
        else:
            return 10

    #fonction qui permet de donner les informations a infracursus pour la création de presence
    def creationPresenceServer(self, numero, nom, prenom, idseance, statut, note, appreciation, datepresence):
        param = {"action": "CreationPresence",
                 "numero": numero,
                 "nom": nom,
                 "prenom": prenom,
                 "idseance": idseance,
                 "statut": statut,
                 "note": note,
                 "appreciation": appreciation,
                 "datepresence": datepresence}
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour

    def verifNbreSeanceIntracursus(self, codeMatiere):
        nbreSeance = self.getNbSeances(codeMatiere)
        if (nbreSeance["status"] == "REUSSITE"):
            return 11
        else:
            return 12

    def getNbSeances(self, codeMatiere):
        param = {"action":      "NombreSeance",
                 "codematiere": codeMatiere}
        return json.loads(self.appellerServer(param))


    def verifListeEtudiantSeanceIntracursus(self, codeseance):
        listeEtudiantSeance = self.listeEtudiantSeanceServer(codeseance)
        if (listeEtudiantSeance["status"] == "REUSSITE"):
            return 15
        else:
            return 16

    def listeEtudiantSeanceServer(self, codeseance):
        param = {"action": "ListerEtudiant",
                 "codeseance": codeseance}
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour



    def verifPublicationSeanceIntracursus(self, codematiere, intitule, publiable):
        publicationSeance = self.publicationSeance(codematiere, intitule, publiable)
        if (publicationSeance["status"] == "REUSSITE"):
            return 13
        else:
            return 14

    def publicationSeance(self, codematiere, intitule, publiable):
        param = {"action": "PublicationSeance",
                 "codematiere": codematiere,
                 "intitule": intitule,
                 "publiable": publiable}
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour






    def verifModificationSeanceIntracursus(self, codeseance, intitule, typeseance, periode, dateseance, heureseance, dureeseance, avecnote, coefficient, publiable):
        modificationSeance = self.modificationSeance(codeseance, intitule, typeseance, periode, dateseance, heureseance, dureeseance, avecnote, coefficient, publiable)
        if (modificationSeance["status"] == "REUSSITE"):
            return 17
        else:
            return 18

    def modificationSeance(self, codeseance, intitule, typeseance, periode, dateseance, heureseance, dureeseance, avecnote, coefficient, publiable):
        param = {"action": "ModificationSeance",
                 "codeseance": codeseance,
                 "intitule": intitule,
                 "typeseance": typeseance,
                 "periode": periode,
                 "dateseance": dateseance,
                 "heureseance": heureseance,
                 "dureeseance": dureeseance,
                 "avecnote": avecnote,
                 "coefficient": coefficient,
                 "publiable": publiable}
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour




    def verifSuppressionSeanceIntracursus(self, codeseance):
        suppressionSeance = self.suppressionSeance(codeseance)
        if (suppressionSeance["status"] == "REUSSITE"):
            return 19
        else:
            return 20

    def suppressionSeance(self, codeseance):
        param = {"action": "SuppressionSeance",
                 "codeseance": codeseance
                 }
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour


    def verifInfoSeanceIntracursus(self, codeseance):
        informationSeance = self.informationSeance(codeseance)
        if (informationSeance["status"] == "REUSSITE"):
            return 21
        else:
            return 22

    def informationSeance(self, codeseance):
        param = {"action": "InfoSeance",
                 "codeseance": codeseance
                 }
        jsonRetour = json.loads(self.appellerServer(param))
        print jsonRetour
        return jsonRetour


    #-----------------------#
    # Fonctions utilitaires #
    #-----------------------#
    def traductions_fil(self, key):
        textes = {"intracursus": _(u"Intracursus"),
                  "configsite":  _(u"Configuration du site")}
        if key in textes:
            return textes[key]
        else:
            return key

    def test(self, condition, valeurVrai, valeurFaux):
        return valeurVrai if condition else valeurFaux

    def encodeUTF8(self, itemAEncoder):
        return [str(encoder).encode("utf-8") for encoder in itemAEncoder]
