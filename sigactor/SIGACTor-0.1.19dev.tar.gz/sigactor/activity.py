from .content import Content
from .property import Property


class Activity():
    def __init__(self, home, post, text, number):
        self.home = home
        self.post = post
        self.text = text
        self.number = number

        self.content = Content(text)

        while True:
            self.properties = {}
            self.restart = False
            for property in self.home.properties:
                if self.restart:
                    break
                self.properties[property] = (Property(
                    self.home, self.post, self, property
                ))
            else:
                break
            continue

        self.subject = 'UNK'
        self.object = 'UNK'

        if self.properties['Orientation'].value == 'Pro-regime':
            self.subject = 'Regime'
            self.object = 'Rebel'
        else:
            self.subject = 'Rebel'
            self.object = 'Regime'

        self.check(self.subject, 'subject')
        self.check(self.object, 'object')

        self.verb = ''
        if self.properties['Ground'].value != '':
            self.verb = 'Clashed with'
        if self.properties['Air'].value != '':
            self.verb = 'Airstrike on'
        if self.properties['Air'].value == 'Ground-to-Air':
            self.verb = self.properties['Air'].value
        if self.properties['Blast'].value != '':
            self.verb = self.properties['Blast'].value
        if self.verb == '' and self.properties['Targeted'].value != '':
            self.verb = self.properties['Targeted'].value
        if self.properties['Tactical'].value != '':
            self.verb = self.properties['Tactical'].value

        self.check(self.verb, 'verb')

        self.properties['Title'].value = (
            self.post.short_date + " SYR " + self.subject + ' ' +
            self.verb + ' ' + self.object + ' ' + ' IVO ' +
            self.properties['Location'].value
        )

        self.fields = []
        for property in self.home.properties:
            self.fields.append(self.properties[property].value)

        home.csvwrite(self.fields)

    def check(self, value, name):
        while True:
            answer = input(
                '\nContent:\n' + self.content.text + '\n' +
                '\nIs "' + value + '" the correct ' + name +
                ' ? (If correct, press enter. ' +
                'Otherwise, enter the correct value or "n" for none. '
                'To see why this value was determined, enter "y." '
                'To restart processing this activity, enter "r") '
            )
            if answer == '':
                return value
            elif answer == 'n':
                return ''
            elif answer == 'y':
                print('\n' + self.y)
            elif answer == 'r':
                self.restart = True
                return ''
            else:
                return answer
