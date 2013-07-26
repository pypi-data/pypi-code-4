# -*- coding: utf-8 -*-
"""
Données de tests
"""
from Sveetchies.gantt.models import *

SCENE_SIZE = (400, 200)
TILE_SIZE = (8, 14)
MOSAIC_SIZE = (300, 100)
REGULAR_FONT_PATH = './fonts/liberation_sans/LiberationSans-Regular.ttf'
BOLD_FONT_PATH = './fonts/liberation_sans/LiberationSans-Bold.ttf'
DEMOS_OUTPUT_PATH = './output/%s'
GLOBAL_BACKGROUND = (240, 240, 240, 255)

# Groupes de catégorie
g_dev = GroupModel(u"Développement")
g_report = GroupModel(u"Recette")
g_prod = GroupModel(u"Production")

# Calendrier de démonstration
scheduleObject = ScheduleModel(u'Démonstration', (
    #(id, label, groupkey, units),
    TaskModel(u"Modélisations et système de validations", g_dev, (
        EventModel(1, 5, 'blue'),
    )),
    TaskModel(u"Intégration email", g_dev, (
        EventModel(6, 3, 'turquoise'),
    )),
    TaskModel(u"Design", g_report, (
        EventModel(9, 3, 'red'),
    )),
    TaskModel(u"Intégration du système d'exportation des données", g_report, (
        EventModel(12, 8, 'yellow'),
    )),
    TaskModel(u"Interface de contrôle des données", g_report, (
        EventModel(9, 3, 'violet'),
    )),
    TaskModel(u"Intégration au site", g_report, (
        EventModel(20, 5, 'orange'),
        EventModel(25, 10, 'grey'),
    )),
    TaskModel(u"Validation de la plateforme", g_prod, (
        EventModel(20, 5, 'green'),
        EventModel(25, 10, 'grey'),
    )),
))
           
if __name__ == "__main__":
    print scheduleObject.__repr__()
    
    print "===== TASKS ====="
    for task_item in scheduleObject.tasks:
        print "*", task_item.__repr__()
    print "----- GRID -----"
    for row in scheduleObject.get_grid(with_groups=False):
        print row
    
    print "===== GROUPS ====="
    for group_item in scheduleObject.groups:
        print "*", group_item.__repr__()
    print "----- GRID -----"
    for row in scheduleObject.get_grid(with_groups=True):
        print row
