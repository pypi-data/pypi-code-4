import os
import sys

try:
    import Image
except:
    from PIL import Image

def massresize(path, new_width):
    for fname in os.listdir(path):
        fname = os.path.join(path, fname)
        try:
            image = Image.open(fname)
        except IOError:
            continue

        width, height = image.size

        new_width = int(new_width)
        new_height = int(new_width/(float(width)/height))

        new_image = image.resize((new_width, new_height), Image.NEAREST)
        new_image.save("%s.resized.%s"%(".".join(fname.split(".")[:-1]), fname.split(".")[-1]))