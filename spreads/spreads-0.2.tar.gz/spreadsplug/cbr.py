from spreads.plugin import HookPlugin


class CBRPlugin(HookPlugin):
    def __init__(self, config):
        pass

    def process(self, path):
        # TODO: Convert all files from 'done' to JPG in a temporary directory
        # TODO: Create RAR from tempdir and name it according to the project
        raise NotImplementedError
