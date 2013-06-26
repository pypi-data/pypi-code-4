from .property import Property


class Activity():
    def __init__(self, home, post, content, number):
        self.home = home
        self.post = post
        self.content = content
        self.number = number

        self.clean_content = self.content.lower()
        self.clean_content = self.clean_content.translate(
            str.maketrans('', '', ',')
        )

        self.words = self.content.split()

        self.clean_words = self.clean_content.split()

        self.location = ''
        self.orientation = ''
        self.verb = ''

        self.define_properties()

        self.properties[0].value = (
            self.post.short_date + " SYR " + self.orientation + ' ' +
            self.verb + ' IVO ' + self.location
        )

        self.fields = []
        for property in self.properties:
            self.fields.append(property.value)

        home.csvwrite(self.fields)

    def define_properties(self):
        self.properties = []
        self.restart = False
        for property in self.home.properties:
            if self.restart:
                self.restart = False
                self.define_properties()
                break
            self.properties.append(Property(
                self.home, self.post, self, property
            ))
