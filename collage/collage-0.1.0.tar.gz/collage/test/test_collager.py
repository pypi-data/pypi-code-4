from collage.test.base import CollageTestCase
from collage.collager import Collager
from collage.search import GoogleImages
import os
from PIL import Image

class TestCollager(CollageTestCase):

    def test(self):
        path = os.path.join(self.temppath, '.std', 'example1')
        os.makedirs(os.path.dirname(path))
        self.write_image_fixture(path)
        path = os.path.join(self.temppath, '.std', 'example2')
        self.write_image_fixture(path)
        path = os.path.join(self.temppath, '.std', 'example3')
        self.write_image_fixture(path)
        c = Collager(self.temppath)
        paths = c.collage_paths
        self.assertTrue(paths)
        path = paths[0]
        self.assertTrue(os.path.exists(path))
        image = Image.open(path)
        self.assertIsInstance(image, Image.Image)

