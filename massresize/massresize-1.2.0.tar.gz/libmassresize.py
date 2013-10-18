import os

try:
    import Image
except:
    from PIL import Image

def massresize(path, new_width):
    if not os.path.exists(path):
        return False
    for fname in os.listdir(path):
        if not os.path.exists(os.path.join(path, "resized")):
            try:
                os.makedirs(os.path.join(path, "resized"))
            except IOError:
                return False
        new_fname = os.path.join(path, "resized", fname)
        fname = os.path.join(path, fname)
        try:
            image = Image.open(fname)
        except IOError:
            continue

        width, height = image.size

        new_width = int(new_width)
        new_height = int(new_width/(float(width)/height))

        new_image = image.resize((new_width, new_height), Image.NEAREST)
        new_image.save(new_fname)
    return True