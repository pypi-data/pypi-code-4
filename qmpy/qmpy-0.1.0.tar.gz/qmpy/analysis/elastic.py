from qmpy.utils import *
from symmetry import *

transforms = [ 
        [[0.1, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.1, 0.0],
         [0.0, 0.0, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.0, 0.1]],

        [[0.0, 0.0, 0.0],
         [0.1, 0.0, 0.0],
         [0.0, 0.0, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.0, 0.1, 0.0]],

        [[0.0, 0.0, 0.0],
         [0.0, 0.0, 0.0],
         [0.1, 0.0, 0.0]]]

def get_unique_transforms(rotations):
    uniq_transforms = list(transforms)
    for rot in rotations:

