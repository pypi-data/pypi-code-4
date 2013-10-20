# -*- coding: utf-8 -*-
"""
Éléments graphiques de base

TODO: * GridDrawer: Bug sur les épaisseurs de bordure > 1 à cause du bug d'épaisseur 
        sur "ImageDraw.line()", contourner avec une technique tel que celle 
        de "TileDrawer";
      * TileTemplateRegistry: Système de cache interne optional;
        
--------
Requiert
--------

    * `Python Imaging Library (PIL) <http://www.pythonware.com/products/pil/index.htm>`_ en version >= 1.1.6;

------------------------
Options de mise en forme
------------------------

La majorité de ces options sont identiques à celles attendus par PIL, consultez sa 
documentation pour plus de détails sur certaines options :

* Les couleurs : (couleur de police, de bordure, de fond) sont soit une chaine de texte 
  donnant le code hexadécimal de la couleur (ex: #f0f0f0), soit un tuple de trois à 
  quatres arguments donnant les indices (de 0 à 255) RGB pour les trois premiers, le 
  dernier argument optional indique le niveau d'opacité (0=totalement tranparent);
* Les Polices : Les chemins de polices TrueType définissent le chemin vers un fichier du type 
  ``*.ttf`` que PIL utilisera, par défaut aucune police TTF n'est spécifiée, ce sera 
  donc celle fourni par défaut dans PIL. Cette dernière semble pose des problèmes avec 
  les textes en unicode.

Liste des options communes
..........................

margin
    * Type: tuple
    * Tuple spécifiant respectivement les marges de gauche et en haut 
      à imposer comme base de coordonnées de départ du coin haut gauche de 
      l'objet.
padding
    * Type: tuple
    * Tuple spécifiant respectivement les marges intérieures de gauche 
      et en haut à imposer comme base de positionnement du texte dans 
      l'objet.
font_ttf
    * Type: string
    * Chemin vers un fichier de police TrueType. Par 
      défaut, aucune police n'est spécifiée et PIL utilise une police 
      par défaut. Attention cette dernière pose problème avec les 
      textes en unicode.
font_size
    * Type: int
    * Taille de la police.
font_align
    * Type: string
    * Type d'alignement du texte dans le rectangle, il peut être à 
      gauche (``left``), à droite (``right``) ou centré 
      (``center``). À gauche par défaut.
font_color
    * Type: tuple or string
    * Couleur du texte.
fill
    * Type: tuple or string
    * Couleur de remplissage dans l'objet
background
    * Type: tuple or string
    * Couleur de remplissage autour de l'objet
border_width
    * Type: int
    * Épaisseur des bordures ou traits de l'objet.
border_color
    * Type: tuple or string
    * Couleur des bordures ou traits de l'objet.
sides
    * Type: tuple
    * Tuple contenant les côtés de l'objet à dessiner. Les noms clés 
      des cotés ne figurant pas dans ce tuple ne seront pas dessinés mais 
      restent comptabilisés dans le calcul des dimensions. Les noms clés 
      possibles sont 'top', 'right', 'bottom', 'left'.
round_radius
    * Type: int
    * Longueur des cotés du carré occupé par l'arrondi, par exemple un radius 
      de 5 donne un carré de 5x5.
round_corners
    * Type: tuple or None
    * Option servant à activer les arrondis, par défaut ``None`` donc ils sont 
      désactivés. Indiquer une liste de noms clés des coins à arrondir les actives, les 
      noms clés sont les suivants 'top-left', 'top-right', 'bottom-left', 
      'bottom-right'.
round_outfill
    * Type: tuple or None
    * Couleur de sur-impression qui sert à masquer les coins de l'objet à arrondir pour 
      donner cet effet. Par défaut transparent et donc les arrondis ne servent presque à 
      rien, c'est pourquoi il est important de le remplir convenablement.
"""
import Image, ImageDraw, ImageFont

