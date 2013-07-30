import uuid

class UUIDGenerator(object):
    @staticmethod
    def generate():
        return uuid.uuid4()

