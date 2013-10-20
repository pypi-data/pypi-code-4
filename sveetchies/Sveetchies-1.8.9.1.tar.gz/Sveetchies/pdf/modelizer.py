# -*- coding: utf-8 -*-
"""
Raccourcis de modélisation d'élements du document PDF
"""
import copy, os

from reportlab.platypus import *
from reportlab.lib.units import inch

class BaseModelizer(object):
    """
    Interface de modélisation des éléments de page de document
    """
    def __init__(self, elements=[], passive=False, default_family_font=None, medias_path='', style=None):
        """
        :type elements: list
        :param elements: (optional) Liste de base d'éléments "Platypus" prêts à être 
                         intégré à la page. Vide par défaut.
        
        :type passive: bool
        :param passive: (optional) Active le mode passif, qui fait que le modelizer ne 
                        modifie jamais la liste des éléments, il ne fait que construire 
                        les éléments qu'on lui demande et les retourne, à charge de 
                        l'utilisateur de les ajouter à la page. Désactivé par défaut, 
                        donc le modelizer ajoute tout ce qu'il construit dans la liste des 
                        éléments.
        
        :type default_family_font: string
        :param default_family_font: (optional) Nom d'une police à spécifier par défaut 
                                    dans tout les éléments. Vide par défaut, donc aucun 
                                    élément ne spécifie de Police particulière par défaut.
        
        :type medias_path: string
        :param medias_path: (optional) Chemin des médias utilisés dans le document. Sert 
                            exclusivement pour retrouver les images. Vide par défaut, 
                            donc toute les images doivent être spécifiés avec un chemin 
                            complet valable. Ce chemin est préfixé à TOUT les médias, 
                            donc si vos médias sont dispersés à plusieurs endroits 
                            différents, il est mieux de le laisser vide.
        
        :type style: dict
        :param style: (optional) Registre des styles à utiliser pour formater les 
                      éléments. Bien qu'en argument nommé, il est indispensable de le 
                      spécifier. En général le style 'default' inclut dans ReportLab 
                      fera l'affaire.
        """
        self.passive = passive
        self.elements = elements
        self.style = style
        self.medias_path = medias_path
        self.default_family_font = default_family_font
    
    def _active_return(self, obj, passive=False):
        """
        :type obj: object
        :param obj: Objet (en général de Platypus) à ajouter à la liste des éléments
        
        :type passive: bool
        :param passive: (optional) Permet d'activer le mode passif malgré l'option 
                        spécifiée à l'instanciation du modelizer.
                        
        :rtype: object
        :return: Renvoi simplement l'objet spécifié à la méthode
        """
        if not self.passive and not passive:
            self.elements.append(obj)
        return obj

    def para_format(self, source, size=12, line_height=16, align=None, color=None):
        """
        Conteneur de texte formaté
        
        :type source: string
        :param source: Texte du paragraphe, peut contenir aussi les quelques éléments 
                       HTML 4.0 compatibles (b, i, etc..) avec ReportLab.
        
        :type size: int
        :param size: (optional) Taille de la police utilisée. 12 unités par défaut.
        
        :type line_height: int
        :param line_height: (optional) Hauteur de ligne du texte. 16 unités par défaut 
                            (en concordance avec la taille par défaut).
        
        :type align: string
        :param align: (optional) Type d'alignement du texte, 'left', 'center' ou 'right'. 
                      Vide par défaut.
        
        :type color: object `reportlab.lib.colors`
        :param color: (optional) Couleur globale du texte. Vide par défaut.
        
        :rtype: string
        :return: Texte encerclé dans les balises de paragraphe et police selon ses 
                 options de mise en forme.
        """
        font_attrs = []
        para_attrs = []
        
        # Option du choix de la famille de police
        if self.default_family_font:
            font_attrs.append('name="%s"' % self.default_family_font)
        
        # Options du paragraphe
        if align:
            para_attrs.append('align="%s"' % align)
        if size:
            para_attrs.append('size="%s"' % size)
        if color:
            para_attrs.append('color="%s"' % color)
        if line_height:
            para_attrs.append('leading="%s"' % line_height)

        # Constitution des éléments XML contenant les options
        para = ('', '')
        if len(para_attrs)>0:
            para = ('<para %s>'% ' '.join(para_attrs), '</para>')
        if len(font_attrs)>0:
            font = ('<font %s>'% ' '.join(font_attrs), '</font>')
        start = para[0]+font[0]
        end = font[1]+para[1]
        content = start+source+end
        
        return content

    def BREAK(self, passive=False):
        """
        Un simple pointeur pour ajouter un élément qui force le passage à la page 
        suivante.
        """
        return self._active_return( PageBreak(), passive=passive )

