import os
import sys

dir = os.path.dirname(__file__)
sys.path.append(dir)

for module in os.listdir(dir):
    if module == '__init__.py' or module[-3:] != '.py':
        continue
    __import__(module[:-3], locals(), globals())
del module
