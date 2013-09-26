"""test"""
def lol(the_list, k):
    """the blank key is horrible."""
    for le in the_list:
        if isinstance(le,list):
            lol(le,k+1)
        else:
            for sth in range(k):
                print("\t", end='')
            print(le)
