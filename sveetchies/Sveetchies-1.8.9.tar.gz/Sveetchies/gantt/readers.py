# -*- coding: utf-8 -*-
"""
Parser de lecture de backend d'un Schedule
"""
import csv, os, sys
from xml.etree.ElementTree import ElementTree

from Sveetchies.gantt.models import *

class CsvReader(object):
    """
    Prévu pour le csv, non fonctionnel
    """
    def fetch(self, filename):
        reader = csv.reader(open(filename, "rb"), delimiter=';', quotechar='"')
        i_row = 0
        for row in reader:
            if i_row > 0:
                for col in row:
                    print col.strip()
            i_row += 1

class XmlBackendError(Exception):
    pass

class XmlReader(object):
    """
    Pour un backend XML
    """
    def __init__(self, default_schedul_title=None, default_group_title="Group %s", default_task_title="Task %s", default_event_tile="white"):
        self.default_schedul_title = default_schedul_title
        self.default_group_title = default_group_title
        self.default_task_title = default_task_title
        self.default_event_tile = default_event_tile
        
        self._parser = ElementTree()

    def get_styles(self, filename):
        """
        Parse un backend de styles de mise en forme
        """
        file_dir = os.path.dirname(filename)
        self._parser.parse(filename)
        root = self._parser.getroot()
        styles = {}
        for item in root.findall('item'):
            if 'name' not in item.keys():
                raise XmlBackendError, "Style item %s is missing an 'name' attribute"
            if 'kind' not in item.keys():
                raise XmlBackendError, "Style item %s is missing an 'kind' attribute"
            if 'value' not in item.keys():
                raise XmlBackendError, "Style item %s is missing an 'value' attribute"
            name = item.get("name")
            kind = item.get("kind")
            value = item.get("value")
            if kind == "integer":
                value = int(value)
            elif kind in ("color", "size"):
                value = tuple([int(v.strip()) for v in value.split(',')])
            elif kind == "path":
                # Résolution des chemins relatifs en utilisant le chemin de du fichier 
                # de styles comme référence de point de base
                if not os.path.isabs(value):
                    value = os.path.normpath(os.path.join(file_dir, value))
            styles[name] = value
        return styles

    def get_backend(self, filename):
        self._parser.parse(filename)
        root = self._parser.getroot()
        schedule_title = root.get("title", default=self.default_schedul_title)
        # Groupes de tâches
        tasks = []
        a = 1
        for group_element in root.findall('group'):
            group_title = group_element.get("title", default=self.default_group_title%a)
            GroupObject = GroupModel(group_title)
            # Tâches
            i = 1
            for task_element in group_element.findall('task'):
                task_title = task_element.get("title", default=self.default_task_title%i)
                # Événements de la tâches
                z = 1
                events = []
                for event_element in task_element.findall('event'):
                    start = int(event_element.get("start"))
                    length = int(event_element.get("length"))
                    tile = event_element.get("tile", default=self.default_event_tile)
                    events.append(EventModel(start, length, tile))
                    z += 1
                # Objet de la tâche
                TaskObject = TaskModel(task_title, group=GroupObject, events=events)
                tasks.append(TaskObject)
                i += 1
            a += 1
        ScheduleObject = ScheduleModel(schedule_title, tasks)
        return ScheduleObject
