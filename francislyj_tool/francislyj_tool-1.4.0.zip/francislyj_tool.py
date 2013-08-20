import sys


def printlist(l, indent=False, level=0, fl=sys.stdout):
    for i in l:
        if isinstance(i, list):
            printlist(i, indent, level + 1, fl)
        else:
            if indent:
                for tab in range(level):
                    print("\t", end="", file=fl)
            print(i, file=fl)
