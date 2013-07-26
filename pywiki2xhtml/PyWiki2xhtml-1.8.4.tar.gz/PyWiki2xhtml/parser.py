# -*- coding: utf-8 -*-
"""
Parser de transformation de base sans les macros

TODO: Certains bouts de code injectent de la syntaxe wiki sans employer la table de 
référence de syntaxe des tags mais directement en dur tel que 
``self.__hashTitleSummary``, les helper et les macros
"""
import string, re, os.path, flat2tree

class Wiki2XhtmlParser(object):
    """
    Parser principal
    """
    def __init__(self):
        """
        Initialisation du parser ou se trouve toute les options par défaut et 
        l'indexation d'une éventuelles listes d'acronymes.
        """
        self.s = ''

        # Tags inline reconnus
        self.inline_syntax = {
            'em' : (u"''",u"''"),
            'strong' : (u'__',u'__'),
            'acronym' : (u'??',u'??'),
            'a' : (u'[',u']'),
            'img' : (u'((',u'))'),
            'q' : (u'{{',u'}}'),
            'code' : (u'@@',u'@@'),
            'anchor' : (u'~',u'~'),
            'del' : (u'--',u'--'),
            'ins' : (u'++',u'++'),
            'note' : (u'$$',u'$$'),
            'word' : (u'¶¶¶',u'¶¶¶'),
            'embed' : (u'«««',u'»»»'),
        }

        self.opt = {
            'active_antispam': True,     # Activation de l'antispam pour les emails
            'active_urls': True,        # Activation des liens []
            'active_auto_img': False,    # Activation des images automatiques dans les liens []
            'active_br': True,      # Activation du <br /> %%%
            'active_code': True,        # Activation du <code> @@...@@
            'active_del': True,     # Activation des del --..--
            'active_em': True,      # Activation du <em> ''...''
            'active_ins': True,     # Activation des ins ++..++
            'active_img': True,     # Activation des images (())
            'active_q': True,       # Activation du <q> {{...}}
            'active_strong': True,  # Activation du <strong> __...__
            'active_acronym': True, # Activation des acronymes
            'active_anchor': True,  # Activation des ancres ~...~
            'active_embeds': True,  # Activation des embed «««..»»» (actif par défaut)
            'active_empty': False,       # Activation du bloc vide øøø (inactif par défaut)
            'active_footnotes': True,   # Activation des notes de bas de page $$..$$
            'active_hr': False,      # Activation des <hr />
            'active_lists': True,       # Activation des listes
            'active_menu_title': False,       # Activation des résumés de titres (inactif par défaut)
            'active_macros': False,       # Activation des macros (inactif par défaut)
            'active_pre': True,     # Activation du <pre>
            'active_quote': True,       # Activation du <blockquote>
            'active_title': True,       # Activation des titres !!!
            'active_wikiwords': False,   # Activation des mots wiki (inactif par défaut)
    
            'parse_pre': True,          # Parser l'intérieur de blocs <pre> ?
    
            'active_fr_syntax': True,   # Corrections syntaxe FR
    
            'first_title_level': 4,  # Premier niveau de titre <h..>
            
            # Pour les notes de bas de page
            'note_prefix': 'wiki-footnote',
            'note_str': u'<div class="footnotes"><h4>Notes</h4>%s</div>',
    
            'words_pattern': u'%s([A-Z][A-Za-z0-9_]+)%s' % (self.inline_syntax['word'][0], self.inline_syntax['word'][1]),
            'mail_pattern': r'^([0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*@([0-9a-zA-Z][-\w]*[0-9a-zA-Z]\.)+[a-zA-Z]{2,9})$',
    
            # Par défaut, pas d'acronymes
            'acronyms_file': None,
            #'acronyms_file': os.path.dirname(__file__)+'/acronyms.txt', # Fichiers d'acronymes au meme endroit que le parser
    
            # Attributs html par défaut pour les éléments embed
            'default_embed_styles': u' wmode="transparent" style="width:400px; height:326px;" type="application/x-shockwave-flash"',
            
            # Options par défaut pour les wikiword
            'absolute_path_wikiroot': '/%s/', # chemin absolu vers le wiki
            'absolute_path_createpage': '/add/%s/', # chemin absolu pour créer une page dans le wiki, None pour le désactiver
            'published_wikipage': {}, # dictionnaire uri=>titre des pages publiés
            
            # Options pour l'url spéciale task:// et category://
            'absolute_path_checkitroot': 'http://redmine.sveetch.net/issues/show/\\1', # chemin complet (avec ou sans http://..) vers un gestionnaire de tâches
            
            # Urls spéciales par défaut
            'special_urls': {
                r'^google://(.*)$': u'http://www.google.fr/search?hl=fr&#38;q=\\1&#38;start=0',
                r'^task://(.*)$': u'http://redmine.sveetch.net/issues/show/\\1',
                r'^wikipedia://(.*)$': u'http://fr.wikipedia.org/wiki/\\1',
            },
            
            # Attributs possibles des positionnements d'images
            'image_float_styles': {
                'left': u' style="float:left; margin: 0 1em 1em 0;"',
                'right': u' style="float:right; margin: 0 0 1em 1em;"',
                'center': u' style="display:block; margin: 1em auto 1em auto;"',
            },
        }
        
        # Par défaut, on cherchera le fichier acronyms.txt à l'emplacement d'ou est lancé le script
        self.acro_table = self.__getAcronyms()

        # Vars de tampon pour faire le sommaire des titres
        self.summary_dict = {} # liste du sommaire
        self.summary_title_id = 0 # id du titre

        self.foot_notes = {}
        

    def setOpt(self, name, value):
        """
        Méthode de modification d'une option
        
        :type name: string
        :param name: nom clé de l'option.
        
        :type value: any
        :param value: Valeur à assigner à l'option.
        """
        self.opt[name] = value

    def getOpt(self, name):
        """
        Méthode pour récupérer la valeure d'une option
        
        :type name: string
        :param name: nom clé de l'option.
        
        :rtype: any
        :return: Retourne la valeur de l'option si elle existe sinon False.
        """
        if (self.opt.has_key(name)):
            return self.opt[name]
        return False

    def kwargsOpt(self, kwargs):
        """
        Méthode de changements des options en une fois
        
        :type kwargs: dict
        :param kwargs: Dictionnaire (name=>value) de valeurs d'options à écraser.
        """
        self.opt.update(kwargs)

    def transform(self, s):
        """
        Traitement d'une chaîne pour lui appliquer la conversion vers XHTML
        
        :type s: string
        :param s: Source du document complet.
        
        :rtype: string
        :return: Texte transformé en XHTML.
        """
        # Initialisation des tags
        self.__initTags()
        self.foot_notes = {}

        # Vérification du niveau de titre
        if (self.getOpt('first_title_level') > 4):
            self.setOpt('first_title_level', 4)

        s = s.replace("\r",'')

        escape_pattern = []

        # Transformation des mots Wiki
        if self.getOpt('active_wikiwords') and self.getOpt('words_pattern'):
            s = self.__parseWikiWord(s)
        
        # Scinde le texte en lignes
        self.T = s.split("\n")
        self.T.append('')

        # Parse les blocs
        res = self.__parseBlocks()

        # Line break
        if (self.getOpt('active_br')):
            res = re.compile('(?<!\\\)%%%', re.M|re.S).sub('<br />', res)
            escape_pattern.append('%%%')

        # Nettoyage des \s en trop
        res = re.sub('[\s]+(</p>|</li>|</pre>)','\\1',res)
        res = re.sub('(<li>)[\s]+','\\1',res)

        # Ajout des séquences d'échappements pour les tags
        if (len(escape_pattern) > 0):
            escape_pattern = [re.escape(e) for e in escape_pattern]
            res = re.compile('\\\('+'|'.join(escape_pattern)+')').sub('\\1', res)

        # Calcul des notes de bas de page
        if (len(self.foot_notes) > 0):
            res_notes = ''
            i = 1
            n_keys = self.foot_notes.keys()
            n_keys.sort()
            for n in n_keys:
                res_notes += "\n"+u'<p>[<a href="#rev-%s" id="%s">%d</a>] %s</p>' % (n, n, i, self.foot_notes[n])
                i += 1
            res += "\n" + self.getOpt('note_str')%res_notes + "\n"

        # Calcul du sommaire de titres
        if self.getOpt('active_menu_title') and len(self.summary_dict)>1:
            obj = flat2tree.flatList_to_Tree(self.summary_dict)
            self.summary = obj.displayTreeForWiki()
        else:
            self.summary = None
        return res

    def render(self, source):
        """
        Renvoi un dictionnaire contenant la transformation de la source, sa 
        version originale, son sommaire
        
        :type source: string
        :param source: Chaîne de texte source dans la syntaxe Wiki.
        
        :rtype: dict
        :return: Dictionnaire contenant la source (source), le xhtml (xhtml) et le 
                 sommaire des titres (summary) si il y'en a un sinon il sera vide 
                 (None).
        """
        xhtml = self.transform(source)
        # Si l'option de sommaire des titres est activé, on le génère. Pendant 
        # sa génération on désactive l'option avant de la réactiver
        summary = None
        if self.getOpt('active_menu_title') and self.summary:
            self.setOpt('active_menu_title', False)
            summary = self.transform( self.summary )
            self.setOpt('active_menu_title', True)
        
        return {
            'source': source,
            'xhtml': xhtml,
            'summary': summary,
        }

    def __initTags(self):
        """
        Désattribution des tags désactivés puis construction des hash de
        références liés aux tags activés
        """
        self.inline_tags = self.inline_syntax.copy()
        if (not self.getOpt('active_urls')):
            del self.inline_tags['a']
        if (not self.getOpt('active_img')):
            del self.inline_tags['img']
        if (not self.getOpt('active_anchor')):
            del self.inline_tags['anchor']
        if (not self.getOpt('active_em')):
            del self.inline_tags['em']
        if (not self.getOpt('active_strong')):
            del self.inline_tags['strong']
        if (not self.getOpt('active_q')):
            del self.inline_tags['q']
        if (not self.getOpt('active_code')):
            del self.inline_tags['code']
        if (not self.getOpt('active_acronym')):
            del self.inline_tags['acronym']
        if (not self.getOpt('active_ins')):
            del self.inline_tags['ins']
        if (not self.getOpt('active_del')):
            del self.inline_tags['del']
        if (not self.getOpt('active_footnotes')):
            del self.inline_tags['note']
        if (not self.getOpt('active_wikiwords')):
            del self.inline_tags['word']
        if (not self.getOpt('active_embeds')):
            del self.inline_tags['embed']

        self.open_tags = self.__getTags()
        self.close_tags = self.__getTags(False)
        self.all_tags = self.__getAllTags()
        self.tag_pattern = self.__getTagsPattern()
        self.escape_table = self.__getEscapeTable()

    def __getTags(self, isOpen=True):
        """
        Forme les dictionnaires de tags ouvrants où fermants des éléments
        inline activés
        
        :type isOpen: bool
        :param isOpen: (optional) Indique si l'on gère les tags ouvrant ou pas (auquel 
                       cas on passe en mode fermant). Par défaut True.
        
        :rtype: dict
        :return: Dictionnaire d'éléments de tags.
        """
        res = {}
        for k in self.inline_tags.keys():
            if isOpen:
                res[k] = self.inline_tags[k][0]
            else:
                res[k] = self.inline_tags[k][1]
        return res

    def __getAllTags(self):
        """
        Forme une liste de tout les tags inline activés
        
        :rtype: dict
        :return: Dictionnaire des tags inlines à vide
        """
        res = {}
        for v in self.inline_tags.values():
            res[v[0]] = u''
            res[v[1]] = u''
        return res.keys()

    def __getTagsPattern(self, escape=0):
        """
        Forme le motif de la regex pour les éléments 'inline'
        
        :type escape: int
        :param escape: (optional) Indique si l'on doit insérer une partie d'échappement.
        
        :rtype: string
        :return: Regex des éléments inline
        """
        tags = [re.escape(e) for e in self.all_tags]
        res = '(%s)' % '|'.join(tags)

        if (not escape):
            res = '(?<!\\\)'+res

        return res

    def __getEscapeTable(self):
        """
        Forme une liste des versions d'échappements de syntaxe des éléments
        inline activés
        
        :rtype: list
        :return: Liste d'échappements des éléments inline.
        """
        res = []
        for v in self.all_tags:
            res.append(u'\\'+v)
        return res

    def __parseBlocks(self):
        """
        Parse chaque ligne et la transforme dans le bloc XHTML qui convient
        
        :rtype: string
        :return: Version XHTML de la source
        """
        mode = typeblock = None
        res = ''
        maxlen = len(self.T)
        i=0

        for v in self.T:
            pre_mode = mode
            pre_type = typeblock
            end = (i+1 == maxlen)

            typeblock, mode, line = self.__getLine(i, typeblock, mode)

            # Parse l'intérieur de la ligne/bloc pour transformer les syntaxes
            # des éléments 'inline'
            if (typeblock != 'pre' or self.getOpt('parse_pre')):
                line = self.__inlineWalk(line)

            # Limitation sur le niveau des titres
            if (typeblock == 'title' and mode > self.getOpt('first_title_level')):
                mode = self.getOpt('first_title_level')
    
            res += self.__closeLine(typeblock, mode, pre_type, pre_mode)
            res += self.__openLine(typeblock, mode, pre_type, pre_mode)

            # P dans les blockquotes
            if (typeblock == 'blockquote' and line.strip() == '' and pre_type == typeblock):
                res += u"</p>\n<p>"

            # Correction de la syntaxe FR dans tout sauf pre et hr
            if (typeblock != None and typeblock != 'pre' and typeblock != 'hr' and self.getOpt('active_fr_syntax')):
                line = re.sub('[ ]+([:?!;](\s|$))','&#160;\\1',line)

            res += line
            i+=1
        return res.strip()

    def __getLine(self, i, typeblock, mode):
        """
        Reconnaissance du type de bloc de la ligne donnée
        
        :type i: int
        :param i: Indice de clé de la ligne en cours dans l'index de toute les lignes.
        
        :type typeblock: string
        :param typeblock: Type de bloc de la ligne précédente
        
        :type mode: string
        :param mode: Mode de la ligne précédente
        
        :rtype: tuple
        :return: Tuple (typeblock, mode, line) de la ligne en cours.
        """
        pre_type = typeblock
        pre_mode = mode
        typeblock = mode = None

        if (self.T[i].strip() == ''):
            return typeblock, mode, ''

        line = self.htmlspecialchars(self.T[i], 'ENT_NOQUOTES')

        # Expressions de reconnaissance
        re_titre = re.match('^([!]{1,4})(.*)$', line)
        re_hr = re.match('^[-]{4}[- ]*$',line)
        re_blockquote = re.match('^(&#62;|;:)(.*)$', line)
        re_list = re.match('^([*#]+)(.*)$', line)
        re_pre = re.match('^[ ]{1}(.*)$', line)
        re_empty = re.match('^øøø(.*)$', line)
        re_escaped_macros = re.match('^(%s)(.*?)(%s)$' % ( re.escape('{%{M'), re.escape('M}%}') ), line)

        # Ligne vide
        if (line == ''):
            typeblock = 0
        # Bloc vide
        elif (self.getOpt('active_empty') and re_empty):
            typeblock = 'empty'
            line = re_empty.group(1).strip()
        # Echappements des macros
        elif (self.getOpt('active_macros') and re_escaped_macros):
            typeblock = 'macro'
        # Titre et création de leur sommaire
        elif (re_titre and self.getOpt('active_title')):
            typeblock = 'title'
            mode = len(re_titre.group(1))
            line = re_titre.group(2).strip()
            # récupère le titre pour le sommaire
            self.summary_title_id += 1
            if self.getOpt('active_menu_title'):
                self.__hashTitleSummary(mode, line)
        # Ligne HR
        elif (re_hr and self.getOpt('active_hr')):
            typeblock = 'hr'
            line = ''
        # Blockquote
        elif (re_blockquote and self.getOpt('active_quote')):
            typeblock = 'blockquote'
            line = re_blockquote.group(2).strip()
        # Liste
        elif (re_list and self.getOpt('active_lists')):
            typeblock = 'list'
            mode = re_list.group(1)
            valid = 1
            # Vérifiaction d'intégrité
            if (typeblock != pre_type):
                dl = 0
            else:
                dl = len(pre_mode)
            d = len(mode)
            delta = d-dl

            if (delta < 0 and pre_mode.find(mode) != 0):
                valid = 0
            if (delta > 0 and typeblock == pre_type and mode.find(pre_mode) != 0):
                valid = 0
            if (delta == 0 and mode != pre_mode):
                valid = 0
            if (delta > 1):
                valid = 0

            if (valid == 0):
                typeblock = 'p'
                mode = None
                line = u'<br />'+line
            else:
                line = re_list.group(2).strip()
        # Préformaté
        elif (re_pre and self.getOpt('active_pre')):
            typeblock = 'pre'
            line = re_pre.group(1)
        else:
            typeblock = 'p'
            line = line.strip()

        return typeblock, mode, line

    def __openLine(self, typeline, mode, pre_type, pre_mode):
        """
        Ouverture de l'élément xhtml de la ligne en cours
        
        :type typeline: string
        :param typeline: Type de bloc de la ligne en cours
        
        :type mode: string
        :param mode: Mode la ligne en cours
        
        :type pre_type: string
        :param pre_type: Type de bloc de la ligne précédente
        
        :type pre_mode: int
        :param pre_mode: Mode la ligne en cours
        
        :rtype: string
        :return: Xhtml de la ligne en cours
        """
        openln = (typeline != pre_type)

        if (openln and typeline == 'p'):
            return u"\n<p>"
        elif (openln and typeline == 'blockquote'):
            return u"\n<blockquote><p>"
        elif ((openln or mode != pre_mode) and typeline == 'title'):
            anchor = u' id="wikititle_%s"'%unicode(self.summary_title_id)
            return "%s%d%s%s"%("\n<h", 6-mode, anchor, '>')
        elif (openln and typeline == 'pre'):
            return u"\n<pre>"
        elif (openln and typeline == 'hr'):
            return u"\n<hr />"
        elif (typeline == 'list'):
            if (openln):
                dl = 0
            else :
                dl = len(pre_mode)
            d = len(mode)
            delta = d-dl
            res = ''

            if (delta > 0):
                if (mode[-1] == '*'):
                    res += u"<ul>\n"
                else:
                    res += u"<ol>\n"
            elif (delta < 0):
                res += u"</li>\n"
                for i in range(abs(delta)):
                    if (pre_mode[0-i-1] == '*'):
                        res += u"</ul>\n</li>\n"
                    else:
                        res += u"</ol>\n</li>\n"
            else:
                res += u"</li>\n"

            return res+u"<li>"
        else:
            return ''

    def __closeLine(self, typeline, mode, pre_type, pre_mode):
        """
        Fermeture de l'élément xhtml de la ligne en cours
        
        :type typeline: string
        :param typeline: Type de la ligne en cours
        
        :type mode: string
        :param mode: Mode la ligne en cours
        
        :type pre_type: string
        :param pre_type: Type de bloc de la ligne précédente
        
        :type pre_mode: int
        :param pre_mode: Mode la ligne en cours
        
        :rtype: string
        :return: Xhtml de la ligne en cours
        """
        close = (typeline != pre_type)

        if (close and pre_type == 'p'):
            return u"</p>\n"
        elif (close and pre_type == 'blockquote'):
            return u"</p></blockquote>\n"
        elif ((close or mode != pre_mode) and pre_type == 'title'):
            return "%s%d%s" % ("</h", 6-pre_mode, ">\n")
        elif (close and pre_type == 'pre'):
            return u"</pre>\n"
        elif (close and pre_type == 'list'):
            res = u''
            for i in range(len(pre_mode)):
                if (pre_mode[0-i-1] == '*'):
                    res += u"</li>\n</ul>"
                else:
                    res += u"</li>\n</ol>"
            return res
        else:
            return "\n"

    def __inlineWalk(self, s, allow_only=None):
        """
        Découpe et parse la ligne donnée pour rechercher et transformer les
        éléments 'inline présents.
        
        :type s: string
        :param s: Chaîne d'une ligne
        
        :type allow_only: list
        :param allow_only: (optional) Liste des éléments autorisés dans un élément 
                           inline. Si vide, pas d'éléments interdit. Vide par défaut.
        
        :rtype: string
        :return: Xhtml de la ligne
        """
        tree = re.split(self.tag_pattern, s)
        res = ''

        i = [0]
        while (i[0] < len(tree)):
            attr = ['']

            if (tree[i[0]] in self.open_tags.values() and
            (allow_only == None or
            self.open_tags.keys()[self.open_tags.values().index(tree[i[0]])] in allow_only)):
                tag = [self.open_tags.keys()[self.open_tags.values().index(tree[i[0]])]]
                tag_type = ['open']

                tree, tag, attr, tag_type, tidy = self.__makeTag(tree,tag,i[0],i,attr,tag_type)
                #
                if (tidy != None):
                    if (tag[0] != ''):
                        res = res+u'<'+tag[0]+attr[0]
                        if (tag_type[0] == 'open'):
                            res = u'%s>' % res
                        else:
                            res = u'%s />' % res
                    res = res+tidy
                else:
                    res = res+tree[i[0]]

            else:
                res = res+tree[i[0]]
            i[0] = i[0]+1

        # Suppression des echappements
        for c in range(len(self.escape_table)-1):
            res = res.replace(self.escape_table[c],self.all_tags[c])

        return res

    def __makeTag(self, tree, tag, position, j, attr, tag_type):
        """
        Construit les paramètres et l'élément du tag d'un bloc
        
        :type tree: string
        :param tree: 
        
        :type tag: string
        :param tag: 
        
        :type position: string
        :param position: 
        
        :type j: string
        :param j: 
        
        :type attr: string
        :param attr: 
        
        :type tag_type: string
        :param tag_type: 
        
        :rtype: tuple
        :return: Tuple (tree, tag, attr, tag_type, res) dont tout les éléments sont 
                 des string.
        """
        res = ''
        closed = 0

        itag = self.close_tags[tag[0]]

        # Recherche fermeture
        for i in range(position+1,len(tree)):
            if (tree[i] == itag):
                closed = 1
                break

        # Résultat
        if (closed == 1):
            for i in range(position+1,len(tree)):
                if (tree[i] != itag):
                    res = res+tree[i]
                else:
                    if (tag[0] == 'a'):
                        tag, attr, tag_type, res = self.__parseLink(res, tag, attr, tag_type)
                    elif (tag[0] == 'img'):
                        tag_type[0] = 'close'
                        attr, res = self.__parseImg(res, attr)
                    elif (tag[0] == 'acronym'):
                        attr, res = self.__parseAcronym(res,attr)
                    elif (tag[0] == 'q'):
                        attr, res = self.__parseQ(res,attr)
                    elif (tag[0] == 'anchor'):
                        tag[0] = 'a'
                        attr, res = self.__parseAnchor(res,attr)
                    elif (tag[0] == 'note'):
                        tag[0] = ''
                        res = self.__parseNote(res)
                    elif (tag[0] == 'embed'):
                        tag, attr, tag_type, res = self.__parseEmbed(res, tag, attr, tag_type)
                    # hack crado pour virer les <word/> sur les wikiword invalides
                    elif (tag[0] == 'word'):
                        tag[0] = 'span'
                    else:
                        res = self.__inlineWalk(res)

                    if (tag_type[0] == 'open' and tag[0] != ''):
                        res = '%s</%s>'% (res, tag[0])
                    j[0] = i
                    break
        else:
            return tree, tag, attr, tag_type, None

        return tree, tag, attr, tag_type, res

    def __antiSpam(self, source):
        """
        Méthode qui modifie la chaîne d'un email pour le rendre inaccessible aux spambots
        
        OBSOLETE: Les spambots lisent ce format depuis bien longtemps, il faudrait 
        trouver une technique plus récente.
        DEPRECATED: En fait actuellement, le retour n'est pas l'email modifié, mais 
        l'email original.
        
        :type source: string
        :param source: Source de l'email.
        
        :rtype: string
        :return: Email modifié.
        """
        encoded = '%'+source[0:(len(source)-1)]
        return source

    def __parseLink(self, s, tag, attr, tag_type):
        """
        Parse un lien qui a été détecté
        
        :type s: string
        :param s: Contenu du lien
        
        :type tag: tuple
        :param tag: ÉLéments XHTML ouvrant et fermant du lien
        
        :type attr: list
        :param attr: Liste des attributs spécifiés
        
        :type tag_type: string
        :param tag_type: Type du tag
        
        :rtype: tuple
        :return: Tuple (tag, attr, tag_type, content)
        """
        n_str = self.__inlineWalk(s,['acronym','img'])
        data = n_str.split('|')
        lang = title = ''
        no_image = 0

        # Juste un lien sans autres options        
        if (len(data) == 1):
            url = s.strip()
            content = s
        # Lien avec des options
        else:
            url = data[1].strip()
            content = data[0]
            # Gestion des options lang|titre dans le lien|desactivation du
            # mode "auto image"
            if (len(data) > 2):
                lang = self.protectAttr(data[2], True)
                if (len(data) > 3):
                    title = data[3]
                    if (len(data) > 4):
                        if (data[4]) : no_image = 1
        # Traitement des url spéciales
        for k,v in self.getOpt('special_urls').items():
            url = re.compile(k).sub(v, url)

        re.sub('&#160;','',url)

        if (re.match('^(.+)[.](gif|jpg|jpeg|png)$',url) and not no_image and
        self.getOpt('active_auto_img')):
            attr[0] += u' src="%s"'%self.protectAttr(self.protectUrls(url))
            if (len(data) > 1) :
                attr[0] += u' alt="%s"'%self.protectAttr(content)
            else:
                attr[0] += u' alt=""'
            if (lang != ''): attr[0] += u' hreflang="%s"'%lang
            if (title != ''): attr[0] += u' title="%s"'%self.protectAttr(title)
            tag[0] = 'img'
            tag_type[0] = 'close'
            return tag, attr, tag_type, ''

        else:
            if(self.getOpt('active_antispam') and re.match('^mailto:',url)):
                    url = u'mailto:%s'%self.__antiSpam( url[7:None] )
            attr[0] += u' href="%s"'%self.protectAttr(self.protectUrls(self.__matchWikiWord(url)))
            if (lang != ''): attr[0] += u' hreflang="%s"'%self.protectAttr(lang)
            if (title != ''): attr[0] += u' title="%s"'%self.protectAttr(title)
            return tag, attr, tag_type, content

    def __parseImg(self, s, attr):
        """
        Forme les attributs à appliquer à l'élément d'une image (<img/> étant un élément 
        sans contenu)
        
        :type s: string
        :param s: Chaîne de l'élément d'image détecté.
        
        :type attr: list
        :param attr: Liste des attributs spécifiés.
        
        :rtype: tuple
        :return: Tuple (attr, content) mais content est toujours vide.
        """
        data = s.split('|')
        alt = ''
        # Url du média en premier argument
        url = data[0]
        # Alternate texte en second arg.
        if (len(data) > 1): alt = data[1]
        # Encapsule sainement les url et le texte alternatif
        attr[0] += u' src="%s"'%self.protectAttr(self.protectUrls(url))
        attr[0] += u' alt="%s"'%self.protectAttr(alt)
        # Option de positionnement en troisieme arg.
        if (len(data) > 2):
            if (data[2] == 'G' or data[2] == 'L'):
                attr[0] += self.getOpt('image_float_styles')['left']
            elif (data[2] == 'D' or data[2] == 'R'):
                attr[0] += self.getOpt('image_float_styles')['right']
            elif (data[2] == 'C'):
                attr[0] += self.getOpt('image_float_styles')['center']
        # Long descriptif en quatrième argument
        if (len(data) > 3):
            attr[0] += u' longdesc="%s"'%self.protectAttr(data[3])

        return attr, ''

    def __parseQ(self, s, attr):
        """
        Forme les attributs et le contenu de l'élément d'une citation
        
        :type s: string
        :param s: Chaîne de l'élément détecté.
        
        :type attr: list
        :param attr: Liste des attributs spécifiés.
        
        :rtype: tuple
        :return: Tuple (attr, content)
        """
        s = self.__inlineWalk(s)
        data = s.split('|')
        lang = cite = ''

        content = data[0]

        if (len(data) > 1):
            lang = self.protectAttr(data[1], True)
            if (lang != '') : attr[0] += u' lang="%s"'%lang
            if (len(data) > 2):
                attr[0] += u' cite="%s"'%self.protectAttr(data[2])

        return attr, content

    def __parseAnchor(self, s, attr):
        """
        Forme les attributs à appliquer à l'élément d'une ancre (une ancre étant un 
        élément sans contenu)
        
        :type s: string
        :param s: Chaîne de l'élément détecté.
        
        :type attr: list
        :param attr: Liste des attributs spécifiés.
        
        :rtype: tuple
        :return: Tuple (attr, content) mais content est toujours vide.
        """
        name = self.protectAttr(s, True)
        if (name != '') : attr[0] += u' id="%s"'%name
        return attr, ''

    def __parseNote(self, s):
        """
        Note wiki détecté dans du texte
        
        Capture le contenu de la note, l'ajoute à la liste des notes et remplace le 
        contenu dans le texte par un indice de note ancré.
        
        :type s: string
        :param s: Chaîne de l'élément détecté.
        
        :rtype: string
        :return: XHTML de l'indice de la note
        """
        i = len(self.foot_notes)+1
        i_key = unicode(i).zfill(3)
        nid = u'%s-%s' % (self.getOpt('note_prefix'), i_key)
        self.foot_notes[nid] = self.__inlineWalk(s)
        return u'<sup>\[<a href="#%s" id="rev-%s">%s</a>\]</sup>' % (nid, nid, i)

    def __parseAcronym(self, s, attr):
        """
        Parse un acronyme détecté
        
        :type s: string
        :param s: Chaîne de l'élément détecté.
        
        :type attr: list
        :param attr: Liste des attributs spécifiés.
        
        :rtype: tuple
        :return: Tuple (attr, content)
        """
        data = s.split('|')

        lang = title = ''
        acronym = data[0]

        if (len(data) > 1):
            title = data[1]
            if (len(data) > 2):
                lang = self.protectAttr(data[2], True)

        if (title == '' and self.acro_table.has_key(acronym)):
            title = self.acro_table[acronym]

        if (title != '') : attr[0] += u' title="%s"'%self.protectAttr(title)
        if (lang != '') : attr[0] += u' lang="%s"'%lang

        return attr, acronym

    def __getAcronyms(self):
        """
        Récupère la liste des acronymes disponible dans le fichier donné
        dans les options
        
        :rtype: dict
        :return: Dictionnaire de tout les acronymes
        """
        f = self.getOpt('acronyms_file')
        if f:
            res = {}
    
            if (os.path.isfile(f)):
                fp = open(f)
                fc = fp.readlines()
                fp.close()
    
                for v in fc:
                    v = v.split(':',1)
                    v = [e.strip() for e in v]
                    res[v[0]] = v[1]
    
                return res

        return {}

    def __strip_inlineSyntax(self, s):
        """
        Parse la chaine et nettoit tout le html qu'elle contient
        
        :type s: string
        :param s: Chaîne de texte à nettoyer
        
        :rtype: string
        :return: Chaîne nettoyée de tout html
        """
        return re.sub(r'<[^>]*?>', '', self.__inlineWalk(s))

    def __hashTitleSummary(self, level, name):
        """
        Ajoute un titre à la liste du sommaire des titres
        
        :type level: int
        :param level: Niveau (selon h1, h2, h3, etc..) du titre
        
        :type name: string
        :param name: Contenu du titre
        """
        title = u"[%s|#wikititle_%d]" % ( self.__strip_inlineSyntax(name), self.summary_title_id )
        self.summary_dict[self.summary_title_id] = { 'title': title, 'lv': level}

    def __parseWikiWord(self, s):
        """
        Recherche et remplace tout les mots wiki par leur équivalent XHTML
        
        :type s: string
        :param s: Chaîne de texte où remplacer les mots wiki
        
        :rtype: string
        :return: Chaîne de texte modifiée
        """
        return re.compile(self.getOpt('words_pattern'),re.M|re.S).sub(self.__replaceWikiWord, s)
    
    def __matchWikiWord(self, s):
        """
        Fonction qui test si une chaine envoyée est bien un wikiword.
        Sert à détecter les wikiword dans les liens.
        
        :type s: string
        :param s: Chaîne de texte censée contenir un wikiword.
        
        :rtype: string
        :return: Lien du wikiword si s'en était bien un.
        """
        if self.getOpt('active_wikiwords') and self.getOpt('word'):
            matchObj = re.match(self.getOpt('words_pattern'), u'%s%s%s' % (self.inline_syntax['word'][0], s, self.inline_syntax['word'][1]) )
            if matchObj != None:
                Word = matchObj.group(1)
                if self.getOpt('published_wikipage').has_key(Word):
                    return self.getOpt('absolute_path_wikiroot') % Word
                else:
                    return self.getOpt('absolute_path_createpage') % Word
        return s
    
    def __replaceWikiWord(self, matchobj):
        """
        Fonction de remplacement d'un wikiword trouvé par regex en son équivalent wiki 
        d'un lien [titre|url].
        
        :type matchobj: MatchObject
        :param matchobj: Objet du match de la regex de 
                         `Wiki2XhtmlParser.__parseWikiWord` d'un wikiword.
        
        :rtype: string
        :return: Lien wiki si s'en est bien un, sinon None
        """
        uriList = self.getOpt('published_wikipage')
        Word = matchobj.group(1)
        if Word:
            # le Wikiword est une page qui existe
            if uriList.has_key(Word):
                href = self.getOpt('absolute_path_wikiroot') % Word
                title = uriList[Word]
                return '[%s|%s]' % (title, href)
            # le Wikiword n'existe pas comme page
            elif self.getOpt('absolute_path_createpage'):
                href = self.getOpt('absolute_path_createpage') % Word
                title = Word
                return '[%s|%s]' % (title, href)
        
        return Word
    
    def __parseEmbed(self, s, tag, attr, tag_type):
        """
        Tag spécial pour les flash vidéo
        
        :type s: string
        :param s: Contenu du lien
        
        :type tag: tuple
        :param tag: Non utilisé
        
        :type attr: list
        :param attr: Liste des attributs spécifiés
        
        :type tag_type: string
        :param tag_type: Type du tag
        
        :rtype: tuple
        :return: Tuple (tag, attr, tag_type, content) mais content est toujours vide.
        """
        data = s.split('|')
        flashvars = False
        # Url du média en premier argument
        url = data[0]
        # Alternate texte en second arg.
        if (len(data) > 1):
            flashvars = data[1]
        # Rajoute les attributs communs de l'élément
        attr[0] += self.getOpt('default_embed_styles')
        # Encapsule sainement les url et le flashvars optionnel
        attr[0] += u' src="%s"'%self.protectAttr( self.protectUrls(url) )
        if flashvars:
            attr[0] += u' flashvars="%s"'%self.protectAttr(self.protectUrls(flashvars))
        return tag, attr, tag_type, ''

    def protectAttr(self, s, name=False):
        """
        Protection de l'intérieur d'un attribut d'un élément
        
        :type s: string
        :param s: Source du contenu de l'attribut à protéger
        
        :type name: bool
        :param name: Indique si l'on doit vérifier que le contenu comporte bien du texte 
                     sans autres caractères spéciaux que ``_:.-``. Si True et que le 
                     contenu contient autre chose, on renvoit directement une chaine 
                     vide.
        
        :rtype: string
        :return: Contenu nettoyé
        """
        if (name and not re.match('^[A-Za-z][A-Za-z0-9_:.-]*$', s)):
            return ''

        s = s.replace("'",u'&#039;')
        s = s.replace('"',u'&#34;')
        return s

    def protectUrls(self, s):
        """
        Protection simpliste envers les liens javascript:xxxx 
        
        :type s: string
        :param s: Source du contenu de l'attribut à protéger
        
        :rtype: string
        :return: Contenu nettoyé
        """
        import urllib
        if (re.match('^javascript:',s)):
            s = u'#'
        return s
    
    def htmlspecialchars( self, s, quote='ENT_COMPAT' ):
        """
        Échappement de caractères qui peuvent troubler la validiter du XHTML
        
        Ceci est en fait une pseudo-simulation de la fonction PHP htmlspecialchars()
        
        :type s: string
        :param s: Source du contenu
        
        :type quote: string
        :param quote: (optional) Type de support des quotes. ENT_COMPAT par défaut. 
                      Choix possibles entre :
                      * ENT_COMPAT remplace uniquement les doubles quotes;
                      * ENT_QUOTES remplace tout les types de quotes;
                      * ENT_NOQUOTES ne remplace aucune quote.
        
        :rtype: string
        :return: Contenu modifié
        """
        s = s.replace('&', u'&#38;')
        s = s.replace('<', u'&#60;')
        s = s.replace('>', u'&#62;')
        if quote != 'ENT_NOQUOTES':
            s = s.replace('"', u'&#34;')
        if quote == 'ENT_QUOTES':
            s = s.replace("'", u'&#039;')

        return s

    def help_syntax(self):
        """
        Renvoi l'aide sur la syntaxe sous forme de xhtml et selon les options
        
        :rtype: string
        :return: Contenu XHTML de l'aide
        """
        help = {}
        help['b'] = {}
        help['i'] = {}

        help['b'][0] = u'<div class="wikicontainer"><p>Laisser une ligne vide entre chaque bloc <em>de m&#234;me nature</em>.</p></div>\n'
        help['b'][0] = u'<h4>Paragraphe</h4><div class="wikicontainer"><p>Du texte et une ligne vide</p>'+\
        u'<h5>Exemple</h5><pre>Lorem ipsum dolor sit amet\n\nConsectetuer adipiscing elit.'+\
        u'</pre>\n'+\
        u'</div>\n'

        help['b']['active_title'] = u'<h4>Titre</h4> <div class="wikicontainer"><p><code>!!!</code>, <code>!!</code>, '+\
        u'<code>!</code> pour des titres plus ou moins importants</p>\n'+\
        u'<h5>Exemple</h5><pre>!!!Lorem ipsum dolor sit amet\n\n!!Consectetuer adipiscing elit.'+\
        u'</pre>\n'+\
        u'<h5>Donne</h5><h3>Lorem ipsum dolor sit amet</h3>\n<h4>Consectetuer adipiscing elit</h4>'+\
        u'</div>\n'

        help['b']['active_hr'] = u'<h4>Trait horizontal</h4> <div class="wikicontainer"><p><code>----</code></p></div>\n'

        help['b']['active_lists'] = u'<h4>Liste</h4> <div class="wikicontainer"><p>Ligne d&#233;butant par <code>*</code> ou '+\
        u'<code>#</code>. Il est possible de m&#233;langer les listes '+\
        u'(<code>*#*</code>) pour faire des listes de plusieurs niveaux. '+\
        u'Respecter le style de chaque niveau</p>'+\
        u'<h5>Exemple</h5><pre>*Lorem ipsum dolor sit amet\n**Consectetuer adipiscing\n*elit.'+\
        u'</pre>\n'+\
        u'<h5>Donne</h5><ul><li>Lorem ipsum dolor sit amet\n<ul><li>Consectetuer adipiscing</li></ul></li>\n<li>elit</li></ul>'+\
        u'</div>\n'

        help['b']['active_pre'] = u'<h4>Texte pr&#233;format&#233;</h4> <div class="wikicontainer"><p>Espace devant chaque ligne de texte</p>'+\
        u'<h5>Exemple</h5><pre> Lorem ipsum dolor sit amet\n Consectetuer adipiscing elit.'+\
        u'</pre>\n'+\
        u'<h5>Donne</h5><pre>Lorem ipsum dolor sit amet\nConsectetuer adipiscing elit</pre>'+\
        u'</div>\n'

        help['b']['active_quote'] = u'<h4>Bloc de citation</h4> <div class="wikicontainer"><p><code>&#62;</code> ou '+\
        u'<code>;:</code> devant chaque ligne de texte</p>'+\
        u'<h5>Exemple</h5><pre>&#62;Lorem ipsum dolor sit amet\n&#62;Consectetuer adipiscing elit.'+\
        u'</pre>\n'+\
        u'<h5>Donne</h5><blockquote><p>Lorem ipsum dolor sit amet</p>\n<p>Consectetuer adipiscing elit</p></blockquote>'+\
        u'</div>\n'

        help['b']['active_embeds'] = u'<h4>Flash</h4> <div class="wikicontainer"><p><code>&#171;&#171;&#171;URL|FLASHVARS&#187;&#187;&#187;</code> où '+\
        u'<strong>URL</strong> est l\'url de l\'objet flash et <strong>FLASHVARS</strong> est une chaine de Flashvars qui sera insérée tel quel.</p>'+\
        u'</div>\n'

        help['i']['active_fr_syntax'] = u'<div class="wikicontainer"><p>La correction de ponctuation est active. Un espace '+\
                    u'ins&#233;cable remplacera automatiquement tout espace '+\
                    u'pr&#233;c&#233;dant les marques ";","?",":" et "!".</p></div>\n'

        help['i']['active_em'] = u'<h4>Emphase</h4> <div class="wikicontainer"><p>Deux apostrophes <code>\'\'texte\'\'</code> qui donne <em>texte</em>.</p></div>\n'

        help['i']['active_strong'] = u'<h4>Forte emphase</h4> <div class="wikicontainer"><p>Deux soulign&#233;s <code>__texte__</code> qui donne <strong>texte</strong>.</p></div>\n'

        help['i']['active_br'] = u'<h4>Retour forc&#233; &#224; la ligne</h4> <div class="wikicontainer"><p><code>%%%</code></p></div>\n'

        help['i']['active_ins'] = u'<h4>Insertion</h4> <div class="wikicontainer"><p>Deux plus <code>++texte++</code> qui donne <ins>texte</ins>.</p></div>\n'

        help['i']['active_del'] = u'<h4>Suppression</h4> <div class="wikicontainer"><p>Deux moins <code>--texte--</code> qui donne <del>texte</del>.</p></div>\n'

        help['i']['active_urls'] = u'<h4>Lien</h4> <div class="wikicontainer"><p><code>[url]</code>, <code>[nom|url]</code>, '+\
        u'<code>[nom|url|langue]</code> ou <code>[nom|url|langue|titre]</code>.</p></div>'

        help['i']['active_img'] = u'<h4>Image</h4> <div class="wikicontainer"><p>'+\
        u'<code>((url|texte alternatif))</code>, '+\
        u'<code>((url|texte alternatif|position))</code> ou '+\
        u'<code>((url|texte alternatif|position|description longue))</code>.</p>'+\
        u'<p>La position peut prendre les valeur L ou G (gauche), R ou D (droite), C (centrée). L\'option C nécessite que le tag de l\'image soit seule sur sa ligne, séparée comme un paragraphe.</p></div>\n'

        help['i']['active_anchor'] = u'<h4>Ancre</h4> <div class="wikicontainer"><p><code>~ancre~</code></p></div>\n'

        help['i']['active_acronym'] = u'<h4>Acronyme</h4> <div class="wikicontainer"><p><code>??acronyme??</code> ou '+\
        u'<code>??acronyme|titre??</code></p></div>\n'

        help['i']['active_q'] = u'<h4>Citation</h4> <div class="wikicontainer"><p><code>{{citation}}</code>, '+\
        u'<code>{{citation|langue}}</code> ou <code>{{citation|langue|url}}</code></p>'+\
        u'<h5>Exemple</h5><pre>{{citation|fr}} ou {{Pas de panique, on va vous aider|fr|http://perdu.com}}</pre>\n'+\
        u'<h5>Donne</h5><p><q lang="fr">citation</q> ou <q cite="http://perdu.com" lang="fr">Pas de panique, on va vous aider</q></p>'+\
        u'</div>\n'

        help['i']['active_code'] = u'<h4> Code</h4> <div class="wikicontainer"><p><code>@@code ici@@</code> qui donne <code>texte</code>.</p></div>\n'

        help['i']['active_footnotes'] = u'<h4> Note de bas de page</h4> <div class="wikicontainer"><p><code>$$Corps de la note$$</code></p></div>\n'

        # sommaire
        res = u'<p id="summary"><a href="#block">Blocs</a> | <a href="#inline">&#201;l&#233;ments en ligne</a></p>'
        # blocs
        if (len(help['b'].items()) > 0):
            res += u'<h3 class="clean_title" id="block">Blocs</h3>\n'
            res += u'<ul class="clean_list">\n'
            for kb in help['b'].keys():
                if self.getOpt(kb) or kb == 0:
                    res += u'<li>\n%s</li>\n'%help['b'][kb]
            res += u'</ul>'
        # elements 'en ligne'
        if (len(help['i'].items()) > 0):
            res += u'<h3 class="clean_title" id="inline">&#201;l&#233;ments en ligne</h3>\n'
            res += u'<ul class="clean_list">\n'
            for ki in help['i'].keys():
                if self.getOpt(ki) or ki == 0:
                    res += u'<li>%s</li>\n'%help['i'][ki]
            res += u'</ul>\n'
        # div à remplir en js pour faire de la prévisualisation
        res += u'<div id="wikiSyntaxDemo" class="inputBox"></div>\n'
        return res

class Wiki2XhtmlParserNewSyntax(Wiki2XhtmlParser):
    """
    Clone du parser principal mais avec une syntaxe légèrement plus conviviale.
    """
    def __init__(self):
        super(Wiki2XhtmlParserNewSyntax, self).__init__()
        # Tags inline reconnus
        self.inline_syntax = {
            'em' : (u"''",u"''"),
            'strong' : (u'**',u'**'),
            'acronym' : (u'??',u'??'),
            'a' : (u'[',u']'),
            'img' : (u'((',u'))'),
            'q' : (u'{{',u'}}'),
            'code' : (u'@@',u'@@'),
            'anchor' : (u'~',u'~'),
            'del' : (u'--',u'--'),
            'ins' : (u'__',u'__'),
            'note' : (u'$$',u'$$'),
            'word' : (u'¶¶¶',u'¶¶¶'),
            'embed' : (u'«««',u'»»»')
        }
