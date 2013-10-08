from base_manager import BaseManager
import os
import pickle


class FileManager(BaseManager):

    path = None

    def __init__(self, namespace, path=None):
        if path is not None:
            self.path = path
        else:
            self.path = self.get_path(namespace)

    def get_path(self, namespace):
        raise NotImplementedError

    def set(self, key, value):
        with open(self.path, 'rb') as input:
            data = pickle.load(input)
            print data
        with open(self.path, 'wb') as output:
            data[key] = value
            pickle.dump(data, output)
            return True

    def get(self, key):
        with open(self.path, 'rb') as input:
            data = pickle.load(input)
            return data[key]

    def length(self):
        with open(self.path, 'rb') as input:
            data = pickle.load(input)
            return len(data)


    def create(self, ignore_already_exists=False):
        if not self.exists():
            data = {}
            with open(self.path, 'wb') as out:
                pickle.dump(data, out)
        else:
            if not ignore_already_exists:
                raise Exception

    def reset(self):
        if self.exists():
            self.delete()
        self.create()

    def delete(self):
        os.remove(self.path)

    def exists(self):
        try:
            with open(self.path):
                pass
            return True
        except IOError:
            return False
