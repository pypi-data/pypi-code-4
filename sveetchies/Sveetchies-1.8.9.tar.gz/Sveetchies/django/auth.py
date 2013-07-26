# -*- coding: utf-8 -*-
"""
Utilitaire(s) lié(s) aux comptes utilisateurs
"""
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group

def get_user_queryset_from_perm(model_object, codename, filter_kwargs={}, order_args=[]):
    """
    Recherche des utilisateurs d'après une permission (assignée directement ou via 
    un groupe) qu'ils doivent posséder
    
    Ceci fonctionne aussi bien avec les utilisateurs qui ont la permission voulue aussi 
    bien directement sur leur compte que via un groupe de permissions.

    :type model_object: object `django.db.models.Model`
    :param model_object: Le modèle de données auquel appartient la permission recherchée.

    :type codename: string
    :param codename: Nom clé de la permission (ex: ``auth.change_user``).

    :type filter_kwargs: dict
    :param filter_kwargs: (optional) Arguments nommés à ajouter à la requête de séléction 
                          des utilisateurs (pour ajouter des conditions supplémentaires). 
                          Vide par défaut.

    :type order_args: list
    :param order_args: (optional) Arguments pour ordonner le queryset construit.

    :rtype: object `django.db.models.query.QuerySet`
    :return: Queryset contenant les objets des utilisateurs qui ont la permission 
             recherchée.
    """
    # Objet de la permission d'après le contenttypes du modèle dont elle dépend 
    # ainsi que son codename
    receive_permission = Permission.objects.get(content_type=ContentType.objects.get_for_model(model_object), codename=codename) 
    # Liste des groupes qui ont la permission recherchée
    receive_groups = Group.objects.filter(permissions=receive_permission)
    # Liste des utilisateurs qui ont la permission directement
    queryset = list(receive_permission.user_set.filter(**filter_kwargs).order_by(*order_args))
    # Liste des utilisateurs qui ont la permission via un groupe, sans doublons
    for item in receive_groups:
        queryset += list(item.user_set.filter(**filter_kwargs).exclude(id__in=[foo.id for foo in queryset]).order_by(*order_args))
    
    return queryset