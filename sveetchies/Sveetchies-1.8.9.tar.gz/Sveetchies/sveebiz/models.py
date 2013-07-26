# -*- coding: utf-8 -*-
"""
Modèles de données

En fait de modèles de données, ce sont plutôt des modèles+controleurs, parfois même 
uniquement contrôleur (vu que la majorité des données proviennent du fichier de config 
utilisateur).
"""
from decimal import Decimal

class Coords(object):
    """
    Modèle des coordonnées disponibles dans la config
    """
    def __init__(self, config):
        """
        :type config: object `ConfigParser.SafeConfigParser`
        :param config: Options utilisateur
        """
        self.config = config
    
    def render(self):
        """
        :rtype: string
        :return: Liste d'éléments des coordonnées, chaque élément étant une "fausse" 
                 directive ReST.
        """
        coords = ''
        
        coords += self.get_author_render()
        coords += self.get_full_adress_render()
        if self.config.has_option('identity', 'phone_number'):
            coords += ':Téléphone: %s\n' % self.config.get('identity', 'phone_number')
        if self.config.has_option('identity', 'mobile_number'):
            coords += ':Portable: %s\n' % self.config.get('identity', 'mobile_number')
        
        return coords
    
    def get_author_render(self):
        """
        :rtype: string
        :return: Liste d'éléments d'itentité, chaque élément étant une "fausse" 
                 directive ReST.
        """
        author = []
        if self.config.has_option('identity', 'first_name'):
            author.append( self.config.get('identity', 'first_name') )
        if self.config.has_option('identity', 'last_name'):
            author.append( self.config.get('identity', 'last_name') )
        if self.config.has_option('identity', 'email'):
            author.append( "<%s>"%self.config.get('identity', 'email') )
        if len(author)>0:
            res = ':Auteur: %s\n' % ' '.join(author)
            return res
        return ''
    
    def get_full_adress_render(self):
        """
        :rtype: string
        :return: Liste d'éléments d'adresse, chaque élément étant une "fausse" 
                 directive ReST.
        """
        full_adress = []
        if self.config.has_option('identity', 'structure_name'):
            full_adress.append( self.config.get('identity', 'structure_name') )
        if self.config.has_option('identity', 'adress'):
            full_adress.append( self.config.get('identity', 'adress') )
        if self.config.has_option('identity', 'town'):
            full_adress.append( self.config.get('identity', 'town') )
        if self.config.has_option('identity', 'zipcode'):
            full_adress.append( self.config.get('identity', 'zipcode') )
        if len(full_adress)>0:
            res = ':Adresse: %s\n' % ', '.join(full_adress)
            return res
        return ''

class Delayer(object):
    """
    Modèle des délais
    
    Gère un délai fixe ou variables (à deux tranches maximum)
    """
    def __init__(self, config):
        """
        :type config: object `ConfigParser.SafeConfigParser`
        :param config: Options utilisateur
        """
        self.config = config
        self.count_min = 0
        self.count_max = 0
    
    def add(self, delay):
        """
        Ajoute un délai au compteur interne et renvoi le rendu du délai
        
        :type delay: string
        :param delay: Le délai à ajouter, un simple chiffre pour un délai fixe et deux 
                      chiffres séparés par un ``-`` pour un délai variable.
        
        :rtype: string
        :return: Rendu du délai
        """
        values = delay.split('-')
        if len(values)>0:
            self.count_min += Decimal(values[0])
            if len(values)>1:
                self.count_max += Decimal(values[1])
            else:
                self.count_max += Decimal(values[0])
            res = self.row_render(values)
            return res
            
        return ''
    
    def row_render(self, values):
        """
        Rendu d'une ligne de délai
        
        :type values: list
        :param values: Liste d'un ou deux chiffres (string) de délai. Un élément pour un 
                       délai fixe et deux éléments pour un délai variable (ex: "entre X 
                       et Y jours").
        
        :rtype: string
        :return: Texte de rendu du délai, en gras au format ReST.
        """
        plural = ''
        if len(values)>1:
            val_min = values[0]
            val_max = values[1]
            if Decimal(val_max)>1:
                plural = 's'
            return '**Estimation de %s à %s jour%s**\n' % (val_min, val_max, plural)
        else:
            val = values[0]
            if Decimal(val)>1:
                plural = 's'
            return '**Estimation de %s jour%s**\n' % (val, plural)
    
    def total(self, unit="jour.homme"):
        """
        Rendu du total de tout les délais additionnés
        
        Le rendu est différent si il y a au moins un délai variable, le délai total sera 
        aussi du type variable (ex: "entre X et Y jours").
        
        :type unit: string
        :param unit: (optional) Label de l'unité à afficher.
        
        :rtype: string
        :return: Texte de rendu du total des délais.
        """
        if self.count_min == self.count_max:
            return 'à %s %s'%(self.correct_decimal_repr(self.count_min), unit)
        else:
            return 'de %s à %s %s'%(self.correct_decimal_repr(self.count_min), self.correct_decimal_repr(self.count_max), unit)
    
    def correct_decimal_repr(self, value):
        """
        Correction de la représentation des chiffres de délai pour avoir des nombres 
        décimaux sans zéros significatifs et utiliser la virgule comme séparateur entre 
        la partie entière et décimale.
        
        :type value: int or float or Decimal
        :param value: Chiffre du délai
        
        :rtype: string
        :return: Représentation du délai
        """
        if str(value).find('.'):
            foo = str(value).split('.')
            if len(foo)>1 and int(foo[1])==0:
                del foo[1]
            value = ','.join(foo)
        return value
        