DEFAULT_TILE_SET = {
    'default': {
        'fill':"white",
        'border_color':"black",
    },
    'red': {
        'fill': (253, 73, 73, 255),
        'border_color': (181, 53, 53, 255),
    },
    'orange': {
        'fill': (255, 171, 39, 255),
        'border_color': (203, 137, 31, 255),
    },
    'blue': {
        'fill': (71, 184, 255, 255),
        'border_color': (51, 132, 184, 255),
    },
    'yellow': {
        'fill': (253, 255, 69, 255),
        'border_color': (178, 177, 75, 255),
    },
    'green': {
        'fill': (159, 255, 76, 255),
        'border_color': (110, 186, 143, 255),
    },
    'grey': {
        'fill': (230, 230, 230, 255),
        'border_color': (191, 191, 191, 255),
    },
    'violet': {
        'fill': (215, 215, 248, 255),
        'border_color': (148, 148, 176, 255),
    },
    'turquoise': {
        'fill': (129, 246, 217, 255),
        'border_color': (105, 200, 177, 255),
    },
}

class RoundCornerDrawer(object):
    """
    Imposition d'arrondis sur les coins d'un rectangle
    
    Les arrondis sont ajoutés par simple sur-impression et le fond externe (outfill) 
    sert à masquer les coins, donc il ne doit donc pas être transparent. Le 
    fond interne est utilisé "normalement" donc il peut être rempli ou transparent, ça 
    ne pose aucun soucis, si ce n'est qu'il peut masquer des objets (selon la dimension 
    de l'arrondi déterminée par le ``radius``, c'est pourquoi les arrondis doivent en 
    général être imposés avant d'autre objets à contenir dans le rectangle (comme du 
    texte).
    
    En général toujours, pour une utilisation avec une textbox ou tout autre objet qui 
    en contiendra un autre, le padding horizontal de cet objet doit correspondre au 
    radius souhaité (ou vice-versa).
    """
    def __init__(self, size, radius, opts={}):
        """
        :type size: tuple
        :param size: (optional) Dimensions du rectangle à former
        
        :type radius: int
        :param radius: Longueur des cotés du carré occupé par l'arrondi, par exemple un radius 
                       de 5 donne un carré de 5x5.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "margin", "background", fill", 
                     "border_color", "border_width".
        """
        self.size = size
        self.radius = radius
        
        self.opts = {
            'margin': (0, 0),
            'background': (0, 0, 0, 0),
            'fill': (0, 0, 0, 0),
            'border_color': (0, 0, 0, 255),
            'border_width': 1,
        }
        self.opts.update(opts)
        
        self._get_coords()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<RoundCornerDrawer Size%s, Radius(%s)>" % (str(self.size), self.radius)
        
    def _get_coords(self):
        """
        Coordonées de base du rectangle
        """
        self.corner_coords = {
            'top-left': (self.opts['margin'], 0),
            'top-right': ( ((self.size[0]+self.opts['margin'][0])-self.radius, self.opts['margin'][1]), 270),
            'bottom-left': ( (self.opts['margin'][0], (self.size[1]+self.opts['margin'][1])-self.radius), 90),
            'bottom-right': ( ((self.size[0]+self.opts['margin'][0])-self.radius, (self.size[1]+self.opts['margin'][1])-self.radius), 180),
        }
        self.border_modifier = {
            'top-left': (1, 1),
            'top-right': (-1, 1),
            'bottom-left': (1, -1),
            'bottom-right': (-1, -1),
        }
        
    def move_coords_for_angle(self, i, key, coords):
        """
        Calcul des coordonnées de destination d'un type de coin selon un indice de 
        déplacement
        
        Cela permet de reproduire un coin et le décaler pour simuler les bordures 
        par répétition.
        
        :type i: int
        :param i: indice de déplacement supplémentaire au coordonnées
        
        :type key: string
        :param key: Nom clé du coin à déplacer
        
        :type coords: tuple
        :param coords: Tuple des coordonnées de destination
        
        :rtype: tuple
        :return: Tuple des coordonnées de destinations à appliquer
        """
        if i>0:
            new_coords = list(coords)
            modifier = self.border_modifier[key]
            return (coords[0]+(modifier[0]*i), coords[1]+(modifier[1]*i))
            
        return coords
        
    def draw(self, imageObject=None, corners=('top-left', 'top-right', 'bottom-left', 'bottom-right')):
        """
        Dessine et assemble les éléments
        
        :type imageObject: object `Image`
        :param imageObject: (optional) Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :type corners: tuple or None
        :param corners: (optional) Option servant à activer les arrondis, par défaut 
                        ``None`` donc ils sont désactivés. Indiquer une liste de noms 
                        clés des coins à arrondir les actives, les noms clés sont les 
                        suivants 'top-left', 'top-right', 'bottom-left', 'bottom-right'.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if not imageObject:
            imageObject = Image.new('RGBA', self.size, (0, 0, 0, 0))
        
        # Arrondi de première couche
        draw = ImageDraw.Draw(imageObject)
        corner_out = Image.new('RGBA', (self.radius, self.radius), self.opts['background'])
        draw = ImageDraw.Draw(corner_out)
        draw.pieslice((0, 0, self.radius*2, self.radius*2), 180, 270, fill=self.opts['fill'], outline=self.opts['border_color'])
        # Arrondi des couches secondaires pour des épaisseurs de bordure supérieur à 1
        draw = ImageDraw.Draw(imageObject)
        corner_in = Image.new('RGBA', (self.radius, self.radius), (0, 0, 0, 0))
        draw = ImageDraw.Draw(corner_in)
        draw.pieslice((0, 0, self.radius*2, self.radius*2), 180, 270, fill=self.opts['fill'], outline=self.opts['border_color'])
        
        # Réutilise l'arrondi en le pivotant selon chaque coin
        for corner_key in [i for i in corners if i in self.corner_coords]:
            corner_coords = self.corner_coords[corner_key]
            for i in range(0, self.opts['border_width']):
                coords = self.move_coords_for_angle(i, corner_key, corner_coords[0])
                if i == 0:
                    imageObject.paste(corner_out.rotate(corner_coords[1]), coords, corner_out.rotate(corner_coords[1]))
                elif i > 0:
                    imageObject.paste(corner_in.rotate(corner_coords[1]), coords, corner_in.rotate(corner_coords[1]))
        
        return imageObject

class BorderDrawer(object):
    """
    Objet d'une bordure de rectangle
    """
    def __init__(self, size, opts={}):
        """
        :type size: tuple
        :param size: Dimensions du rectangle à former, le tuple est sous la forme 
                     ``(largeur, hauteur)``.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "margin", "border_color", "border_width", 
                     "sides", round_corners", "round_radius", "round_outfill".
        """
        self.size = size
        
        self.opts = {
            'margin': (0, 0),
            'border_color': (0, 0, 0, 255),
            'border_width': 1,
            'sides': ('top', 'right', 'bottom', 'left'),
            'round_corners': None,
            'round_radius': 5,
            'round_outfill': (0, 0, 0, 0),
        }
        self.opts.update(opts)
        
        self._get_coords()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<BorderDrawer Size%s; Margin%s; Border(%s)>" % (str(self.size), str(self.opts['margin']), self.opts['border_width'])
        
    def _get_coords(self):
        """
        Coordonées de base du rectangle
        """
        self.x_min = self.opts['margin'][0]
        self.y_min = self.opts['margin'][1]
        self.x_max = (self.x_min+self.size[0])-1
        self.y_max = (self.y_min+self.size[1])-1

    def round(self, imageObject):
        """
        Applique les arrondis de coins souhaités
        
        :type imageObject: object `Image`
        :param imageObject: Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if self.opts['round_corners'] and self.opts['round_radius']>0:
            rcd = RoundCornerDrawer(self.size, self.opts['round_radius'], opts={
                'margin': self.opts['margin'],
                'background': self.opts['round_outfill'],
                'border_width': self.opts['border_width'],
                'border_color': self.opts['border_color'],
            })
            rcd.draw(imageObject, corners=self.opts['round_corners'])

        return imageObject
        
    def draw(self, imageObject=None):
        """
        Dessine et assemble les éléments
        
        :type imageObject: object `Image`
        :param imageObject: (optional) Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if not imageObject:
            imageObject = Image.new('RGBA', self.size, (0, 0, 0, 0))
        
        draw = ImageDraw.Draw(imageObject)
        
        i = 0
        # Redessine les traits pour chaque épaisseur de bordure
        # C'est un workaround du bug de l'utilisation de l'argument ``width`` de 
        # ``draw.line()`` qui créé des épaisseurs approximatives
        #foo = ['red','blue','green','black']
        for item in range(0, self.opts['border_width']):
            if 'left' in self.opts['sides']:
                # Gauche x + n
                draw.line(((self.x_min+item, self.y_min), (self.x_min+item, self.y_max)), fill=self.opts['border_color'])
            if 'right' in self.opts['sides']:
                # Droite x - n
                draw.line(((self.x_max-item, self.y_min), (self.x_max-item, self.y_max)), fill=self.opts['border_color'])
            if 'top' in self.opts['sides']:
                # Haut y + n
                draw.line(((self.x_min, self.y_min+item), (self.x_max, self.y_min+item)), fill=self.opts['border_color'])
            if 'bottom' in self.opts['sides']:
                # Bas y - n
                draw.line(((self.x_min, self.y_max-item), (self.x_max, self.y_max-item)), fill=self.opts['border_color'])
                i += 1
        
        return self.round(imageObject)
 
class TileDrawer(object):
    """
    Objet d'une tuile
    """
    def __init__(self, size=(50, 30), opts={}):
        """
        :type size: tuple
        :param size: Dimensions du rectangle à former, le tuple est sous la forme 
                     ``(largeur, hauteur)``.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "margin", "fill", "border_color", "border_width", 
                     "sides", round_corners", "round_radius", "round_outfill".
        """
        self.size = size
        self.tile_width, self.tile_height = self.size
        
        self.opts = {
            'margin': (0, 0),
            'fill': (255, 255, 255, 255),
            'border_width': 1,
            'border_color': (0, 0, 0, 255),
            'sides': ('top', 'right', 'bottom', 'left'),
            'round_corners': None,
            'round_radius': 5,
            'round_outfill': (0, 0, 0, 0),
        }
        self.opts.update(opts)
        
        self._get_coords()

    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<TileDrawer Size%s; Start%s; Start%s; End%s>" % (str(self.size), str(self.opts['margin']), str(self.start_point), str(self.end_point))

    def _get_coords(self):
        """
        Calcul les coordonnées des points de dessin du cadre complet
        """
        self.start_point = (self.opts['margin'][0], self.opts['margin'][1])
        # Les points de fin commencent à "n-border_width" vu que les points déterminent 
        # le coin gauche du pixel ou est dessiné le trait de l'épaisseur de bordure
        self.end_point = ((self.opts['margin'][0]+self.tile_width)-1, (self.opts['margin'][1]+self.tile_height)-1)

    def round(self, imageObject):
        """
        Applique les arrondis de coins souhaités
        
        :type imageObject: object `Image`
        :param imageObject: (optional) Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if self.opts['round_corners'] and self.opts['round_radius']>0:
            rcd = RoundCornerDrawer(self.size, self.opts['round_radius'], opts={
                'margin': self.opts['margin'],
                'background': self.opts['round_outfill'],
                'fill': self.opts['fill'],
                'border_width': self.opts['border_width'],
                'border_color': self.opts['border_color'],
            })
            rcd.draw(imageObject, corners=self.opts['round_corners'])

        return imageObject

    def draw(self, imageObject=None):
        """
        Dessine et assemble les éléments
        
        :type imageObject: object `Image`
        :param imageObject: (optional) Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if not imageObject:
            imageObject = Image.new('RGBA', self.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(imageObject)
        
        # Rectangle de fond servant à dessiner les contours
        draw.rectangle([ self.start_point, self.end_point ], fill=self.opts['fill'])
        
        # Rectangle de masque par dessus le rectangle de fond, dessiné uniquement 
        # si l'épaisseur de bordure > 1, sinon le premier rectangle est simplement rempli 
        # avec la couleur de fond et ça suffit
        if self.opts['border_width']>0:
            borderObject = BorderDrawer(self.size, opts={
                'margin': self.opts['margin'],
                'border_color': self.opts['border_color'],
                'border_width': self.opts['border_width'],
                'sides': self.opts['sides'],
            })
            borderObject.draw(imageObject)
        
        return self.round(imageObject)

class GridDrawer(object):
    """
    Objet d'une grille
    """
    def __init__(self, size, tile_size, opts={}):
        """
        :type size: tuple
        :param size: Dimensions de l'image à retourner par ``self.draw()`` si il doit la créer.
        
        :type tile_size: tuple
        :param tile_size: Dimensions des tuiles formant la grille, toute les tuiles ayant 
                          les mêmes dimensions.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "margin", "background", "border_color", 
                     "border_width", "round_corners", "round_radius", "round_outfill".
        """
        self.size = size
        self.tile_size = tile_size
        
        self.opts = {
            'margin': (0, 0),
            'border_color': (191, 191, 191, 255),
            'border_width': 1,
            'background': (0, 0, 0, 0),
            'round_corners': None,
            'round_radius': 5,
            'round_outfill': (0, 0, 0, 0),
        }
        self.opts.update(opts)
        
        self._get_coords()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<GridDrawer Size%s; Margin%s; Tile%s>" % (str(self.size), str(self.opts['margin']), str(self.tile_size))
        
    def _get_coords(self):
        self.vertical_lines_coords = self._get_vertical_lines()
        self.horizontal_lines_coords = self._get_horizontal_lines()
        
    def _get_vertical_lines(self):
        """
        Coordonnées des lignes verticales
        
        :rtype: list
        :return: Liste de tuple de coordonnées de lignes sous la forme 
                 ``(x, y), (x, y))``, le premier élément étant le point de départ et 
                 l'autre le point d'arrêt.
        """
        start = self.opts['margin'][0]
        width = self.opts['margin'][0]+self.size[0]
        step = self.tile_size[0]-1
        vertical_start_points = range(start, width, step)
        
        vertical_lines_coords = []
        for pt in vertical_start_points:
            vertical_lines_coords.append(((pt, self.opts['margin'][1]), (pt, self.size[1]+self.opts['margin'][1]-1)))
        return vertical_lines_coords

    def _get_horizontal_lines(self):
        """
        Coordonnées des lignes horizontales
        
        :rtype: list
        :return: Liste de tuple de coordonnées de lignes sous la forme 
                 ``(x, y), (x, y))``, le premier élément étant le point de départ et 
                 l'autre le point d'arrêt.
        """
        start = self.opts['margin'][1]
        width = self.opts['margin'][1]+self.size[1]
        step = self.tile_size[1]-1
        horizontal_start_points = range(start, width, step)
        
        horizontal_lines_coords = []
        for pt in horizontal_start_points:
            horizontal_lines_coords.append(((self.opts['margin'][0], pt), (self.size[0]+self.opts['margin'][0]-1, pt)))
        return horizontal_lines_coords

    def round(self, imageObject):
        """
        Applique les arrondis de coins souhaités
        """
        if self.opts['round_corners'] and self.opts['round_radius']>0:
            rcd = RoundCornerDrawer(self.size, self.opts['round_radius'], opts={
                'margin': self.opts['margin'],
                'background': self.opts['round_outfill'],
                'fill': self.opts['background'],
                'border_width': self.opts['border_width'],
                'border_color': self.opts['border_color'],
            })
            rcd.draw(imageObject, corners=self.opts['round_corners'])

        return imageObject

    def draw(self, imageObject=None):
        """
        Dessine et assemble les éléments
        
        :type imageObject: object `Image`
        :param imageObject: (optional) Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if not imageObject:
            imageObject = Image.new('RGBA', self.size, self.opts['background'])
        
        draw = ImageDraw.Draw(imageObject)
        
        # Dessine la grille complète
        for points in self.vertical_lines_coords:
            draw.line(points, fill=self.opts['border_color'], width=self.opts['border_width'])
        for points in self.horizontal_lines_coords:
            draw.line(points, fill=self.opts['border_color'], width=self.opts['border_width'])
        
        return self.round(imageObject)
 
