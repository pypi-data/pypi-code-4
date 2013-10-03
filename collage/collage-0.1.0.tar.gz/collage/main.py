from collage.base import CollageObject, ApplicationError
from collage.search import GoogleImages
from collage.collager import Collager
from PIL import Image
import sys

class Application(CollageObject):
    """Create collages on demand with images from given search queries.
    """

    def __init__(self, path=None, max_results=None):
        super(Application, self).__init__(path)
        self.max_results = max_results

    def run(self, queries=None):
        """Create collages using images found using given search queries.
        """
        try:
            self.info("Creating collages, please wait...")
            if queries:
                self.queries = queries
            else:
                self.queries = "pig piglet sheep lamb cow dog puppy cat kitten goat".split()
            image_service = GoogleImages(self.path, max_results=self.max_results)
            image_service.pull(self.queries)
            collager = Collager(self.path)
            self.collage_paths = collager.collage_paths
        except ApplicationError:
            sys.exit(1)

    def show_image(self, path):
        """Display image in given filesystem path on screen.
        """
        image = Image.open(path)
        image.show()
