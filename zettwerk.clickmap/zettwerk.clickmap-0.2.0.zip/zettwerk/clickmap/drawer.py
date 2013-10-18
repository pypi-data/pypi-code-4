from PIL import Image
from PIL.ImageDraw import Draw
from tempfile import mkstemp
    
IMAGE_FORMAT = 'RGB'
OUTPUT_FORMAT = 'PNG'
BACKGROUND_COLOR = (255, 255, 255)

MAX_DOTSIZE = 10

def do(width, height, coords):
    image = Image.new(IMAGE_FORMAT,
                      (width, height),
                      BACKGROUND_COLOR)
    _add_coords(image, coords)

    return _write_image(image)


def _add_coords(image, coords):
    """ """
    image_drawer = Draw(image)
    for coord in coords:
        _draw_weighted_coord(image_drawer,
                             x=coord[0],
                             y=coord[1],
                             weight=coord[2])
        
def _draw_weighted_coord(drawer, x, y, weight):
    """
    a higher weight results in a bigger circle
    """
    fill_color = (255, 0, 0)
    border_color = (0, 0, 0)
    if weight > MAX_DOTSIZE:
        weight = MAX_DOTSIZE
        
    area = (x - weight,
            y - weight,
            x + weight,
            y + weight)
    
    drawer.ellipse(area,
                   outline=border_color,
                   fill=fill_color)
        
def _write_image(image):
    (dest_handle, dest_path) = mkstemp(".png")
    image.save(dest_path, OUTPUT_FORMAT)
    return dest_path
