from __future__ import print_function
def readlist (mylist,level=0):
    for entry in mylist:
        if isinstance(entry, list):
            readlist(entry,level+1)
        else:
            for tab_stop in range(level):
                print("\t",end='')
            print(entry)

