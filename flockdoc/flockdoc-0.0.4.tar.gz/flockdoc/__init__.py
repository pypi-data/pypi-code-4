import sys
import os

__version__ = '0.0.4'

if 'templates' in os.listdir(os.path.dirname(__file__)):
    template_path = 'flockdoc/templates'  # relative to the root directory
else:
    template_path = os.path.join(sys.prefix, 'flockdoc/templates')
