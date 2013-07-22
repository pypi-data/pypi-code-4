
import os
import sys
import logging
from PIL import Image

log = logging.getLogger(__name__)

class Thumb(object):
    '''
    A simple class to:

      #. check for the existence of the thumbnail of the requested size
      #. create a thumbnail
      #. delete a thumbnail
    '''
    def __init__(self, image_file, size_x=128, size_y=128):
        self.image_file = image_file
        self.size_x = size_x
        self.size_y = size_y

        self.size = size_x, size_y

    def make(self):
        outfile = self.outfile
        if self.image_file != outfile:
            try:
                im = Image.open(self.image_file)
                im.thumbnail(self.size, Image.ANTIALIAS)
                im.save(outfile, "JPEG")
            except IOError:
                log.exception("unable to create thumbnail for '%s'",
                               self.image_file)

    def delete(self):
        os.remove(self.outfile)

    @property
    def thumb_filename(self):
        '''returns just the thumbnail's filename'''
        f = os.path.basename(self.outfile)
        return f

    @property
    def outfile(self):
        '''returns the full path to the file which is to be
        made/searched for/ deleted etc
        '''
        # notice how the tuple self.size to populate the two ints here
        f = os.path.splitext(self.image_file)[0] + ".thumb%dx%d.jpg" % self.size
        return f

    @property
    def exists(self):
        f = os.path.exists(self.outfile)
        return f




