# -*- coding: utf-8 -*-
"""
Objet de compositions à partir des éléments
"""
import Image, ImageDraw, ImageFont

from Sveetchies.gantt.png.elements import *

class MosaicComposer(object):
    """
    Objet d'une mosaique de tuiles
    
    À noter que les tuiles se chevauchent sur leur bordure droite et basse pour rendre un 
    effet visuel d'une grille.
    """
    def __init__(self, cols, rows, grid, size=(300, 100), tile_size=None, tile_merge=True, opts={}):
        """
        :type cols: int
        :param cols: Largeur maximum des colonnes (=~emplacements de tuiles).
        
        :type rows: int
        :param rows: Nombre de lignes de colonnes.
        
        :type grid: list
        :param grid: Liste des lignes d'emplacements de tuiles.
        
        :type size: tuple
        :param size: Dimension à appliquer, inutilisé si l'argument ``tile_size`` est 
                     spécifié. Sinon il sert à calculer automatiquement la dimension des 
                     tuiles requises pour remplir les dimensions indiqués. La dimension 
                     réelle de la mosaique ne sera pas exacte mais toujours un peu 
                     inférieur pour remplir sans dépasser.
        
        :type tile_size: tuple
        :param tile_size: Dimensions des tuiles formant la mosaique, toute les tuiles 
                          ayant les mêmes dimensions.
        
        :type tile_merge: boolean
        :param tile_merge: Si ``True`` indique que les cellules adjacentes fusionnent 
                           leurs bordures horizontales de sorte que des tuiles qui se 
                           suivent forment visuellement un rectangle entier. Si ``False`` 
                           toute les tuiles conservent leurs bordures horizontales. Cette 
                           option est activé par défaut.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "background", "border_width". À 
                     noter que "border_width" n'a pas ici vocation à un encadrement 
                     général, il stipule seulement la taille des bordures des tuiles et 
                     sert aussi aux calculs de leur positionnement.
        """
        self.cols = cols
        self.rows = rows
        self.grid = grid
        self.size = size
        self.tile_size = tile_size
        self.tile_merge = tile_merge
        
        self.opts = {
            'background': (0, 0, 0, 0),
            'border_width': 1,
        }
        self.opts.update(opts)
        
        self._get_coords()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<MosaicComposer Size%s; Cols(%s); Rows(%s); Tile%s; Offset%s>" % (str(self.size), self.cols, self.rows, str(self.tile_size), str(self.offset))

    def _get_coords(self):
        """
        Coordonées des éléments
        
        Si la dimension de tuile n'est pas spécifiée, elle est déterminée à partir du 
        nombre de colonnes et lignes qui doivent remplir au maximum l'espace alloué par 
        la dimension indiqué à l'instance et sans jamais le dépasser.
        
        Le calcul de la dimension réelle prends compte du chevauchement d'une épaisseur 
        de bordure qu'il y a entre les tuiles de la mosaique.
        """
        width, height = self.size
        
        if not self.tile_size:
            # On retire l'épaisseur de bordure de la taille de la grille pour tenir compte du 
            # fait qu'il y a une bordure de plus que de cellule, celle du bout de la ligne.
            real_width = width - self.opts['border_width']
            real_height = height - self.opts['border_width']
            self.tile_size = [width/self.cols, height/self.rows]
            # On vérifie combien de cellules ayant la taille calculée juste avant il 
            # faudrait pour remplir la grille avec la nouvelle taille. Si ce nombre est plus 
            # grand que celui fixé, on essaie avec une taille plus grande de 1 px.
            while real_width/self.tile_size[0] > self.cols :
                self.tile_size[0] += self.opts['border_width']
            while real_height/self.tile_size[1] > self.rows :
                self.tile_size[1] += self.opts['border_width']
        
        self.offset = ((self.tile_size[0]-self.opts['border_width'])*self.cols+self.opts['border_width'] , (self.tile_size[1]-self.opts['border_width'])*self.rows+self.opts['border_width'])

    def _get_tile_context(self, pos, context):
        """
        Détermine si la tuile est la première et/ou la dernière de sa série
        
        Par "série", on entends des tuiles qui se suivent sans emplacement vides entres 
        elles (mais autour).
        
        :type pos: int
        :param pos: Position dans le contexte
        
        :type context: list
        :param context: Contexte où retrouver la tuile
        
        :rtype: tuple
        :return: Retourne un tuple contenant deux arguments booléen respectivement :
                 * Celui pour indiquer que la tuile est la première de sa série
                 * Celui pour indique que la tuile est la dernière de sa série
        """
        first = last = True
        if self.tile_merge:
            if pos > 0 and context[pos-1] != None:
                first = False
            if pos+1 < len(context) and context[pos+1] != None:
                last = False
        return first, last

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
            imageObject = Image.new('RGBA', self.offset, self.opts['background'])
        
        tileregistry = TileTemplateRegistry()
        
        tile_sides = ['top', 'right', 'bottom', 'left']
        row = 0
        # Ouvre la grille complète
        for task_row in self.grid:
            col = 0
            # Traite toute les emplacements de chaque ligne
            for event in task_row:
                # Si l'emplacement n'est pas vide de tuile
                if event:
                    sides = tile_sides[:]
                    is_first, is_last = self._get_tile_context(col, task_row)
                    if not is_first:
                        sides.remove('left')
                    if not is_last:
                        sides.remove('right')
                    # Tuile à instancier par un template de tuile
                    asset = tileregistry.draw(event, size=self.tile_size, opts={
                        'border_width':self.opts['border_width'],
                        'sides': sides,
                    })
                    # Copie l'élément de la tuile dans l'image de la mosaique
                    pos_x = (self.tile_size[0]*col)-(1*col)
                    pos_y = (self.tile_size[1]*row)-(1*row)
                    imageObject.paste(asset, (pos_x, pos_y), asset)
                col += 1
            row += 1
        
        return imageObject