class HTMLInterface(BaseModelizer):
    """
    Surcouche d'interface pour la modélisation pré-déterminés des éléments dans un 
    esprit HTML-like.
    """
    def STRONG(self, content):
        """
        Mise en gras
        
        :type content: string
        :param content: Texte
        
        :rtype: string
        :return: Texte encerclé par sa balise de mise en forme.
        """
        return "<strong>%s</strong>" % content

    def EMPHASE(self, content):
        """
        Mise en emphase (italique)
        
        :type content: string
        :param content: Texte
        
        :rtype: string
        :return: Texte encerclé par sa balise de mise en forme.
        """
        return "<em>%s</em>" % content

    def MARGIN(self, obj, margin=None, passive=False):
        """
        Marges extérieures imposés à un élément
        
        Les marges horizontales ne sont pas implémentés. Et les marges 
        verticales sont simplement imposés en ajoutant un "Spacer" de la hauteur de la 
        marge avant ou après l'élément (selon sa position).
        
        De fait cette méthode n'a quasiment aucun intérêt en utilisation "passive" du 
        modelizer.
        
        :type obj: object
        :param obj: Objet auquel doit être imposé les marges
        
        :type margin: tuple
        :param margin: (optional) Tuple ou liste d'exactement quatres entiers 
                       représentant respectivement les marges haut, droite, bas, 
                       gauche.
        
        :type passive: bool
        :param passive: (optional) Permet d'activer le mode passif malgré l'option 
                        spécifiée à l'instanciation du modelizer.
        
        :rtype: object
        :return: L'objet exact spécifié.
        """
        if not margin:
            margin = (0, 0, 0, 0)
        top, right, bottom, left = margin
        
        if top > 0:
            self._active_return( Spacer(1, top), passive=passive )
        
        if isinstance(obj, list) or isinstance(obj, tuple):
            for item in obj:
                self._active_return( item, passive=passive )
        else:
            self._active_return( obj, passive=passive )
        
        if bottom > 0:
            self._active_return( Spacer(1, bottom), passive=passive )
        
        return obj

    def P(self, content, passive=False, **kwargs):
        """
        Élément d'un paragraphe
        
        C'est la base d'une majorité d'éléments du modelizer.
        
        :type content: string
        :param content: Texte
        
        :type passive: bool
        :param passive: (optional) Permet d'activer le mode passif malgré l'option 
                        spécifiée à l'instanciation du modelizer.
        
        :type kwargs: various
        :param kwargs: Arguments nommés représentant les options de mise en forme. 
                       Les arguments supportés sont :
                       
                       * @padding: None ou bien toujours un tuple de 4 éléments (top, right, bottom, left);
                       * @border_size: int;
                       * @border_color: `reportlab.lib.colors`;
                       * @background: `reportlab.lib.colors`;
        
        :rtype: object `reportlab.platypus.Paragraph`
        :return: Objet du paragraphe créé
        """
        custom_style = copy.deepcopy(self.style)
        _force_wedge = False
        margin = None
        if 'margin' in kwargs:
            margin = kwargs['margin']
            del kwargs['margin']
        if 'padding' in kwargs:
            custom_style.borderPadding = kwargs['padding']
            custom_style.spaceBefore = kwargs['padding'][0]
            custom_style.spaceAfter = kwargs['padding'][2]
            custom_style.leftIndent = kwargs['padding'][3]
            custom_style.rightIndent = kwargs['padding'][1]
            _force_wedge = True
            del kwargs['padding']
        if 'bullet' in kwargs:
            custom_style.bulletFontSize = kwargs.get('font_size', 12)
            custom_style.bulletIndent = custom_style.bulletFontSize+5
            custom_style.leftIndent = (custom_style.bulletFontSize+5)*2
            custom_style.allowWidows = 1
            custom_style.bulletFontName = 'Symbol'
            content = '<bullet>\xe2\x80\xa2</bullet>'+content
            del kwargs['bullet']
        if 'border_size' in kwargs:
            custom_style.borderWidth = kwargs['border_size']
            del kwargs['border_size']
        if 'border_color' in kwargs:
            custom_style.borderColor = kwargs['border_color']
            del kwargs['border_color']
        if 'background' in kwargs:
            custom_style.backColor = kwargs['background']
            del kwargs['background']
        
        obj = Paragraph(self.para_format(content, **kwargs), custom_style)
        self.MARGIN(obj, margin=margin, passive=passive)
        
        if _force_wedge:
            self._active_return( Spacer(1, 1), passive=passive )
        
        return obj
    
    def HEADING(self, content, size=22, bold=True, italic=False, line_height=24, padding=(0.2*inch, 0, 0.2*inch, 0), align="center", **kwargs):
        """
        Élément d'un titre
        
        :type content: string
        :param content: Texte
        
        :type size: int
        :param size: (optional) Taille de la police utilisée. 22 unités par défaut.
        
        :type bold: bool
        :param bold: (optional) Indique si le titre doit être mis complètement en gras. 
                     Activé par défaut.
        
        :type italic: bool
        :param italic: (optional) Indique si le titre doit être mis complètement en 
                       italique. Activé par défaut.
        
        :type line_height: int
        :param line_height: (optional) Hauteur de ligne du texte. 24 unités par défaut 
                            (en concordance avec la taille par défaut).
        
        :type padding: tuple
        :param padding: (optional) Tuple ou liste d'exactement quatres entiers 
                       représentant respectivement les marges intérieures haut, droite, 
                       bas, gauche.
        
        :type align: string
        :param align: (optional) Type d'alignement du texte, 'left', 'center' ou 'right'. 
                      Centré par défaut.
        
        :type kwargs: various
        :param kwargs: Arguments nommés supplémentaires représentant des options de mise 
                       en forme utilisé par le paragraphe.
        
        :rtype: object `reportlab.platypus.Paragraph`
        :return: Objet du titre (représenté par un objet de paragraphe mis en forme 
                 spéciquement).
        """
        if bold:
            content = self.STRONG(content)
        if italic:
            content = self.EMPHASE(content)
        return self.P(content, size=size, line_height=line_height, align=align, padding=padding, **kwargs)
    
    def H1(self, content, size=22, bold=True, italic=False, line_height=24, padding=(0.2*inch, 0, 0.2*inch, 0), align="center", **kwargs):
        """
        Titre de niveau 1
        
        Signature identique à `HTMLInterface.HEADING` et attends les mêmes arguments. 
        Et l'alignement est à gauche.
        """
        return self.HEADING(content, size=size, bold=bold, italic=italic, line_height=line_height, padding=padding, align=align, **kwargs)

    def H2(self, content, size=20, bold=True, italic=False, line_height=22, padding=(0.1*inch, 0, 0.1*inch, 0), align="left", **kwargs):
        """
        Titre de niveau 2
        
        Signature identique à `HTMLInterface.HEADING` et attends les mêmes arguments en 
        abaissant juste les dimensions de polices. Et l'alignement est à gauche.
        """
        return self.HEADING(content, size=size, bold=bold, italic=italic, line_height=line_height, padding=padding, align=align, **kwargs)

    def H3(self, content, size=18, bold=True, italic=False, line_height=20, padding=(0.1*inch, 0, 0.1*inch, 0), align="left", **kwargs):
        """
        Titre de niveau 3
        
        Signature identique à `HTMLInterface.HEADING` et attends les mêmes arguments en 
        abaissant juste les dimensions de polices. Et l'alignement est à gauche.
        """
        return self.HEADING(content, size=size, bold=bold, italic=italic, line_height=line_height, padding=padding, align=align, **kwargs)

    def H4(self, content, size=16, bold=True, italic=False, line_height=18, padding=(0.1*inch, 0, 0.1*inch, 0), align="left", **kwargs):
        """
        Titre de niveau 4
        
        Signature identique à `HTMLInterface.HEADING` et attends les mêmes arguments en 
        abaissant juste les dimensions de polices. Et l'alignement est à gauche.
        """
        return self.HEADING(content, size=size, bold=bold, italic=italic, line_height=line_height, padding=padding, align=align, **kwargs)

    def IMG(self, path, width=None, height=None, kind='direct', margin=None, align="center", passive=False):
        """
        Image
        
        :type path: string
        :param path: Chemin de l'image à récupérer pour l'inclure au document. Il est 
                     toujours joint au préfixe ``BaseModelizer.medias_path``.
        
        :type width: int
        :param width: (optional) Largeur de l'image. Vide par défaut, donc automatiquement 
                      récupéré d'après sa dimension originale et sa proportion.
        
        :type height: int
        :param width: (optional) Hauteur de l'image. Vide par défaut, donc automatiquement 
                      récupéré d'après sa dimension originale et sa proportion.
        
        :type kind: string
        :param kind: (optional) Type de proportionnement de l'image. Il doit toujours 
                     être "direct" si @width et @height sont None, sinon "proportional" 
                     peut être utilisé. Par défaut le type "direct" est utilisé.
        
        :type margin: tuple
        :param margin: (optional) Tuple ou liste d'exactement quatres entiers 
                       représentant respectivement les marges intérieures haut, droite, 
                       bas, gauche. (Les marges horizontales ne sont pas implémentés). 
                       Vide par défaut
        
        :type align: string
        :param align: (optional) Type d'alignement de l'image, 'left', 'center' ou 'right'. 
                      Centré par défaut.
        
        :type passive: bool
        :param passive: (optional) Permet d'activer le mode passif malgré l'option 
                        spécifiée à l'instanciation du modelizer.
        
        :rtype: object `reportlab.platypus.Image`
        :return: Objet de l'image.
        """
        path = os.path.join(self.medias_path, path)
        
        obj = Image(path, width, height, kind=kind)
        obj.hAlign = align.upper()
        
        return self.MARGIN(obj, margin=margin, passive=passive)

    def UL(self, items, margin=(0.1*inch, 0, 0.1*inch, 0), passive=False, **kwargs):
        """
        Liste à puces
        
        Pour l'instant, tout les items sont formatés par les kwargs donnés à la liste 
        sauf margin qui est absorbé et utilisé pour la liste et non les éléments.
        
        Contrairement à HTML, la liste n'est que "virtuelle", elle n'existe pas comme un 
        élément à part entière et renvoi uniquement sa liste d'éléments (ses lignes).
        
        L'intérêt de cette méthode est surtout de gérer une mise en forme commune (via 
        les kwargs) de toute les lignes et d'imposer des marges extérieurs autour de ce 
        lot de ligne.
        
        :type items: list
        :param items: Liste des lignes de texte de la liste à puce, chaque élément sera 
                      un élément de la liste. Chaque élément utilise les options de mise 
                      en forme fournis dans les 'kwargs' qui sont ceux supportés par les 
                      paragraphes.
        
        :type margin: tuple
        :param margin: (optional) Tuple ou liste d'exactement quatres entiers 
                       représentant respectivement les marges intérieures haut, droite, 
                       bas, gauche. (Les marges horizontales ne sont pas implémentés). 
                       Vide par défaut
        
        :type passive: bool
        :param passive: (optional) Permet d'activer le mode passif malgré l'option 
                        spécifiée à l'instanciation du modelizer.
        
        :type kwargs: various
        :param kwargs: Arguments nommés supplémentaires représentant des options de mise 
                       en forme utilisé par le paragraphe.
        
        :rtype: list
        :return: Liste des éléments de la liste à puce.
        """
        obj = [self.LI(item, **kwargs) for item in items]
        
        self.MARGIN(obj, margin=margin, passive=passive)
        
        return obj

    def LI(self, content, **kwargs):
        """
        Élément d'une liste à puces
        
        :type content: string
        :param content: Texte
        
        :type kwargs: various
        :param kwargs: Arguments nommés supplémentaires représentant des options de mise 
                       en forme utilisé par le paragraphe.
        
        :rtype: object `reportlab.platypus.Paragraph`
        :return: Objet de la ligne (représentée par un objet de paragraphe mis en forme 
                 spéciquement) indenté par une puce.
        """
        kwargs['bullet'] = True
        return self.P(content, passive=True, **kwargs)

    def TABLE(self, header_rows=[], body_row=[], col_sizing='auto', cell_styles=[], passive=False):
        """
        Élément d'un tableau de base pour des données tabulés
        
        WARNING: Pour l'instant c'est un peu foireux, nécessite encore pas mal de boulot 
                 de conception sur l'approche pour les tableaux.
                 
        :type header_rows: list
        :param header_rows: (optional) Cellule d'entêtes (comme des <th/>). Vide par 
                            défaut.
        
        :type body_row: list
        :param body_row: (optional) Liste des lignes du tableau. Chaque ligne est une 
                         liste d'éléments représentant une cellule. En général du texte, 
                         ou bien un objet paragraphe, voire un string vide pour certains 
                         cas (comme les cellules nécessaires à une fusion).
        
        :type col_sizing: string or list
        :param col_sizing: (optional) Soit une liste qui spécifie la dimension de chaque 
                           colonne du tableau. Soit un string spécifiant un 
                           type de dimensionnement automatique : 
                           
                           * auto: ne spécifie aucune largeur de colonne, Platypus se débrouille tout seul;
                           * *proportional: Calcul une largeur identique pour toute les colonnes;
        
        :type cell_styles: list
        :param cell_styles: (optional) Liste de tuples des options de styles de cellules 
                            (l'équivalent de qu'attends l'argument ``style`` de 
                            ``Platypus.Table``). Vide par défaut donc aucun style.
        
        :type passive: bool
        :param passive: (optional) Permet d'activer le mode passif malgré l'option 
                        spécifiée à l'instanciation du modelizer.
        
        :rtype: object `reportlab.platypus.Table`
        :return: Objet du tableau.
        """
        cell_styles = []
        header_rows = [header_rows]
        content_rows = header_rows+body_row
        
        # Nombre maximum de cellules par ligne
        max_cols = max([len(item) for item in content_rows])
        #print "max_cols: ", max_cols
        
        # Calcul des largeurs de colonnes
        col_sizes = None
        if isinstance(col_sizing, list) or isinstance(col_sizing, tuple):
            col_sizes = col_sizing
        elif col_sizing == 'proportional':
            width = 100/max_cols
            col_sizes = ["%s%%"%width for i in range(0, max_cols)]
        #print "col_sizes: ", col_sizes
        
        # TODO: * combler les trous du cellules des lignes en leur rajoutant à la fin le 
        #       * nombre de cellules manquantes
        #       * en même temps créer un registre des span nécessaires (aux trous 
        #         uniquement, pas d'autres déductions automatiques)
        table = Table(content_rows, col_sizes, style=cell_styles)
        
        return self._active_return( table, passive=passive )
