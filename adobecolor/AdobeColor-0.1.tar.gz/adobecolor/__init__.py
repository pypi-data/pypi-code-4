import _aco
from _exceptions import *  # All of the exceptions should be available from the main package

def aco(str_or_file):
    datafile = str_or_file
    if not hasattr(str_or_file, "open"):
        datafile = open(str_or_file, "rb")

    return _aco.Aco(datafile.read())
