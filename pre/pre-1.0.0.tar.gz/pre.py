"""這個模組是測試用的"""

#這是第一個function
def firstFun(theList):
    for aa in theList:
        if isinstance(aa,list):
            firstFun(aa)
        else:
            print(aa)

