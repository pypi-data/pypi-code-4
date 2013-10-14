import json

from passta import __version__
from passta.gpg import EncryptedFile


class Store:
    VERSION = 1

    def __init__(self, filename):
        self.file_ = EncryptedFile(filename)
        self.load()

    @property
    def empty_content(self):
        return {
            'passwords': {},
            '__passta': {
                'version': __version__,
                'store_version': self.VERSION,
            },
        }

    def load(self):
        try:
            content = self.file_.read()
        except IOError:
            content = self.empty_content
        else:
            try:
                content = json.loads(content)
            except ValueError as e:
                raise IOError(e)

        if not '__passta' in content:   # store version 0
            passwords = content
            content = self.empty_content
            content['passwords'] = passwords

        if content['__passta']['store_version'] > self.VERSION:
            raise IOError('Can\'t read store: version too new')

        content['__passta']['version'] == __version__
        self.content = content

    def save(self):
        self.file_.write(json.dumps(self.content))

    def __contains__(self, key):
        return key in self.content

    def __getitem__(self, key):
        return self.content[key]

    def __setitem__(self, key, value):
        self.content[key] = value
