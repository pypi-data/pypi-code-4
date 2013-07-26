# -*- coding: utf-8 -*-
"""
Gestion de diagrammes de gantt

Pour l'instant, il existe uniquement une génération en image, basée sur 
Python Imaging Library (PIL). Contient une couche (dans ``png.elements``) d'interfaces 
pour dessiner des éléments graphiques simples (rectangles, texte, etc..).

Les interfaces de compositions plus élaborés se trouvent dans ``png.composers``, 
nottement l'interface pour dessiner un diagramme complet. Ce dernier recoit ses données 
d'un objet de calendrier de tâches (cf ``models.ScheduleModel``).

Une démonstration complète de tout les interfaces se trouve dans ``demos``, la 
démonstration d'un diagramme se trouvent dans ``demos.composers``.

Les diagrammes générés sont simples et composés d'une ligne d'unités (en général des 
jours), une colonne de titres de tâches (optionnellement précédé par leur nom de groupe) 
et une mosaique contenant les tuiles pour chaque unités de tâches sur un fond d'une grille.

NOTE: Pour l'instant ce module n'est qu'à l'état de prototype. Bien qu'il soit 
      actuellement capable de faire ce pourquoi il est prévu, il n'est pas vraiment 
      finalisé dans son API.
"""
