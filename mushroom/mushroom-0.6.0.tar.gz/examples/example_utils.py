import os
import sys

from mushroom.simple import SimpleServer, StaticFile


EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)


class ExampleStaticFile(StaticFile):
    def __init__(self, filename):
        super(ExampleStaticFile, self).__init__(
                os.path.join(EXAMPLES_DIR, filename))


class ExampleServer(SimpleServer):
    urls = [
        ('/js/mushroom.js', StaticFile(os.path.join(PROJECT_ROOT, 'js', 'mushroom.js'))),
        ('/js/jquery.js', ExampleStaticFile('jquery-1.8.2.min.js')),
        ('/js/knockout.js', ExampleStaticFile('knockout-2.2.0.min.js')),
        ('/js/gauge.js', ExampleStaticFile('gauge-1.2.min.js')),
    ]
