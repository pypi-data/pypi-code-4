def impLista(theList):
    for item in theList:
        if isinstance(item, list):
            impLista(item)
        else:
            print(item)
