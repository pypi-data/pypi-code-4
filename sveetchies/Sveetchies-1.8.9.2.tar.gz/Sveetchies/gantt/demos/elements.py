# -*- coding: utf-8 -*-
"""
Démonstrations des éléments graphiques de base
"""
import Image

from Sveetchies.gantt.png.elements import *

from Sveetchies.gantt.demos import *

# Arrondis
print "===== ROUND CORNERS ====="
round_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
rcd1 = RoundCornerDrawer((40,40), 10, opts={
    'margin':(0, 0),
    'border_width':1,
})
print rcd1
rcd1.draw(round_scene, corners=('top-left', 'top-right', 'bottom-left', 'bottom-right'))
# Sur un rectangle simple
tileObject = TileDrawer(size=(60, 40), opts={
    'margin':(60, 60),
    'border_width':2,
    'fill':"yellow",
    "border_color":(0, 255, 0, 255),
})
print tileObject
tileObject.draw(round_scene)
rcd2 = RoundCornerDrawer((60, 40), 10, opts={
    'margin':(60, 60),
    'border_width':2,
    'background':GLOBAL_BACKGROUND,
    'fill':(0, 0, 0, 0),
    'border_color':(0, 255, 0, 255),
})
print rcd2
rcd2.draw(round_scene, corners=('top-left', 'top-right', 'bottom-left', 'bottom-right'))
# Sur une textbox
tbd = TextBoxDrawer("Lorem ipsum salace nec vergirture", opts={
    'margin': (120, 120),
    'padding': (5, 2),
    'font_ttf': REGULAR_FONT_PATH,
    'border_width': 1,
    'font_size': 12,
    'font_color': (35, 35, 220, 255),
    'fill': (1, 154, 255, 255),
    'border_color': (35, 35, 220, 255),
})
print tbd
tbd.draw(round_scene)
rcd3 = RoundCornerDrawer(tbd.box_size, 5, opts={
    'margin': (120, 120),
    'border_width': 1,
    'background': GLOBAL_BACKGROUND,
    'fill': (1, 154, 255, 255),
    'border_color': (35, 35, 220, 255),
})
print rcd3
rcd3.draw(round_scene, corners=('top-left',))

round_scene.save(DEMOS_OUTPUT_PATH%"round.png", "PNG")
print

# Bordure d'encadrement
print "===== BORDER ====="
border_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
bd1 = BorderDrawer((200, 100), opts={
    'border_color':(0, 0, 0, 255),
    'border_width':1,
})
bd1.draw(border_scene)
print bd1
bd2 = BorderDrawer((200, 100), opts={
    'margin':(20, 20),
    'border_color':(255, 0, 0, 255),
    'border_width':4,
})
bd2.draw(border_scene)
print bd2
bd3 = BorderDrawer((200, 100), opts={
    'margin':(40, 40),
    'border_color':(0, 0, 255, 255),
    'border_width':4,
    'round_corners': ('top-left', 'top-right', 'bottom-left', 'bottom-right'),
    'round_outfill': GLOBAL_BACKGROUND,
})
bd3.draw(border_scene)
print bd3
bd4 = BorderDrawer((200, 100), opts={
    'margin':(60, 60),
    'border_color':(0, 255, 0, 255),
    'border_width':4,
    'sides':('right', 'bottom'),
})
bd4.draw(border_scene)
print bd4
border_scene.save(DEMOS_OUTPUT_PATH%"border.png", "PNG")
print

# Simples tuiles
print "===== TILES ====="
tile_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
tileObject1 = TileDrawer(size=TILE_SIZE, opts={
    'fill': "red",
    'border_width': 1,
    'border_color': "black",
})
print tileObject1
tileObject1.draw(tile_scene)

tileObject2 = TileDrawer(size=(60, 40), opts={
    'margin': (20, 50),
    'fill': "yellow",
    'border_width': 2,
    'border_color': "green",
})
print tileObject2
tileObject2.draw(tile_scene)

tileObject3 = TileDrawer(size=(50, 50), opts={
    'margin': (160, 80),
    'fill': "grey",
    'border_width': 1,
    'border_color': "black",
    'sides': ('right', 'left'),
})
print tileObject3
tileObject3.draw(tile_scene)

tileObject4 = TileDrawer(size=(50, 50), opts={
    'margin': (250, 20),
    'fill': (71, 184, 255, 255),
    'border_width': 1,
    'border_color': (51, 132, 184, 255),
    'round_corners': ('top-left', 'top-right', 'bottom-left', 'bottom-right'),
    'round_outfill': GLOBAL_BACKGROUND,
})
print tileObject4
tileObject4.draw(tile_scene)

