from collage.test.base import CollageTestCase
from collage.search import GoogleImages
import tempfile
import os
import PIL.Image
import StringIO
import shutil

class TestGoogleImages(CollageTestCase):

    example_queries = ['kitten']

    def test(self):
        g = GoogleImages(path=self.temppath, max_results=4)
        self.assertFalse(g.get_paths('.std'))
        g.pull(self.example_queries)
        self.assertTrue(g.results)
        self.assertTrue(g.get_paths('.std'))
        image = g.open_image(g.get_paths('.std')[0])
        self.assertEqual(image.size, g.std_size)

