"""Contains functions for drawing the environment.
"""
from PIL import Image
from PIL import ImageColor
import aggdraw
import itertools
import os

CELL_SIZE = 8 # size of a grid cell in pixels
IMAGE_BOARDER = 2 # number of blanks cells around the image boarder

def draw_environment(grid, out_filename=None):
    """Draws the environment, either saving it to a file or returning an Image.
    """
    x_cells = grid.shape[0]
    y_cells = grid.shape[1]
    image_width = (x_cells + IMAGE_BOARDER * 2) * CELL_SIZE
    image_height = (y_cells + IMAGE_BOARDER * 2) * CELL_SIZE
    im = Image.new('RGB', (image_width, image_height), 'white')
    draw = aggdraw.Draw(im)
    draw.setantialias(True)
    draw_chemicals(draw, grid)
    #TODO: draw a legend
    draw_boarder(draw, x_cells, y_cells)
    draw.flush()
    if out_filename is not None:
        try:
            os.remove(out_filename)
        except Exception:
            pass
        im.save(out_filename)
    else:
        return im

def draw_chemicals(draw, grid):
    """Draws the distribution of chemicals in the environment.

    If ``out_filename`` is provided, the image is saved. Otherwise, a PIL 
    Image object is returned.

    Args:
        grid: A numpy array. Generally, this is an Environment.grid attribute.
    """
    x_cells = grid.shape[0]
    y_cells = grid.shape[1]
    num_chemicals = grid.shape[2]
    colors = make_chemical_colors(num_chemicals)
    for point in itertools.product(xrange(x_cells), xrange(y_cells)):
        for chemical, amount in enumerate(grid[point[0], point[1]]):
            brush = aggdraw.Brush(colors[chemical])
            #TODO: choose a better scale for percent. don't use hard coded 2.0
            scale_factor = amount
            #TODO: scale circle size by amount
            draw_circle(draw, point[0], point[1], scale_factor, brush=brush)

def draw_organisms(draw_object, grid_x, grid_y):
    """Draws the organisms on the environment grid.
    """

def draw_boarder(draw_object, grid_x, grid_y):
    """Draws a boarder around the environment grid.
    """
    x1 = y1 = IMAGE_BOARDER * CELL_SIZE - 1
    x2 = (IMAGE_BOARDER + grid_x) * CELL_SIZE + 1
    y2 = (IMAGE_BOARDER + grid_y) * CELL_SIZE + 1
    pen = aggdraw.Pen(ImageColor.getrgb('black'), width=1)
    draw_object.rectangle((x1, y1, x2, y2), pen, None)

def draw_circle(draw_object, cell_x, cell_y, size, pen=None, brush=None):
    """Draws a circle on ``draw_object`` in cell (cell_x, cell_y) with a
    diameter of ``size`` cells.
    """
    radius = size * CELL_SIZE / 2
    x1 = (cell_x + 0.5 + IMAGE_BOARDER) * CELL_SIZE - radius
    y1 = (cell_y + 0.5 + IMAGE_BOARDER) * CELL_SIZE - radius
    x2 = (cell_x + 0.5 + IMAGE_BOARDER) * CELL_SIZE + radius
    y2 = (cell_y + 0.5 + IMAGE_BOARDER) * CELL_SIZE + radius
    #assert(x2 - x1 == y2 - y1)
    draw_object.ellipse((x1, y1, x2, y2), pen, brush)

def make_chemical_colors(num_colors, sat=0.5, value=0.5, format='PIL'):
    """Returns a list of ``num_colors`` colors for coloring chemicals.

    sat and val are values between 0 and 1.
    """
    sat = int(sat * 100)
    value = int(value * 100)
    try:
        color_step = 360 / num_colors
    except ZeroDivisionError:
        return []
    rgb_colors = [ImageColor.getrgb('hsl({},{}%,{}%)'.format(hue, sat, value)) 
                    for hue in range(0, 360, color_step)]
    if format == 'matplotlib':
        rgb_colors = [(r/255.0, g/255.0, b/255.0) for r, g, b in rgb_colors]
    return rgb_colors