tile_scene.save(DEMOS_OUTPUT_PATH%"tiles.png", "PNG")
print

# Grille
print "===== GRID ====="
grid_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
#
gd1 = GridDrawer((191,115), (20,20), opts={
    'margin': (0, 0),
    'round_corners': ('top-left', 'top-right', 'bottom-left', 'bottom-right'),
    'round_radius': 5,
    'round_outfill': GLOBAL_BACKGROUND,
})
print gd1
gd1.draw(grid_scene)

gd2 = GridDrawer((191,115), (20,20), opts={
    'margin': (200, 40),
    'border_color': (255, 0, 0, 255),
    'border_width': 2,
})
print gd2
gd2.draw(grid_scene)
#
grid_scene.save(DEMOS_OUTPUT_PATH%"grid.png", "PNG")
print

# Boîte de texte
print "===== TEXTBOX ====="
textbox_scene = Image.new("RGBA", SCENE_SIZE, GLOBAL_BACKGROUND)
#
tbd1 = TextBoxDrawer(u"Hellô World!", opts={
    'font_ttf': REGULAR_FONT_PATH,
    'font_size': 14,
})
print tbd1
tbd1.draw(textbox_scene)
#
tbd2 = TextBoxDrawer("Rounded Aware !", opts={
    'margin': (250, 30),
    'padding': (5, 4),
    'font_ttf': REGULAR_FONT_PATH,
    'font_size': 14,
    'font_color': (90, 166, 123, 255),
    'fill': (159, 255, 76, 255),
    'border_color': (110, 186, 143, 255),
    'round_radius': 5,
    'round_corners': ('top-left', 'top-right', 'bottom-left', 'bottom-right'),
    'round_outfill': GLOBAL_BACKGROUND,
})
print tbd2
tbd2.draw(textbox_scene)
#
txt_gp_margin = (20, 70)
txt_gp_padding = (5, 5)
tbd2 = TextBoxDrawer("Lorem ipsum salace nec vergirture", opts={
    'margin': txt_gp_margin,
    'padding': txt_gp_padding,
    'font_ttf': REGULAR_FONT_PATH,
    'font_size': 12,
    'font_color': (35, 35, 220, 255),
    'fill': (1, 154, 255, 255),
    'border_width': 1,
    'border_color': (35, 35, 220, 255),
})
print tbd2
tbd2.draw(textbox_scene)
#
tbd3 = TextBoxDrawer(u"Plôp", size=tbd2.box_size, opts={
    'margin': (txt_gp_margin[0], tbd2.box_size[1]+tbd2.opts['margin'][1]+5),
    'padding': txt_gp_padding,
    'font_ttf': REGULAR_FONT_PATH,
    'font_size': 12,
    'font_align': 'left',
    'font_color': (35, 35, 220, 255),
    'fill': (1, 154, 255, 255),
    'border_width': 1,
    'border_color': (35, 35, 220, 255),
})
print tbd3
tbd3.draw(textbox_scene)
#
tbd4 = TextBoxDrawer(u"Plöp", size=tbd3.box_size, opts={
    'margin': (txt_gp_margin[0], tbd3.box_size[1]+tbd3.opts['margin'][1]+5),
    'padding': txt_gp_padding,
    'font_ttf': REGULAR_FONT_PATH,
    'font_size': 12,
    'font_align': 'right',
    'font_color': (35, 35, 220, 255),
    'fill': (1, 154, 255, 255),
    'border_width': 1,
    'border_color': (35, 35, 220, 255),
})
print tbd4
tbd4.draw(textbox_scene)
#
tbd5 = TextBoxDrawer(u"PlŒp", size=tbd4.box_size, opts={
    'margin': (txt_gp_margin[0], tbd4.box_size[1]+tbd4.opts['margin'][1]+5),
    'padding': txt_gp_padding,
    'font_ttf': REGULAR_FONT_PATH,
    'font_size': 12,
    'font_align': 'center',
    'font_color': (35, 35, 220, 255),
    'fill': (1, 154, 255, 255),
    'border_width': 1,
    'border_color': (35, 35, 220, 255),
})
print tbd5
tbd5.draw(textbox_scene)
#
textbox_scene.save(DEMOS_OUTPUT_PATH%"textbox.png", "PNG")
print
