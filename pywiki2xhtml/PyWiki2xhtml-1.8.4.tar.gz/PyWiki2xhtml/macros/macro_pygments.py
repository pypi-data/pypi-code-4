#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Macro 'pygments'

Cette macro permet d'insérer du code dans le document avec mise en valeur par coloration 
syntaxique selon un format de language.

Exemple de la syntaxe wiki : ::

    {% pygments javascript withlineos %}
    /**
    ** Un faux script Javascript
    ** ________________________________________
    **/
    $(document).ready(function(){
        alert("Hello World");
    });
    {% endpygments %}

Rendu prévu pour l'exemple : ::

    <table class="highlighttable"><tr><td class="linenos"><pre>1
    2
    3
    4
    5
    6
    7</pre></td><td class="code"><div class="highlight"><pre><span style="color: #408080; font-style: italic">/**</span>
    <span style="color: #408080; font-style: italic">** Un faux script Javascript</span>
    <span style="color: #408080; font-style: italic">** ________________________________________</span>
    <span style="color: #408080; font-style: italic">**/</span>
    $(<span style="color: #008000">document</span>).ready(<span style="color: #008000; font-weight: bold">function</span>(){
        alert(<span style="color: #BA2121">&quot;Hello World&quot;</span>);
    });
    </pre></div>
    </td></tr></table>

Cette macro fonctionne en mode 'post', pour l'ajouter aux macros du parser il suffit de 
la spécifier après l'instanciation du parser tel que : ::

    W2Xobject = Wiki2XhtmlParser()
    W2Xobject.add_macro('pygments', mode='post', func=parse_macro_pygments)

Requiert le module Python Pygments_.

.. _Pygments: http://pygments.org/
"""
try:
    from pygments import highlight
    from pygments.util import ClassNotFound
    from pygments.lexers import TextLexer, get_lexer_by_name
    from pygments.formatters import HtmlFormatter
except ImportError:
    def parse_macro_pygments(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
        """
        Méthode bidon qui renvoi la source inchangée
        
        Utilisé dans le cas ou pygments n'a pas été installé
        """
        return source
else:
    def parse_macro_pygments(source, opts, macro_escaped, macro_serial, macro_value, macro_args=None):
        """
        Méthode de traitement de la macro 'pygments'
        
        La syntaxe de cette macro peut recevoir deux arguments :
        
        * le premier indique le format du language du contenu, par défaut si 
        il n'est pas renseigné Pygments le formatera comme du Plain/text donc 
        sans highlight. Si le nom du language donné n'est pas reconnu, 
        Plain/text est assigné.
        * Le second argument peut indiquer "withlineos" pour que Pygment 
        rajoute les numéros de lignes au contenu. Par défaut il ne le fait pas, 
        tout autre valeur que "withlineos" lui fait prendre la valeur par défaut.
        
        TODO: Le gros défaut de cette méthode, c'est qu'elle ne pourra pas 
        inclure dans son contenu les tags d'une macro activée sur le parser, 
        sinon elle risque (selon l'ordre d'appel des méthodes des macros) 
        d'etre échappées voir empecher que pygments puisse traiter le contenu.
        TODO: Aucune idée de si on peut faire planter pygments par un 'exploit'.
        
        :type source: string
        :param source: Source du document complet.
        
        :type opts: dict
        :param opts: Dictionnaire des options en cours du parser.
        
        :type macro_escaped: string
        :param macro_escaped: Version d'échappement de la macro qui sert à sa recherche 
                            pour remplacement.
        
        :type macro_serial: string
        :param macro_serial: Clé unique de la macro.
        
        :type macro_value: string
        :param macro_value: Valeur source de la macro.
        
        :type macro_args: list or None
        :param macro_args: (optional) Liste des arguments inclus dans la macro, None si il 
                        n'y en avait pas.
        
        :rtype: string
        :return: Source du document avec le contenu de la macro remplacée par le rendu de 
                son traitement.
        """
        if macro_args:
            try:
                lexer = get_lexer_by_name(macro_args[0].lower(), stripall=True)
            except ClassNotFound:
                lexer = TextLexer()
        else:
            lexer = TextLexer()
        # Option de formatage
        formatopts = { 'noclasses':True }
        if len(macro_args)>1:
            if macro_args[1].lower() == 'withlineos':
                formatopts['linenos'] = 'table'
        
        # Rendu de Pygments
        render = highlight(macro_value, lexer, HtmlFormatter(**formatopts))
        return source.replace(macro_escaped, render)