class Costs(object):
    """
    Modèle des coûts
    """
    def __init__(self, config, delayer):
        """
        :type config: object `ConfigParser.SafeConfigParser`
        :param config: Options utilisateur.
        
        :type delayer: object `Delayer`
        :param delayer: Objet du registre des délais.
        """
        self.config = config
        self.delayer = delayer
    
    def get_fees(self, fee_type=None):
        """
        :type fee_type: string
        :param fee_type: Nom clé d'un type spécifique de coût à traiter, peut être 
                         'correction', 'evolution' ou 'base'. Ce dernier est équivalent 
                         à None, qui est la valeur par défaut).
        
        :rtype: string
        :return: Rendu du coût séléctionné
        
        Les types de coûts sont :
        
        * 'standard' ou None : Tarif de base;
        * 'corrective' : Tarif de maintenance corrective;
        * 'evolution' : Tarif de maintenance évolutive;
        """
        output = []
        if fee_type == 'corrective':
            fee = self.config.get('fees', 'corrective')
        elif fee_type == 'evolution':
            fee = self.config.get('fees', 'evolution')
        else:
            fee = self.config.get('fees', 'base')
        
        output.append("La charge de travail est estimée %s au tarif journalier de %s Euros HT." % (self.delayer.total(), fee))
        output.append("Cette estimation ne tient pas compte des possibles fonctionnalités non validés ou en attente.")
        if fee_type != 'corrective':
            output.append("Le tarif journalier pour la maintenance corrective est estimée à 140 Euros HT.")
            if fee_type != 'evolution':
                output.append("Le tarif journalier pour la maintenance évolutive est estimée à 150 Euros HT.")
        output.append("La facturation se fera par un compte rendu d'activités (rapport des jours travaillés) fourni par le prestataire au client à chaque fin de mois et à la fin du délai prévu par le contrat.")
        
        return '\n\n'.join(output)
        
class Softwares(object):
    """
    Modèle des briques logicielles séléctionnées
    """
    def __init__(self, config):
        """
        :type config: object `ConfigParser.SafeConfigParser`
        :param config: Options utilisateur
        """
        self.config = config
    
    def get_softs_render(self, softs=[]):
        """
        Rendu ReST pour les logiciels séléctionnés
        
        :type softs: list
        :param softs: Liste de noms clés de logiciels, les noms clés doivent correspondre 
                      à ce qui est référencé dans le fichier de config utilisateur.
        
        :rtype: string
        :return: Rendu de la liste des logiciels
        """
        if len(softs)==0:
            return ''
        
        output = []
        for item in softs:
            if self.config.has_option('software', item):
                output.append('* %s;' % self.config.get('software', item))
        
        return ('\n'.join(output))+'\n'
