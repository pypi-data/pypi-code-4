
def print_lol(raw_list, indent=False, level=0):
    for element in raw_list:
        if isinstance (element, list):
            print_lol(element, indent, level + 1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')

            print (element)
    return
