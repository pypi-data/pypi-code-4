from cellnopt.admin import *
import os

def test_multi_distribute_one():
    d = MultiDistributeRPackage(["CNORdt"], revision="HEAD")
    d.distribute()
    d.help()
    for filename in d.packages_name_rev:
        os.remove(filename)


def test_multi_distribute_all():
    d = MultiDistributeRPackage(revision="HEAD")
    d.distribute()
    for filename in d.packages_name_rev:
        os.remove(filename)
