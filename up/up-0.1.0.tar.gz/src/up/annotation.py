import time


class Annotation(object):
    def __init__(self, message):
        self.message = message
        self.date = time.time()
