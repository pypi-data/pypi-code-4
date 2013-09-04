from ConfigParser import SafeConfigParser
from copy import deepcopy
import os

from tod.links import expand

def parse_repo_mapping(path):
    mapping_file = os.path.join(path, 'mapping.ini')
    parser = SafeConfigParser()
    parser.read(mapping_file)
    mapping = {}
    for s in parser.sections():
        mapping[s] = {c[0]:c[1] for c in parser.items(s)}
    return mapping
