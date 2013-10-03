from collage.base import CollageObject
from collage.test.base import CollageTestCase
from collage.test.base import example_img_base64
import base64
import os

class TestCollageObject(CollageTestCase):

    def setUp(self):
        super(TestCollageObject, self).setUp()
        self.o = CollageObject(self.temppath)

    def test_get_path(self):
        self.assertTrue(os.path.exists(self.o.get_path('test')))

    def test_get_paths(self):
        self.assertFalse(self.o.get_paths('test'))

    def test_open_image(self):
        path = os.path.join(self.temppath, 'tmp.png')
        self.write_image_fixture(path)
        try:
            self.assertTrue(self.o.open_image(path))
        except Exception, e:
            os.unlink(path)
            self.fail("Unable to open image: %s" % e)
        else:
            os.unlink(path)

    def test_open_images(self):
        path = os.path.join(self.temppath, 'tmp.png')
        self.write_image_fixture(path)
        try:
            self.assertTrue(self.o.open_images([path]))
        except Exception, e:
            os.unlink(path)
            self.fail("Unable to open image: %s" % e)
        else:
            os.unlink(path)

    def test_new_image(self):
        image = self.o.new_image()
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, self.o.std_size)

    def test_thumbnail(self):
        image = self.o.thumbnail(self.o.new_image())
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.size, self.tile_size)

    def test_pixels(self):
        pixels = self.o.pixels(self.o.thumbnail(self.o.new_image()))
        self.assertEqual(len(pixels), self.o.tile_size[0]*self.o.tile_size[1])

    def test_thumbnail(self):
        path = os.path.join(self.temppath, 'tmp.png')
        f = open(path, "w")
        f.write(base64.decodestring(example_img_base64))
        f.close()
        try:
            img = self.o.open_image(path)
            # Check thumbnail.
            size = (4,4)
            self.assertNotEqual(img.size, size)
            img = self.o.thumbnail(img, size)
            self.assertEqual(img.size, size)
        finally:
            os.unlink(path)