class TextBoxDrawer(object):
    """
    Objet d'une boîte de texte
    
    Permet de mettre du texte dans un rectangle.
    
    Prévu uniquement pour du texte simple sur une ligne (pas de gestion de multi-lignes 
    pour les textes longs)
    """
    def __init__(self, text, size=(0, 0), opts={}):
        """
        :type text: string
        :param text: Texte servant à remplir le rectangle.
        
        :type size: tuple
        :param size: (optional) Dimensions du rectangle à former, le tuple est sous la 
                     forme ``(largeur, hauteur)``. Si la dimension n'est pas spécifiée 
                     elle est automatiquement calculée à partir de la largeur requise 
                     pour la longueur du texte plus les padding.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "margin", "padding", "font_color", 
                     "font_ttf", "font_size", "font_align", "fill", 
                     "border_width", "border_color", "sides", "round_corners", 
                     "round_radius", "round_outfill".
        """
        self.text = text
        self.size = size
        
        self.opts = {
            'margin': (0, 0),
            'padding': (0, 0),
            'fill': (255, 255, 255, 255),
            'border_width': 1,
            'border_color': (0, 0, 0, 255),
            'sides': ('top', 'right', 'bottom', 'left'),
            'font_color': (0, 0, 0, 255),
            'font_ttf': None,
            'font_size': 14,
            'font_align': "left",
            'round_corners': None,
            'round_radius': 5,
            'round_outfill': (0, 0, 0, 0),
        }
        self.opts.update(opts)
        
        self._get_font(self.opts['font_ttf'], self.opts['font_size'])
        self._get_coords()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return self.__unicode__().encode('UTF8')
    
    def __unicode__(self):
        return "<TextBoxDrawer Size%s; BoxSize%s; Align(%s); Margin%s; Padding%s; Border(%s) TextSize%s> %s" % (str(self.size), str(self.box_size), self.opts['font_align'], str(self.opts['margin']), str(self.opts['padding']), self.opts['border_width'], str(self.text_size), self.text)
        
    def _get_font(self, font_ttf=None, font_size=14):
        """
        Charge le fichier truetype spécifié sinon la police par défaut
        
        La taille spécifiée n'est pas appliquable sur une police par défaut
        
        :type font_ttf: string
        :param font_ttf: (optionel) Chemin vers un fichier de police TrueType. Par 
                         défaut, aucune police n'est spécifiée et PIL utilise une police 
                         par défaut. Attention cette dernière pose problème avec les 
                         textes en unicode.
        
        :type font_size: int
        :param font_size: Taille de la police.
        """
        if not font_ttf:
            self.font = ImageFont.load_default()
        else:
            self.font = ImageFont.truetype(font_ttf, font_size)
        
    def _get_coords(self):
        """
        Coordonées des éléments
        """
        self.text_size = self.font.getsize(self.text)
        self.box_size = self.size
        if not self.size or self.size == (0, 0):
            self.size = self.text_size
            self.box_size = (self.size[0]+(self.opts['padding'][0]*2), self.size[1]+(self.opts['padding'][1]*2))
        
        # Calcul des coordonnées du texte pour suivre l'alignement demandé
        if self.opts['font_align'] == 'right':
            self.text_coords = (self.opts['margin'][0]+(self.box_size[0]-self.text_size[0]-self.opts['padding'][0]), self.opts['padding'][1]+self.opts['margin'][1])
        elif self.opts['font_align'] == 'center':
            x_base = (self.box_size[0]-self.text_size[0])/2
            self.text_coords = (x_base+self.opts['margin'][0], self.opts['padding'][1]+self.opts['margin'][1])
        else:
            self.text_coords = (self.opts['padding'][0]+self.opts['margin'][0], self.opts['padding'][1]+self.opts['margin'][1])

    def round(self, imageObject):
        """
        Applique les arrondis de coins souhaités
        """
        if self.opts['round_corners'] and self.opts['round_radius']>0:
            rcd = RoundCornerDrawer(self.box_size, self.opts['round_radius'], opts={
                'margin': self.opts['margin'],
                'background': self.opts['round_outfill'],
                'fill': self.opts['fill'],
                'border_width': self.opts['border_width'],
                'border_color': self.opts['border_color'],
            })
            rcd.draw(imageObject, corners=self.opts['round_corners'])

        return imageObject
    
    def draw(self, imageObject=None):
        """
        Dessine et assemble les éléments
        
        :type imageObject: object `Image`
        :param imageObject: (optional) Object d'une image ouverte par *PIL*. Par défaut, 
                            si elle n'est pas spécifiée, une nouvelle image sera crée à 
                            la volée à partir des options liés (background, size) de 
                            l'objet si il en a.
        
        :rtype: object `Image`
        :return: L'objet de l'image contenant les éléments dessinés.
        """
        if not imageObject:
            imageObject = Image.new('RGBA', self.size, (0, 0, 0, 0))
        
        tileObject = TileDrawer(size=self.box_size, opts={
            'margin': self.opts['margin'],
            'fill': self.opts['fill'],
            'border_width': self.opts['border_width'],
            'border_color': self.opts['border_color'],
            'sides': self.opts['sides'],
        })
        tileObject.draw(imageObject)
        
        imageObject = self.round(imageObject)
        
        draw = ImageDraw.Draw(imageObject)
        
        draw.text(self.text_coords, self.text, font=self.font, fill=self.opts['font_color'])
        
        return imageObject

