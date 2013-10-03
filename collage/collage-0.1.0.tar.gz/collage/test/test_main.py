from collage.test.base import CollageTestCase
from collage.main import Application

class TestApplication(CollageTestCase):

    def test(self):
        app = Application(self.temppath, max_results=4)
        app.run(queries=['kitten', 'puppy'])
        self.assertTrue(app.collage_paths)

