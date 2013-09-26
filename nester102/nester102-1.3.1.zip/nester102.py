"""test"""
def lol(the_list, n=False, k=0):
    """the blank key is horrible."""
    for le in the_list:
        if isinstance(le,list):
            lol(le, n, k+1)
        else:
            if n=False:
                print(le)
            else:
                for sth in range(k):
                print("\t", end='')
                print(le)
