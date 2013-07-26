# -*- coding: utf-8 -*-
"""
Modèles de données

Principe
........

        ^
        |
        |
 Tasks  |
        |
        |____________________>

         Unitline for events


Couches d'utilisation
.....................

    [Bottom] 
            > Event*
                    > Task*
                           > Schedule
                                     > [Top]
"""
class EventModel(object):
    """
    Evénement dans une tache
    """
    def __init__(self, start, length, tile):
        """
        :type start: int
        :param start: Position de départ de l'évènement dans le tableau des emplacements 
                      disponibles pour la ligne de la tâche.
        
        :type length: int
        :param length: Longueur de l'évènement
        
        :type tile: any
        :param tile: Accepte n'importe quel objet mais actuellement seul les types suivants sont implémentés :
                     * un `string` contenant le nom clé d'un template de tuile;
                     * un objet `Sveetchies.gantt.png.TileDrawer` qui définit une tuile déja créée;
        """
        self.start = start
        self.length = length
        self.tile = tile
        self.end = self.start+self.length-1
    
    def __repr__(self):
        return '<EventModel Tile %s from %s to %s>' % (self.__str__(), self.start, self.end)
    
    def __str__(self):
        return self.__unicode__().encode('UTF8')
    
    def __unicode__(self):
        return self.tile
    
    def get_tiles(self):
        """
        Renvoi une liste d'emplacements occupés par l'évènement
        
        :rtype: list
        :return: La liste est une répétition du ``self.tile`` selon la longueur de 
                 l'évènement
        """
        return [self.tile for i in range(0, self.length)]

class GroupModel(object):
    """
    Groupe de catégorie de tâches
    
    Un même groupe peut être lié à plusieurs tâches différentes
    """
    def __init__(self, label):
        """
        :type label: string
        :param label: Désignation du groupe
        """
        self.label = label
        self.tasks = []
    
    def __repr__(self):
        return '<GroupModel Tasks(%s)> %s' % (len(self.tasks), self.__str__())
    
    def __str__(self):
        return self.__unicode__().encode('UTF8')
    
    def __unicode__(self):
        return self.label

class TaskModel(object):
    """
    Tâche
    
    Une tache peut etre composée de plusieurs évènements qui se suivent sur une même 
    ligne de cellules
    """
    def __init__(self, label, group=None, events=()):
        """
        :type label: string
        :param label: Désignation de la tâche
        
        :type group: object `GroupModel`
        :param group: (optional) Objet du groupe auquel appartient la tâche. Vide par 
                      défaut.
        
        :type events: list
        :param events: (optional) Liste d'évènements contenus. Vide par défaut.
        """
        self.label = label
        self.group = group
        self.events = events
        self.width = self._get_width()
        self.group.tasks.append(self)
    
    def __repr__(self):
        return '<TaskModel Width(%s)> %s' % (self.width, self.__str__())
    
    def __str__(self):
        return self.__unicode__().encode('UTF8')
    
    def __unicode__(self):
        return self.label
    
    def _get_width(self):
        """
        Renvoi la liste combinant toute les cellules d'évènements contenus
        
        :rtype: int
        :return: Liste composé de tout les emplacements des évènements mis à bout à bout
        """
        width = 0
        for event_item in self.events:
            pos = event_item.start-1
            if event_item.end>width:
                width = event_item.end
        
        return width

    def get_event_cells(self, width=None):
        """
        Renvoi la ligne de toute les évènements de la tâche
        
        :type width: int
        :param width: (optional) Nombre d'emplacements optionnel qui modifie la longueur 
                      de la liste. Par défaut si non spécifié, la longueur sera des 
                      évènements bout à bout.
        
        :rtype: list
        :return: Liste complète de tout les évènements à leur position dans les
                 emplacements disponibles. Par défaut tout les emplacements sont vides 
                 (``None``) et sont occupés par les évènements correspondant.
        """
        if not width:
            width = self.width
        
        cells = [None for col in range(1, width+1)]
        
        for event in self.events:
            for cell in range(event.start, event.end+1):
                cells[cell-1] = event.tile
        
        return cells

class ScheduleModel(object):
    """
    Calendrier de tâches
    """
    def __init__(self, name, tasks=()):
        """
        :type name: string
        :param name: Désignation du calendrier.
        
        :type tasks: list
        :param tasks: (optional) Liste d'objets `TaskModel` composant le calendrier. 
                      Vide par défaut.
        """
        self.name = name
        self.tasks = tasks
        self.width = self._get_width()
        self.groups = self._get_groups()

    def __repr__(self):
        return '<ScheduleModel Groups(%s) Tasks(%s) Width(%s)> %s' % (len(self.groups), len(self.tasks), self.width, self.__str__())
    
    def __str__(self):
        return self.__unicode__().encode('UTF8')
    
    def __unicode__(self):
        return self.name

    def _get_width(self):
        """
        Renvoi la longueur combinée de toute les cellules d'évènements de toute les tâches
        
        :rtype: int
        :return: Longueur retenue de la plus longue (en emplacement occupés par les 
                 évènements) Tâche
        """
        width = 0
        for task_item in self.tasks:
            if task_item.width>width:
                width = task_item.width
        
        return width
    
    def _get_groups(self):
        """
        Renvoi une liste sans doublons des groupes utilisés dans les tâches
        
        :rtype: list
        :return: Liste d'objets `GroupModel` liés par les tâches, sans doublons.
        """
        groups = []
        for task_entry in self.tasks:
            # Groupe
            if task_entry.group not in groups:
                groups.append(task_entry.group)
        return groups

    def get_grid(self, with_groups=False):
        """
        Renvoi la grille complète du calendrier
        
        :type with_groups: boolean
        :param with_groups: (optional) Active l'utilisation des groupes pour construire 
                            la grille, un groupe prendra alors une ligne vide pour lui 
                            tout seul juste avant la ligne de la première de ses tâches.
                            Par défaut cette option est désactivée et ne renvoi que les 
                            lignes des tâches.
        
        :rtype: list
        :return: Une liste contenant les listes d'évènements des tâches.
        """
        grid = []
        # Fait une ligne par tâche à partir d'un prototype
        if with_groups:
            for group in self.groups:
                grid.append([])
                for task in group.tasks:
                    grid.append(task.get_event_cells(width=self.width))
        else:
            for task in self.tasks:
                grid.append(task.get_event_cells(width=self.width))
        return grid
