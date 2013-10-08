import platforms

class PyPreferences(object):

    manager = None

    def get_manager_cls(self):
        for platform, cls in platforms.platforms.items():
           if cls.is_current_platform():
               return cls.get_manager()

    def __init__(self, namespace, path=None):
        super(PyPreferences, self).__init__()
        manager_cls = self.get_manager_cls()
        self.manager = manager_cls(namespace, path=path)
        self.manager.create(True)

    def __getitem__(self, key):
        return self.manager.get(key)

    def __setitem__(self, key, value):
        self.manager.set(key, value)

    def __delitem__(self, key):
        pass

    def __contains__(self, item):
        try:
            data = self[item]
        except Exception:
            return False
        else:
            return True

    def __len__(self):
        return self.manager.length()
