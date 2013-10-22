# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.sites.models import Site
from django.template import Variable, TemplateSyntaxError, VariableDoesNotExist

def get_metas(extra={}):
    """
    Renvoi les métas du site courant
    
    Les métas concernant le site courant se base sur les données enregistrées dans son 
    entrée du modèle `django.contrib.sites.models.Site`. Modifiables dans 
    "Administration de Django > Sites > Sites".
    
    Par défaut, les métas sont les suivants :
    
    * name: Nom du site enregistré dans l'entrée du site;
    * domain: le nom de domaine enregistré dans l'entrée du site;
    * web_url: URL de base du site à partir de son nom de domaine "domain". Aucun ajout 
      de slash de fin sur l'URL, si il y'en a une elle proviendra du nom de domaine dans 
      l'entrée du site;
    * medias_url: URL des médias tel qu'il a été configuré dans les settings Django 
      de l'application du site;
    * STATIC_URL: URL des fichiers statiques tel qu'il a été configuré dans les 
      settings Django de l'application du site;
    
    :type extra: dict
    :param extra: (optional) Dictionnaire de métas supplémentaires à ajouter au 
                  dictionnaire de métas standard.
    
    :rtype: dict
    :return: Dictionnaire contenant les métas du site courant
    """
    site_current = Site.objects.get_current()
    res = {
        'name': site_current.name,
        'domain': site_current.domain,
        'web_url': 'http://%s' % site_current.domain,
        'medias_url': settings.MEDIA_URL,
        'STATIC_URL': getattr(settings, 'STATIC_URL', ''),
    }
    res.update(extra)
    return res

def get_string_or_variable(value, context, safe=False, default=None, capture_none_value=True):
    """
    Résoud une variable dans le context de template donné.
    
    * Si la valeure donnée est entourée de double ou simple quotes, on la considère 
      comme une chaine de caractères à prendre telle quelle;
    * Sinon on tente de résoudre le nom trouvé dans le context;
    * Si rien de toute cela ne fonctionne renvoi une exception ou bien renvoi la valeur 
      par défaut si le mode silencieux (safe=True) est activé.
    
    :type value: string
    :param value: Valeur à résoudre. C'est soit directement une chaîne de caractères, 
                  soit un nom de variable à résoudre dans le context du template.
    
    :type context: object `django.template.RequestContext`
    :param context: Objet du contexte du template en cours ou sera recherché la valeur 
                    de la variable si ce n'est pas un simple string.
    
    :type safe: bool
    :param safe: (optional) Indique que l'échec pour retrouver le contenu de la variable 
                 doit être silencieux. Si activé, la valeur par défaut de ``default`` 
                 est renvoyée. False par défaut, l'échec remonte une exception 
                 `django.template.TemplateSyntaxError`.
    
    :type default: any
    :param default: (optional) Valeur par défaut renvoyée en cas d'échec pour retrouver 
                    la variable et si le mode silencieux est activé. Par défaut la 
                    valeur est ``None``.
    
    :type capture_none_value: bool
    :param capture_none_value: (optional) Indique si l'on doit capturer une variable du 
                               nom de "None" directement comme un ``None`` sans tenter de 
                               la résoudre comme un nom de variable. Dans ce cas, "None" 
                               deviendra un nom réservé pour le templatetag en cours. Si 
                               cette argument vaut ``False``, la méthode essayera de 
                               résoudre "None" comme un nom de variable dans le contexte. 
                               Par défaut cette option est activé (``True``).
    
    :rtype: any
    :return: La valeur de la variable si retrouvée, sinon la valeur par défaut.
    """
    # Capture du nom de variable "None" directement comme un ``None``
    if capture_none_value and value == "None":
        return None
    
    if value != None:
        # Ne résoud pas les chaînes de texte (toujours encerclés par des simples ou 
        # doubles quotes)
        if not(value[0] == value[-1] and value[0] in ('"', "'")):
            # Tente de résoudre le nom de variable dans le context donné
            try:
                value = Variable(value).resolve(context)
            except VariableDoesNotExist:
                # Échec qui remonte une exception de template
                if not safe:
                    raise TemplateSyntaxError("Unable to resolve '%s'" % value)
                # Échec silencieux qui renvoi la valeur par défaut sans lever d'exception
                else:
                    return default
        # Chaîne de texte dont on retire les quotes d'encerclement de la valeur
        else:
            value = value[1:-1]
    
    return value

def startswith_in_list(src, items):
    """
    Comparaison de type "startswith" avec une liste de 'match' possibles
    """
    for k in items:
        if src.startswith(k):
            return k
    return False

def endswith_in_list(src, items):
    """
    Comparaison de type "endswith" avec une liste de 'match' possibles
    """
    for k in items:
        if src.endswith(k):
            return k
    return False
