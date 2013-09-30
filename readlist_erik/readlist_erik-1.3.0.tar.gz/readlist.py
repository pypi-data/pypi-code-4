from __future__ import print_function
def readlist (mylist,uselevel=False,level=0):
    for entry in mylist:
        if isinstance(entry, list):
            readlist(entry,uselevel,level+1)
        else:
            if uselevel:
                for tab_stop in range(level):
                    print("\t",end='')
            print(entry)

