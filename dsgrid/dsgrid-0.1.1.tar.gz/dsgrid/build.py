from adapter import DockerAdapter
import os
from subprocess import call



class GridBuilder:

    def __init__(self):
        self.adapter = DockerAdapter()

    def is_installed(self):
        container = self.adapter.find_image('dsgrid/selenium-hub')
        return container

    def build(self, container):
        if container == 'phantomjs':
            if not os.path.exists('files/phantomjs'):
                return False
            self.adapter.client.build('files/phantomjs', 'dsgrid/phantomjs-node')
            return True

        if container == 'firefox':
            if not os.path.exists('files/firefox'):
                return False
            self.adapter.client.build('files/firefox', 'dsgrid/firefox-node')
            return True

        if container == 'selenium-hub':
            if not os.path.exists('files/selenium'):
                return False
            self.adapter.client.build('files/selenium', 'dsgrid/selenium-hub')
            return True

        return False





