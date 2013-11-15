import dj.utils


class Context:
    name = None
    path = None

    def __init__(self):
        self.refresh()

    def refresh(self):
        self.root = dj.utils.find_project_root()
        self.name = dj.utils.find_project_name(self.root)

    def update(self, root, name):
        self.root = root
        self.name = name
