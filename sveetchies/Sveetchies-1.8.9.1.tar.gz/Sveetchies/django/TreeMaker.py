# -*- coding: utf-8 -*-
"""
Arborescence HTML d'une liste "plate" à partir d'un template

Voyez `Sveetchies.TreeMaker.RawTreeMaker` pour plus de détails sur le fonctionnement 
de ce système.

Le template utilisé ressemble à cela : ::

    <ul>
        {% for item in seq %}<li>
            <a href="{{ item.uri }}">{{ item.title }}</a>
            {{ item.recurse }}
        </li>{% endfor %}
    </ul>

Où :

* ``seq`` est la liste des éléments du niveau en cours;
* ``id``, ``title``, ``uri`` sont les attributs de l'élément en cours, ils sont 
  exactement ceux que vous avez spécifié à l'élément dans la liste "plate";
* ``item.recurse`` est une variable contenant un appel récursif à ce même template pour 
  les éléments descendants (niveau inférieur) de l'éléments en cours.

TODO: * Permettre d'embarquer aussi l'objet dans les résultats et pas seulement les 
        quelques attributs (title, uri, etc..) retenus actuellement;
      * Technique pour passer directement un QuerySet;
"""
from Sveetchies.TreeMaker import RawTreeMaker

from django.template import Context, loader

class TemplatedTree(RawTreeMaker):
    """
    Héritage de `Sveetchies.TreeMaker.RawTreeMaker` pour procéder à la mise en forme de 
    l'arborescence à partir d'un template récursif
    """
    def render(self, seq_list=None, indent=0, recursed_template="kiwi/recurse_parent_tree.html", extra_context={}):
        """
        Retourne le résultat du template compilé pour afficher l'arborescence calculée
        
        :type seq_list: list
        :param seq_list: (optional) Liste d'éléments à traiter. Par défaut c'est le 
                         contenu de l'attribut ``self.tree`` qui est utilisé, celui-ci 
                         étant rempli à l'instanciation. En théorie vous n'avez pas 
                         besoin de spécifier cet argument, il est destiné à un usage 
                         interne (lors des appels récursifs de chaque niveau de la liste 
                         globale).
        
        :type indent: int
        :param indent: (optional) Indique le niveau d'indentation de départ pour 
                       l'affichage, c'est en fait un pointeur du niveau en cours dans la 
                       liste globale. En utilisation interne il est toujours incrémenté 
                       de 1 à chaque nouveau niveau d'enfants. Par défaut il vaut 0.
        
        :type recursed_template: string
        :param recursed_template: (optional) Chemin du template récursif à utiliser, ce 
                                  doit être un chemin de template valide pour Django. Le 
                                  template par défaut est celui intégré à ``Kiwi`` (un 
                                  reste de l'ancienne provenance du code) vous aurez 
                                  probablement besoin de lui spécifier un autre template.
        
        :type extra_context: dict
        :param extra_context: (optional) Contexte supplémentaire à passer au template. 
                              Vide par défaut.
        
        :rtype: string
        :return: Le template compilé contenant l'arborescence
        """
        compiled_template = loader.get_template(recursed_template)
        
        if not seq_list:
            seq_list = self.tree
        
        # Trie la liste
        if self.order_key:
            seq_list = self.sort_list_by_dictkey(seq_list, self.order_key)

        for item in seq_list:
            # Traite les enfants
            if len(item['__TreeChildren'])>0:
                item['recurse'] = self.render(item['__TreeChildren'], indent=indent+1, recursed_template=recursed_template, extra_context=extra_context)
        
        # On passe ce contexte au template
        context = {
            "seq": seq_list,
            "indent": indent,
        }
        context.update(extra_context)
        c = Context(context)

        return compiled_template.render(c)
