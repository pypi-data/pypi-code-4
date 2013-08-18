# coding: utf-8
import sys

VERSION = '0.0.3'

if sys.version_info[0] == 2:
    from gat_python.truco_algorithm import TrucoAlgorithm
else:
    from .truco_algorithm import TrucoAlgorithm
