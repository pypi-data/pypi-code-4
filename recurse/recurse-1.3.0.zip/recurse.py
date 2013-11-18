def printlol(thelist, indent=True, level=0):
    for eachitem in thelist:
        if isinstance(eachitem, list):
            printlol(eachitem, indent, level+1)
        else:
            if indent:
                for tabstop in range(level):
                    print("\t" * level, end='')
            print(eachitem)
