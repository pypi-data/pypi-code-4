def print_lvl(liste):
    for element in liste:
        if isinstance(element, list):
            print_lvl(element)
        else:
                print(element)
