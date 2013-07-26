# -*- coding: utf-8 -*-
from django.template import RequestContext, Context, loader
from django.template.defaultfilters import slugify
from django.utils.http import urlquote

class SearchManager:
    """
    Générateur de recherche avancée.
    
    Gère la recherche textuelle, les filtres de tris et d'ordre sur une 
    requete grace à des schémas de recherche. Ces schémas contiennent les 
    possibilités de recherche, le nécessaire pour construire le html des 
    formulaires ainsi que les "lookup" pour la DB API de Django qui va faire 
    la requête BDD.
    
    Le principe :
    
    On instancie ce manager, fait la recherche texte, filtre puis ordonne le queryset. 
    On construit ensuite le HTML du formulaire de recherche, puis les arguments à ajouter 
    aux urls de navigation dans la pagination des résultats.
    
    Le manager va lui meme récupérer les motifs de recherches dans le request 
    qu'on lui a passé en l'instanciant.
    """
    def __init__(self, request):
        """
        :type request: object `django.http.HttpRequest`
        :param request: Requête HTTP auquel se "greffer"
        """
        self.request = request
        self.url_args = []
        # Eléments de la requete à former
        self.lookup_query = {}
        self.lookup_order = []
        self.lookup_extra = {}
        # Historique des éléments utilisés
        self.values_searchtext = {}
        self.values_filter = {}
        self.values_order = {}
        self.values_extra = {}
        
        # On récupère les arguments dans POST et GET
        self.requested_keys = {}
        for b in request.POST.copy().items():
            self.requested_keys[ b[0] ] = b[1]
        for g in request.GET.copy().items():
            self.requested_keys[ g[0] ] = g[1]
    
    
    def make_searchtext(self, search_schema, global_prefix=''):
        """
        Construit les éléments de la requête pour rechercher du texte
        
        Un filtre spécial et unique associé au champs texte permet de 
        choisir sur quel critère se fera la recherche textuelle
        
        Le schéma est sous le format suivant : ::
        
            search_schema = {
                'text_namefield1' : 'lookup_key',
                'text_namefield2' : (
                    'filter_namefield',
                    {
                        'pattern1' : ('pattern1_label', 'lookup_key'),
                        'pattern2' : ('pattern2_label', custom_function),
                        ...
                    }
                )
                ...
            }
        
        :type search_schema: dict
        :param search_schema: Un dictionnaire python contenant les relations 
                              "mots-clés->model" et leurs options.
        
        :type global_prefix: string
        :param global_prefix: (optional) Un préfixe a rajouter sur tout les éléments 
                              de la requete (utile pour les relations de model). N'y 
                              incluez pas de caractère de séparation de préfixe.
                              Vide par défaut.
        """
        
        # Séléction des relations seulement si on a un prefix de relation qui
        # implique donc un modèle avec une relation
        if global_prefix:
            global_prefix = global_prefix+'__'
            self.lookup_query['select_related'] = False
        
        # Mise en forme du lookup selon le schéma donné
        for text_namefield, opts in search_schema.items():
            # Init à zéro pour faire plaisir au template
            self.values_searchtext[text_namefield] = False
            # Si le motif est dans le request et qu'il n'est pas vide
            if self.requested_keys.has_key(text_namefield) and self.requested_keys[text_namefield]:
                # Si la valeure de la clé est un String, on passe directement 
                # par la méthode simple de recherche
                if isinstance(opts, basestring):
                    self.lookup_query[opts] = self.requested_keys[text_namefield][:50].strip()
                    self.values_searchtext[text_namefield] = self.requested_keys[text_namefield][:50].strip()
                    
                # La valeure est un tuple avec plusieurs possibilités de 
                # recherches selon un filtre
                else:
                    filter_namefield = opts[0]
                    # Vérifie chaque possibilité de recherche
                    for filter_pattern, attr in opts[1].items():
                        # Si la possibilité de recherche est séléctionnée
                        if self.requested_keys.has_key(filter_namefield) and self.requested_keys[filter_namefield]:
                            pattern = self.requested_keys[filter_namefield]
                            if pattern == filter_pattern:
                                # Lookup direct si la valeur de attr[1] est un String
                                if isinstance(attr[1], str):
                                    self.lookup_query[attr[1]] = self.requested_keys[text_namefield][:50].strip()
                                    # Historique
                                    self.values_searchtext[filter_namefield] = pattern
                                    self.values_searchtext[text_namefield] = self.requested_keys[text_namefield][:50].strip()
                                # Si la valeur de attr[1] n'est pas un String, 
                                # il doit forcément être une fonction qui 
                                # compilera des données à l'avance pour faire 
                                # une recherche customisée
                                else:
                                    self.lookup_query.update( attr[1](pattern, self.requested_keys[text_namefield][:50].strip()) )
                                    # Historique
                                    self.values_searchtext[filter_namefield] = pattern
                                    self.values_searchtext[text_namefield] = self.requested_keys[text_namefield][:50].strip()
                                break
    
    def make_filter(self, filter_schema, global_prefix=False):
        """
        Construit les éléments de la requête pour trier les résultats
        
        Le schéma est sous le format suivant : ::
        
            filter_schema = {
                'filter_namefield1' : ('lookup_key',),
                'filter_namefield2' : ('lookup_key', 'optionnal type'),
                ...
            }
        
        :type filter_schema: dict
        :param filter_schema: Un dictionnaire python contenant les relations 
                              "mots-clés->model" et leurs options.
        
        :type global_prefix: string
        :param global_prefix: (optional) Un préfixe a rajouter sur tout les éléments 
                              de la requete (utile pour les relations de model). N'y 
                              incluez pas de caractère de séparation de préfixe.
                              Vide par défaut
        """
        # Séléction des relations seulement si on a un prefix de relation qui
        # implique donc un modèle avec une relation
        if global_prefix:
            global_prefix = global_prefix+'__'
            self.lookup_query['select_related'] = True
        
        # Mise en forme du lookup selon les filtrés postés
        for filter_namefield, opts in filter_schema.items():
            # Init à zéro pour faire plaisir au template
            self.values_filter[filter_namefield] = False
            # Si le motif est dans le request et qu'il n'est pas vide
            if self.requested_keys.has_key(filter_namefield) and self.requested_keys[filter_namefield]:
                # Nom du motif avec son type de séléction dans la db api
                keylookup = opts[0]
                # Marque le motif et sa valeure pour le repositionner dans 
                # le template
                self.values_filter[filter_namefield] = self.parse_pattern_value( self.requested_keys[filter_namefield], opts)
                # En cas de préfixe globale
                if global_prefix: keylookup = global_prefix+keylookup
                # Ajoute le motif à la requete
                self.lookup_query[keylookup] = self.parse_pattern_value( self.requested_keys[filter_namefield], opts)

    def make_order(self, order_schema, global_prefix=False, **kwargs):
        """
        Construit les éléments de la requête pour ordonner les résultats
        
        Le schéma est sous le format suivant : ::
        
            order_schema = {
                # Utilise asc/desc comme motifs pour un simple tri 
                # ascendant/descendant
                'order_namefield1' : 'order_key',
                # Utilise des motifs spécifiques entrainant des taches spécifiques
                'order_namefield2' : {
                    'pattern1' : 'order_key',
                    'pattern2' : '-order_key',
                    ...
                },
                ...
            }
        
        :type order_schema: dict
        :param order_schema: Un dictionnaire python contenant les relations 
                              "mots-clés->model" et leurs options.
        
        :type global_prefix: string
        :param global_prefix: (optional) Un préfixe a rajouter sur tout les éléments 
                              de la requete (utile pour les relations de model). N'y 
                              incluez pas de caractère de séparation de préfixe.
                              Vide par défaut
        """
        value_patterns = ['asc','desc']
        # Mise en forme du lookup selon les filtres postés
        for order_namefield, opts in order_schema.items():
            self.values_order[order_namefield] = False
            # Si le motif est dans le request et qu'il n'est pas vide
            if self.requested_keys.has_key(order_namefield) and self.requested_keys[order_namefield]:
                # En cas de dictionnaire, on passe en mode spécifique 
                if isinstance(opts, dict):
                    value_patterns = opts.keys()
                # Si le motif donné est autorisé dans le schéma
                if self.requested_keys[order_namefield] in value_patterns:
                    self.values_order[order_namefield] = self.requested_keys[order_namefield]
                    # Mode spécifique
                    if isinstance(opts, dict):
                        lkey = opts[ self.requested_keys[order_namefield] ]
                        # En cas de préfixe globale
                        if global_prefix: lkey = global_prefix+lkey
                    # Mode normal (ascendant/descendant)
                    else:
                        # Ordre ascendant par défaut
                        lkey = opts
                        # En cas de préfixe globale
                        if global_prefix: lkey = global_prefix+lkey
                        # Ordre descendant sur demande
                        if self.requested_keys[order_namefield] == 'desc':
                            lkey = "-"+lkey
                        # Ajoute le motif à la requete
                    self.lookup_order.append(lkey)
            elif kwargs.get('default_%s'%order_namefield, False):
                default = kwargs['default_%s'%order_namefield]
                self.values_order[order_namefield] = default
                self.lookup_order.append(order_schema[order_namefield][default])

    def make_extra(self, extra_schema):
        """
        Construit les éléments de la requête pour la partie "extra" de la db api.
        Ne gère pour l'instant que les "select", utile pour faire des count sur 
        des liaisons.
        
        Le schéma est sous le format suivant : ::
        
            extra_schema = {
                '' : '',
                'extra_namefield': (
                    ('pattern1', {'lookup_key': 'SELECT plop FROM foobar WHERE id=1'}),
                    ...
                )
            }
        
        :type extra_schema: dict
        :param extra_schema: Un dictionnaire python contenant les relations 
                              "mots-clés->model" et leurs options.
        """
        # Mise en forme du lookup selon les filtres postés
        for extra_namefield, opts in extra_schema.items():
            self.values_extra[extra_namefield] = False
            # Si le motif est dans le request et qu'il n'est pas vide
            if self.requested_keys.has_key(extra_namefield) and self.requested_keys[extra_namefield]:
                # Test toute les possibilités prévus par le schémas
                for pattern, selects in opts:
                    if self.requested_keys[extra_namefield] == pattern:
                        self.values_extra[extra_namefield] = self.requested_keys[extra_namefield]
                        # Ajoute les séléctions en extra de la requete
                        for k, v in selects.items():
                            if not self.lookup_extra.has_key('select'):
                                self.lookup_extra['select'] = {}
                            self.lookup_extra['select'][k] = v
                        break

    
    def make_html_form(self, schema, values, template, initcontext={}, hidden_values={}):
        """
        Compile le template d'un formulaire html pour une recherche/tri/ordre
        
        :type schema: dict
        :param schema: Le schéma utilisé pour la recherche
        
        :type values: dict
        :param values: Les valeurs soumises dans le formulaire (valeurs vides quand le 
                       manager n'a rien trouvé dans le request en comparaison de son 
                       schéma de recherche)
        
        :type template: string
        :param template: Contenu du template à compiler avec les données du contexte.
        
        :type initcontext: dict
        :param initcontext: (optional) Contexte de base à passer au template et auquel 
                            sera ajouté le contexte du formulaire de recherche.
                            Vide par défaut.
        
        :type hidden_values: dict
        :param hidden_values: (optional) Valeurs à placer dans des champs cachés, le nom 
                              clé de chaque élément sera le nom du champ (@name) et la 
                              valeur de l'élément sera la valeur du champ (@value).
                              Vide par défaut.
        
        :rtype: string
        :return: Le template compilé contenant le formulaire de recherche et les critères 
                 de recherche qui ont été soumis (s'il y'en a).
        """
        # Valeurs optionnelles à faire passer dans un champ hidden
        hidden = """<input type="hidden" name="%s" value="%s"/>\n"""
        hidden_fields = ''
        for key, val in hidden_values.items():
            hidden_fields += hidden % (key, val)
        
        # Variable pour le template
        extra_context = {
            'schema': schema,
            'requested_keys': values,
            'hidden_fields': hidden_fields,
        }
        initcontext.update(extra_context)
        
        return loader.get_template(template).render(RequestContext(self.request, initcontext))
    
    def make_url_args(self, values, without=None):
        """
        Forme les arguments de recherche à ajouter à l'url en cours (comme 
        ceux de pour la pagination)
        
        :type values: dict
        :param values: Les valeurs soumises dans le formulaire (valeurs vides quand le 
                       manager n'a rien trouvé dans le request en comparaison de son 
                       schéma de recherche)
        
        :rtype: list
        :return: Liste des arguments, chaque élément de la liste est un argument déja 
                 formé (``name=value``) et encodé pour être ajouté à une URL.
        """
        url_args = []
        for k,v in values.items():
            if v and k != without:
                ## Prend soin des arguments non string
                #if not isinstance(v, basestring):
                    #v = str(v)
                ## Prends soin des strings unicodes (que urllib n'apprécie pas)
                #elif isinstance(v, unicode):
                    #v = v.encode('utf-8', 'ignore')
                # Ajout l'argument échappé pour l'url
                url_args.append( "%s=%s" % (k, urlquote(v)) )
        
        return url_args
    
    def make_complete_urlargs(self, without=None):
        """
        Forme tout les arguments de recherche dans une seule et meme url
        """
        args = []
        for values in (self.values_searchtext, self.values_filter, self.values_order):
            args += self.make_url_args(values, without=without)
        return "&amp;".join(args)
    
    def make_all_urlargs(self, without=None):
        """
        Forme tout les arguments de recherche dans une seule et meme url
        
        DEPRECATED
        """
        self.url_args = self.make_complete_urlargs(without=without)
    
    def parse_pattern_value(self, value, pattern_schema):
        """
        Typage de la valeur d'un motif 
        
        :type value: string
        :param value: Valeur retrouvée dans le Request fournit. Quel que soit son type 
                      visé, elle est toujours fournit dans un string (vu qu'elle provient 
                      de la requête).
        
        :type pattern_schema: string or list or dict
        :param pattern_schema: Options du motif de recherche dans son schéma. Son type 
                               varie selon son schéma.
        
        :rtype: string or int
        :return: Retourne la valeur correctement typée
        """
        if len(pattern_schema)>1:
            if pattern_schema[1] == "int":
                return int(value)
        
        return value