class ScheduleMosaicComposer(MosaicComposer):
    """
    Objet d'une mosaique de tâches d'un calendrier
    """
    def __init__(self, scheduleObject, size=(300, 100), tile_size=(10, 10), tile_merge=True, with_groups=False, opts={}):
        """
        :type scheduleObject: object ``Sveetchies.gantt.models.ScheduleModel``
        :param scheduleObject: Objet du calendrier qui détermine le nombre de colonnes, 
                               de lignes et la grille de données.
        
        :type size: tuple
        :param size: Dimension à appliquer, inutilisé si l'argument ``tile_size`` est 
                     spécifié. Sinon il sert à calculer automatiquement la dimension des 
                     tuiles requises pour remplir les dimensions indiqués. La dimension 
                     réelle de la mosaique ne sera pas exacte mais toujours un peu 
                     inférieur pour remplir sans dépasser.
        
        :type tile_size: tuple
        :param tile_size: Dimensions des tuiles formant la mosaique, toute les tuiles 
                          ayant les mêmes dimensions.
        
        :type tile_merge: boolean
        :param tile_merge: Si ``True`` indique que les cellules adjacentes fusionnent 
                           leurs bordures horizontales de sorte que des tuiles qui se 
                           suivent forment visuellement un rectangle entier. Si ``False`` 
                           toute les tuiles conservent leurs bordures horizontales. Cette 
                           option est activé par défaut.
        
        :type with_groups: boolean
        :param with_groups: Indique si le calendrier doit utiliser les groupes et les 
                            insérer dans la grille. Par défaut cette option est 
                            désactivée.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "background", "border_width".
        """
        self.scheduleObject = scheduleObject
        self.size = size
        self.tile_size = tile_size
        self.tile_merge = tile_merge
        self.with_groups = with_groups
        
        self.rows = len(self.scheduleObject.tasks)
        if self.with_groups:
            self.rows += len(self.scheduleObject.groups)
        self.cols = self.scheduleObject.width
        self.grid = self.scheduleObject.get_grid(with_groups=self.with_groups)
        
        self.opts = {
            'background': (0, 0, 0, 0),
            'border_width': 1,
        }
        self.opts.update(opts)
        
        self._get_coords()
        
    def __str__(self):
        return "<ScheduleMosaicComposer Size%s; Cols(%s); Rows(%s); Tile%s; Offset%s>" % (str(self.size), self.cols, self.rows, str(self.tile_size), str(self.offset))

