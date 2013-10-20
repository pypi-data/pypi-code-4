# -*- coding: utf-8 -*-
"""
Objet de compositions à partir des éléments
"""
import Image

from Sveetchies.gantt.png.elements import *
from Sveetchies.gantt.png.composers import *

from Sveetchies.gantt.demos import *

# Mosaique simple
print "===== MOSAIC ====="
mosaic_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
grid = (
    ('blue', 'blue', None, None, None, None, None, None, None, None),
    (None, None, 'blue', 'blue', None, None, None, None, None, None),
    (None, None, None, None, None, None, None, None, None, None),
    (None, None, None, None, 'blue', 'blue', 'blue', 'blue', None, None),
    (None, None, None, None, None, None, None, None, 'blue', None),
    (None, None, None, None, None, None, None, None, None, 'blue'),
)
mosaicObject = MosaicComposer(10, 6, grid=grid, tile_size=(20, 20), tile_merge=False)
print mosaicObject
mosaicObject.draw(mosaic_scene)
mosaic_scene.save(DEMOS_OUTPUT_PATH%"mosaic.png", "PNG")
print

# Mosaique à partir du calendrier
print "===== MOSAIC SCHEDULE ====="
mosaic_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
mosaicschedObject = ScheduleMosaicComposer(scheduleObject, size=MOSAIC_SIZE)
print mosaicschedObject
mosaicschedObject.draw(mosaic_scene)
mosaic_scene.save(DEMOS_OUTPUT_PATH%"mosaic_schedule.png", "PNG")
print

# Ligne d'unités
print "===== UNITLINE ====="
ulc = UnitLineComposer([str(i) for i in range(1, scheduleObject.width+1)], opts={
    'font_ttf':BOLD_FONT_PATH,
    'font_align':'center',
    'padding':(3, 8),
    'margin':(10, 20),
    'background': GLOBAL_BACKGROUND,
    'round_corners': ('top-left', 'top-right', 'bottom-left', 'bottom-right'),
    'round_outfill': GLOBAL_BACKGROUND,
})
print ulc
unitline_scene = ulc.draw()
unitline_scene.save(DEMOS_OUTPUT_PATH%"unitline.png", "PNG")
print

# Diagramme
print "===== DIAGRAM ====="
ssd = ScheduleSceneComposer(scheduleObject, opts={
    'background': (255, 255, 255, 255),
    'border_color':(0, 0, 0, 255),
    'grid_fill':(255, 255, 255, 255),
    'title_padding': (6, 6),
    'title_font_ttf': REGULAR_FONT_PATH,
    'title_font_size': 14,
    'title_fill':(255, 255, 255, 255),
    'group_font_ttf': BOLD_FONT_PATH,
    'group_font_align': 'center',
    'group_fill': (230, 230, 255, 255),
    'unit_padding': (7, 7),
    'unit_font_ttf': BOLD_FONT_PATH,
    'unit_font_size': 11,
    'unit_font_color':(0, 0, 0, 255),
    'unit_border_color':(150, 150, 150, 255),
    'unit_fill': (230, 230, 255, 255),
    'round_radius': 6,
})
print ssd.__repr__()
diag_scene = ssd.draw()
#
diag_scene.save(DEMOS_OUTPUT_PATH%"diagram.png", "PNG")