class TileTemplateRegistry(object):
    """
    Registre des "templates" d'options de mise en forme des tuiles
    """
    def __init__(self, default=DEFAULT_TILE_SET):
        """
        :type default: dict
        :param default: (optional) Dictionnaire des templates d'options de tuile, rangés 
                        par leur nom clé.
        """
        self.configs = default
    
    def set(self, configs):
        """
        Redéfinit complètement le registre
        
        :type configs: dict
        :param configs: Dictionnaire de templates d'options de tuile.
        """
        self.configs = configs
    
    def add(self, configs):
        """
        Ajoute de nouveau éléments au registre, si ils existent déja (d'après leur nom 
        clé) leur précédente valeur est écrasée.
        
        :type configs: dict
        :param configs: Dictionnaire d'options de tuile d'un nouveau template à ajouter 
                        (écrase son homologue de nom clé).
        """
        self.configs.update(configs)
    
    def get(self, key, opts={}):
        """
        Retourne simplement les options d'un template
        
        :type key: string
        :param key: Nom clé du template recherché.
        
        :type opts: dict
        :param opts: (optional) Dictionnaire d'options à écraser dans les options du 
                     template recherché.
        
        :rtype: dict
        :return: Dictionnaire d'options
        """
        kwargs = self.configs[key]
        kwargs.update(opts)
        return kwargs
    
    def draw(self, key, size, opts={}):
        """
        Dessine la tuile à partir des options du template demandé
        
        :type key: string
        :param key: Nom clé du template recherché.
        
        :type size: tuple
        :param size: Dimensions de la tuile, le tuple est sous la forme 
                     ``(largeur, hauteur)``.
        
        :type opts: dict
        :param opts: (optional) Dictionnaire d'options à écraser dans les options du 
                     template recherché.
        
        :rtype: object `Image`
        :return: Object de l'image de la tuile dessinée 
        """
        return TileDrawer(size, opts=self.get(key, opts=opts)).draw()