class UnitLineComposer(object):
    """
    Objet d'une ligne de tuiles d'unités
    """
    def __init__(self, units, opts={}):
        """
        :type units: list
        :param units: Liste d'éléments de la ligne d'unités
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "margin", "padding", "font_ttf", "font_size", 
                     "font_align", "font_color", "fill", "background", "border_width", "border_color".
        """
        self.units = units
        
        self.opts = {
            'margin': (0, 0),
            'padding': (2, 2),
            'font_ttf': None,
            'font_size': 11,
            'font_align': "left",
            'font_color': (0, 0, 0, 255),
            'fill': (0, 0, 0, 0),
            'background': (0, 0, 0, 0),
            'border_width': 1,
            'border_color': (0, 0, 0, 255),
            'round_corners': None,
            'round_radius': 5,
            'round_outfill': (0, 0, 0, 0),
        }
        self.opts.update(opts)
        
        self._get_coords()
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "<UnitLineComposer Size%s; Cols(%s); Tile%s>" % (str(self.size), self.cols, str(self.tile_size))

    def _get_coords(self):
        """
        Coordonées des éléments
        """
        self.rows = 1
        self.cols = len(self.units)
        self.size = (0, 0)
        # Séléction de l'unité la plus large et récupère ses dimensions de tuiles pour 
        # les imposer comme référence
        max_unit = ''
        for u in self.units:
            if len(u) > len(max_unit):
                max_unit = u
        tbd = TextBoxDrawer(max_unit, opts={
            'border_width': self.opts['border_width'],
            'padding': self.opts['padding'],
            'font_ttf': self.opts['font_ttf'],
            'font_size': self.opts['font_size'],
        })
        self.tile_size = tbd.box_size
        
        # Calcul la dimension complète de l'image avec tout ses éléments
        width = ((self.tile_size[0]-self.opts['border_width'])*self.cols)+self.opts['border_width']
        height = ((self.tile_size[1]-self.opts['border_width'])*self.rows)+self.opts['border_width']
        self.size = (width, height)

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
                'fill': self.opts['fill'],
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
            imageObject = Image.new('RGBA', (self.opts['margin'][0]+self.size[0], self.opts['margin'][1]+self.size[1]), self.opts['background'])
        
        col = 0
        for unit_text in self.units:
            pos_x = self.opts['margin'][0]+(self.tile_size[0]*col)-(1*col)
            pos_y = self.opts['margin'][1]
            tbd = TextBoxDrawer(unit_text, size=self.tile_size, opts={
                'margin': (pos_x, pos_y),
                'border_width': self.opts['border_width'],
                'padding': self.opts['padding'],
                'font_ttf': self.opts['font_ttf'],
                'font_size': self.opts['font_size'],
                'font_align': self.opts['font_align'],
                'font_color': self.opts['font_color'],
                'fill': self.opts['fill'],
                'border_color': self.opts['border_color'],
            })
            tbd.draw(imageObject)
            col += 1
        
        return self.round(imageObject)

