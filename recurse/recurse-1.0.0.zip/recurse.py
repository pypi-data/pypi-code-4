def printlol(thelist):
    for eachitem in thelist:
        if isinstance(eachitem, list):
            printlol(eachitem)
        else:
            print(eachitem)
