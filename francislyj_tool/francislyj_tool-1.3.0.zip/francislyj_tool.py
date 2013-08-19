def printlist(l, indent=False, level=0):
    for i in l:
        if isinstance(i, list):
            printlist(i, indent, level + 1)
        else:
            if indent:
                for tab in range(level):
                    print("\t", end="")
            print(i)