class ScheduleSceneComposer(object):
    """
    Objet de la scène complète d'un diagramme de gantt à partir d'un calendrier
    """
    opts = {
        'background': (0, 0, 0, 0),
        'border_width': 1,
        'border_color': (0, 0, 0, 255),
        'grid_fill': (0, 0, 0, 0),
        'grid_border_color': (191, 191, 191, 255),
        'title_padding': (4, 4),
        'title_font_ttf': None,
        'title_font_size': 12,
        'title_font_color': (0, 0, 0, 255),
        'title_font_align': 'right',
        'title_fill': (0, 0, 0, 0),
        'group_font_ttf': None,
        'group_font_color': (0, 0, 0, 255),
        'group_font_align': 'right',
        'group_fill': (0, 0, 0, 0),
        'unit_padding': (1, 2),
        'unit_font_ttf': None,
        'unit_font_size': 12,
        'unit_font_color': (0, 0, 0, 255),
        'unit_font_align': 'center',
        'unit_fill': (0, 0, 0, 0),
        'round_radius': False,
    }
    def __init__(self, scheduleObject, with_groups=True, opts={}):
        """
        :type scheduleObject: object ``Sveetchies.gantt.models.ScheduleModel``
        :param scheduleObject: Objet du calendrier qui détermine le nombre de colonnes, 
                               de lignes et la grille de données.
        
        :type with_groups: boolean
        :param with_groups: Indique si le calendrier doit utiliser les groupes et les 
                            insérer dans la grille. Par défaut cette option est 
                            désactivée.
        
        :type opts: dict
        :param opts: Vide par défaut. Permet de changer les options de mise en forme par 
                     défaut. Les options disponibles sont "background", "border_width", "border_color", 
                     "grid_border_color", "grid_fill". De plus les titres et les unités 
                     ont tout deux les options "font_ttf", "font_size", "font_color", 
                     "font_align", "padding", "fill" avec le préfixe respectivement "title_" 
                     et "unit_". Les groupes héritent des options des titres sauf pour "font_ttf", 
                     "font_color", "font_align", "fill" sous le préfixe "group_".
                     Optionnellement existe aussi l'option "round_radius", False par 
                     défaut et qui désactive les arrondis, si indiqué il doit être un ``integer`` 
                     donnant le radius des arrondis, ces derniers sont positionnés automatiquement 
                     sur tout les angles des éléments du graphique.
        """
        self.scheduleObject = scheduleObject
        self.with_groups = with_groups
        
        self.opts.update(opts)
        
        self.rows = len(self.scheduleObject.tasks)
        self.cols = self.scheduleObject.width
        
        self._get_coords()
        
    def __repr__(self):
        return '<ScheduleSceneComposer Size%s Tile%s> %s' % (str(self.size), str(self.tile_size), self.__str__())
    
    def __str__(self):
        return self.__unicode__().encode('UTF8')
    
    def __unicode__(self):
        return self.scheduleObject.__unicode__()
        
    def _get_coords(self):
        """
        Coordonées des éléments
        """
        # Récupère le plus long titre de tache ou de groupe et le garde comme référence
        max_text = ''
        for task_row in self.scheduleObject.tasks:
            if len(task_row.label) > len(max_text):
                max_text = task_row.label
        if self.with_groups:
            for group in self.scheduleObject.groups:
                if len(group.label) > len(max_text):
                    max_text = group
        # Calcul la hauteur nécessaire au titre de référence
        tbd = TextBoxDrawer( max_text, opts={
            'border_width': self.opts['border_width'],
            'padding': self.opts['title_padding'],
            'font_ttf': self.opts['title_font_ttf'],
            'font_size': self.opts['title_font_size']
        })
        self.reference_title_size = tbd.box_size
        
        # Calcul la largeur nécessaire aux tuiles de la ligne des unités
        units = [str(i) for i in range(1, self.cols+1)]
        unitline_opts = {
            'margin':(self.reference_title_size[0]-1, 0),
            'padding': self.opts['unit_padding'],
            'font_ttf': self.opts['unit_font_ttf'],
            'font_size': self.opts['unit_font_size'],
            'font_align': self.opts['unit_font_align'],
            'font_color': self.opts['unit_font_color'],
            'fill': self.opts['unit_fill'],
            'border_width': self.opts['border_width'],
            'border_color': self.opts['border_color'],
            'round_corners': ('top-left', 'top-right'),
            'round_radius': int(self.opts['round_radius']),
            'round_outfill': self.opts['background'],
        }
        self.unitlineObject = UnitLineComposer(units, opts=unitline_opts)
        
        # Dimensions de la tuile pour les mosaiques
        self.tile_size = (self.unitlineObject.tile_size[0], self.reference_title_size[1])
        
        # Instancie la mosaique pour récupérer ses dimensions
        self.mosaic_coords = (self.reference_title_size[0]-1, self.unitlineObject.size[1]-self.opts['border_width'])
        self.mosaicObject = ScheduleMosaicComposer(self.scheduleObject, tile_size=self.tile_size, with_groups=self.with_groups, opts={
            'border_width':self.opts['border_width'],
        })
        
        # Calcul la dimension complète de l'image avec tout ses éléments
        self.size = (self.mosaicObject.offset[0]+self.reference_title_size[0]-self.opts['border_width'], self.mosaicObject.offset[1]+self.unitlineObject.size[1]-self.opts['border_width'])

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
        
        # Mosaique de tuiles des taches
        self.unitlineObject.draw(imageObject)
        mosaic_scene = self.mosaicObject.draw()

        # Grille de fond de la mosaique
        gridObject = GridDrawer(self.mosaicObject.offset, self.mosaicObject.tile_size, opts={
            'border_color': self.opts['grid_border_color'],
            'border_width': self.mosaicObject.opts['border_width'],
            'background': self.opts['grid_fill'],
        })
        grid_scene = gridObject.draw()
        # Bordure de cadre par dessus le tout
        borderObject = BorderDrawer(self.mosaicObject.offset, opts={
            'border_color': self.opts['border_color'],
            'border_width': self.mosaicObject.opts['border_width'],
            'round_corners': ('bottom-right',),
            'round_radius': int(self.opts['round_radius']),
            'round_outfill': self.opts['background'],
        })
        border_scene = borderObject.draw()
        
        text_coords = [0, self.unitlineObject.size[1]-self.opts['border_width']]
        text_opts = {}
        group_row = 1
        for group in self.scheduleObject.groups:
            # Titre optionnel du groupe
            if self.with_groups:
                round_corn = None
                if group_row==1:
                    round_corn = ('top-left',)
                tbd = TextBoxDrawer(group.label, size=self.reference_title_size, opts={
                    'margin': tuple(text_coords),
                    'border_width': self.opts['border_width'],
                    'padding': self.opts['title_padding'],
                    'font_ttf': self.opts['group_font_ttf'],
                    'font_size': self.opts['title_font_size'],
                    'font_align': self.opts['group_font_align'],
                    'font_color': self.opts['group_font_color'],
                    'fill': self.opts['group_fill'],
                    'border_color': self.opts['border_color'],
                    'round_corners': round_corn,
                    'round_radius': int(self.opts['round_radius']),
                    'round_outfill': self.opts['background'],
                })
                tbd.draw(imageObject)
                text_coords[1] += self.reference_title_size[1]-self.opts['border_width']
            # Titres des taches du groupe
            title_row = 1
            for task_item in group.tasks:
                round_corn = None
                if group_row==len(self.scheduleObject.groups) and title_row==len(group.tasks):
                    round_corn = ('bottom-left',)
                tbd = TextBoxDrawer(task_item.label, size=self.reference_title_size, opts={
                    'margin': tuple(text_coords),
                    'border_width': self.opts['border_width'],
                    'padding': self.opts['title_padding'],
                    'font_ttf': self.opts['title_font_ttf'],
                    'font_size': self.opts['title_font_size'],
                    'font_align': self.opts['title_font_align'],
                    'font_color': self.opts['title_font_color'],
                    'fill': self.opts['title_fill'],
                    'border_color': self.opts['border_color'],
                    'round_corners': round_corn,
                    'round_radius': int(self.opts['round_radius']),
                    'round_outfill': self.opts['background'],
                })
                tbd.draw(imageObject)
                text_coords[1] += self.reference_title_size[1]-self.opts['border_width']
                title_row += 1
            group_row += 1
        
        imageObject.paste(grid_scene, self.mosaic_coords, grid_scene)
        imageObject.paste(mosaic_scene, self.mosaic_coords, mosaic_scene)
        imageObject.paste(border_scene, self.mosaic_coords, border_scene)
        
        return imageObject
