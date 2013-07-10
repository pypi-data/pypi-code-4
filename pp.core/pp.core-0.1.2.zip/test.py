# -*- encoding: utf-8 -*-

import sys
from pp.core.fslayer import Filesystems
from pp.core.project import Project
from pp.core.project import PublishingLocation

fs = Filesystems(sys.argv[1])

source = Project(fs['localfs'], u'Mein schönes Projekt')
source.create_structure()
source.create_demo_content()

target = PublishingLocation(fs['aws'], u'My target')
target.create_structure()
