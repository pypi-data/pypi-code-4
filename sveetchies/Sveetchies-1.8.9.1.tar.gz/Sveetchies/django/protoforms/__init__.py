# -*- coding: utf-8 -*-
"""
Extra add-ons pour les modèles et leurs formulaires

Cette application permet de gérer des formulaires de bout en ligne automatiquement à 
partir des modèles.

Le système s'implémente selon plusieurs étapes :

* Créer un modèle héritant du modèle abstrait ``BaseContainer``;
* Spécifier dans le manager du modèle, un schéma qui définira tout ce qui concerne la 
  mise en forme dans le ou les formulaires;
* Créer l'entrée du formulaire dans "urls.py", ce peut être une simple vue ou un objet 
  "FormWizard";
* Créer la vue du formulaire ou son controleur "FormWizard";
* Créer le ou les objet de formulaire héritant de ``BaseContainerForm`` ou 
  ``BaseContainerModelForm``. Sa définition des champs est automatique, il n'y a que 
  la méthode ``save()`` qui est requise et l'attribut ``Meta``;
* Créer les templates du formulaire, les templates sont en fait génériques, il suffit de 
  recopier ceux d'un formulaire du même type (Form ou FormWizard) et le customiser si besoin;
* Créer le template de mail de type ``xxx-to-supervisor`` pour les superviseurs, où 
  ``xxx`` est le nom exact du modèle;
"""
from django.conf import settings
from django.contrib.messages import constants as message_constants

__version__ = '0.1.5'

#
# Définitions par défaut des settings manquants
#

# Template de nom clé interne d'une relation d'extension dans les modèles
PROTO_EXTENDED_VALUE_FIELD_KEY = getattr(settings, 'PROTO_EXTENDED_VALUE_FIELD_KEY', "proto_extension_%s")
# Formats de date à la francaise utilisés pour le champ FRZipcode
PROTO_DATE_FIELD_FORMATS = getattr(settings, 'PROTO_DATE_FIELD_FORMATS', (
    '%d-%m-%Y',
    '%d/%m/%Y',
    '%d/%m/%y'
))
# Niveau supplémentaire aux messages de succès spécifiques à Protoforms, "None" pour 
# désactiver leur utilisation
PROTO_MESSAGE_FORM_SUCCESS = getattr(settings, 'PROTO_MESSAGE_FORM_SUCCESS', message_constants.SUCCESS+1)
# Chemin du template utilisé pour afficher un champ de formulaire
PROTO_FIELD_TEMPLATE = getattr(settings, 'PROTO_FIELD_TEMPLATE', "protoforms/cf_field.html")
# Types d'éléments disponibles dans les listes de séléction
PROTO_SELECTION_KINDS = getattr(settings, 'PROTO_SELECTION_KINDS', (
    ('sample', u'Exemple'),
))
# Longueur maximum (en BDD) des clés d'éléments de liste de séléction
PROTO_SELECTION_KEY_LENGTH = getattr(settings, 'PROTO_SELECTION_KEY_LENGTH', 50)
# Quelques listes de labels utiles
PROTO_CIVILITY_LABELS = (
    ('mister', 'Monsieur'),
    ('madam', 'Madame'),
    ('miss', 'Mademoiselle'),
)
PROTO_BOOLEAN_YES_OR_NO_CHOICE = (
    (True, 'Oui'),
    (False, 'Non'),
)
