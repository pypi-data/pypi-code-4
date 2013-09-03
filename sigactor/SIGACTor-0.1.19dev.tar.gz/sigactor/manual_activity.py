from .activity import Activity


class ManualActivity():
    def __init__(self, home):
        self.home = home

        content = input("\nWhat is the activity's content? ")

        properties = []
        for property in home.properties:
            print('\nContent:\n' + content)

            properties += input("\nWhat is the activity's " + property + '? ')

        home.csvwrite(properties)
