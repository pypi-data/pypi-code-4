from .content import Content
from .property import Property


class Activity():
    def __init__(self, home, post, text, number):
        self.home = home
        self.post = post
        self.text = text
        self.number = number

        self.content = Content(text)

        self.define_properties()

        if self.properties['Orientation'].value == 'Pro-regime':
            self.actor = 'Regime'
        else:
            self.actor = 'Rebel'

        self.verb = ''
        if self.properties['Ground'].value != '':
            self.verb = 'Clashes'
        if self.properties['Air'].value != '':
            self.verb = 'Airstrike'
        if self.properties['Air'].value == 'Ground-to-Air':
            self.verb = self.properties['Air'].value
        if self.properties['Blast'].value != '':
            self.verb = self.properties['Blast'].value
        if self.verb == '' and self.properties['Targeted'].value != '':
            self.verb = self.properties['Targeted'].value
        if self.properties['Tactical'].value != '':
            self.verb = self.properties['Tactical'].value

        self.properties['Title'].value = (
            self.post.short_date + " SYR " + self.actor + ' ' +
            self.verb + ' IVO ' + self.properties['Location'].value
        )

        self.fields = []
        for property in self.home.properties:
            self.fields.append(self.properties[property].value)

        home.csvwrite(self.fields)

    def define_properties(self):
        self.properties = {}
        self.restart = False
        for property in self.home.properties:
            if self.restart:
                self.define_properties()
                break
            self.properties[property] = (Property(
                self.home, self.post, self, property
            ))
