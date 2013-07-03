def print_teams(animals):
        for animal in animals:
                if isinstance(animal, list):
                        print_teams(animal)
                else:
                        print(animal)





