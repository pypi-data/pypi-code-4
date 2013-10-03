import os
import sys
import glob
from Queue import Queue
from threading import Thread
from PIL import Image, ImageOps

class CollageObject(object):

    std_size = 795,795
    tile_size = 15,15
    cmp_size = 3,3

    num_workers = None

    def __init__(self, path=None):
        if not path:
            self.path = os.path.join(os.getcwd(), '.collage-data')
        else:
            self.path = os.path.abspath(path)
            if not os.path.exists(path):
                os.makedirs(path)

    def start_queue(self):
        """Create thread-safe queue object, and worker threads.
        """
        self.q = Queue()
        for i in range(self.num_workers):
            t = Thread(target=self.queue_worker)
            t.daemon = True
            t.start()

    def queue_worker(self):
        """Loop around queue. Wait for and do tasks.
        """
        while True:
            task = self.q.get()
            try:
                self.do_task(task)
            except Exception, e:
                msg = "Failed to complete task: %s: %s" % (task, e)
                self.error(msg)
            self.q.task_done()

    def do_task(self, task):
        """Abstract task handler (override in subclasses).
        """
        raise Exception, "Abstract method not implemented."
        
    def get_history_path(self, token):
        """Get filesystem path for history.
        """
        return os.path.join(self.get_path('.hist') , token)

    def get_std_image_path(self, image_id):
        """Get filesystem path for processed image.
        """
        return os.path.join(self.get_path('.std') , image_id)

    def get_color_image_path(self, image_id, color_name):
        """Get filesystem path for categorised image.
        """
        return os.path.join(self.get_path(color_name), image_id)

    def get_collage_image_path(self, image_id):
        """Get filesystem path for collaged image.
        """
        return os.path.join(self.get_path('collages') , image_id)

    def get_path(self, state):
        """Get filesystem path for given state.
        """
        path = os.path.join(self.path, state)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_paths(self, state):
        """Lists filesystem paths for images in given state.
        """
        return glob.glob(os.path.join(self.get_path(state), '*'))

    def open_image(self, path):
        """Opens image from data in given file object.
        """
        image = None
        try:
            image = Image.open(path)
        except Exception, e:
            pass
        return image

    def open_images(self, paths):
        """Opens images from data in given file objects.
        """
        return [self.open_image(p) for p in paths]

    def new_image(self):
        """Constructs new image object of standard size.
        """
        return Image.new("RGB", self.std_size, color=None)

    def thumbnail(self, image, size=None):
        """Constructs small version of given image.
        """
        if size == None:
            size = self.tile_size
        return ImageOps.fit(image, size, Image.ANTIALIAS)

    def pixels(self, image):
        """Converts given image to a list of pixels.
        """
        pix = image.load()
        wrange = range(image.size[0])
        hrange = range(image.size[1])
        return [pix[i,j] for i in wrange for j in hrange]

    def write(self, msg):
        """Writes given msg to STDOUT (no new line).
        """
        sys.stdout.write(msg)
        sys.stdout.flush()

    def info(self, msg):
        """Prints given msg to STDOUT (new line added).
        """
        sys.stdout.write("%s\n" % msg)
        sys.stdout.flush()

    def warn(self, msg):
        """Prints given warning to STDERR.
        """
        sys.stderr.write("Warning: %s\n" % msg)
        sys.stderr.flush()

    def error(self, msg):
        """Prints given error to STDERR.
        """
        sys.stderr.write("Error: %s\n" % msg)
        sys.stderr.flush()

    def exit(self, msg):
        """Prints given error to STDERR and raises ApplicationError.
        """
        self.error(msg)
        raise ApplicationError()


class ApplicationError(Exception): pass
