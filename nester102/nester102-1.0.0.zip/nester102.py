"""test"""
def lol(the_list):
    """the blank key is horrible."""
    for le in the_list:
        if isinstance(le,list):
            lol(le)
        else:
            print(le)
