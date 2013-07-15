class Property():
    def __init__(self, home, post, activity, name):
        self.home = home
        self.post = post
        self.activity = activity
        self.name = name

        self.value = ''
        self.y = ''

        if self.name == 'Title':
            self.value = ''

        if self.name == 'Location':
            self.elements = [
                'mosque',
                'prison',
                'airport',
                'civilian airport',
                'military airport',
                'road',
                'street',
                'highway',
                'area',
                'neighborhood',
                'neighbourhood',
                'village',
                'town',
                'city',
                'province',
            ]

            self.units = {}

            for number in range(0, len(self.elements)):
                if number <= 7:
                    self.units[self.elements[number]] = (
                        self.activity.content.locate(
                            self.elements[number], tag=True
                        )
                    )
                else:
                    self.units[self.elements[number]] = (
                        self.activity.content.locate(self.elements[number])
                    )

            if self.post.province:
                self.units['province'] = self.post.province
                self.y += 'Province determined by post. '

            if self.units['province'].lower() == 'damascus':
                self.units['province'] = 'Dimashq'

            if not self.units['town']:
                if self.units['province'] in ['Aleppo', 'Hama', 'Homs']:
                    self.town = self.post.province
                    self.y += 'Town determined by province. '
                if self.units['province'] == 'Raqqah':
                    self.units['town'] = 'al-Raqqah'
                    self.y += 'Town determined by province. '
                if self.units['province'] == 'Dimashq':
                    self.units['town'] = 'Damascus'
                    self.y += 'Town determined by province. '

            self.units['province'] = 'Rif ' + self.units['province']

            for element in self.elements:
                if self.units[element].lower() == 'the':
                    if len(self.post.activities):
                        self.units[element] = (
                            self.post.activities[self.activity.number - 1]
                            .properties[1].units[element]
                        )

                if self.units[element]:
                    self.value += self.units[element] + ', '

            if self.value:
                if self.value[-2:] == ', ':
                    self.value = self.value[:-2]

            self.value = self.check(self.value)
            self.activity.location = self.value

        if self.name == 'Lat-Long':
            self.value = ''
            my_location = self.activity.properties['Location'].value

            for location in self.home.locations:
                if my_location in location['names']:
                    self.value = location['Lat-Long']

        if self.name == 'Grid Prec':
            self.value = ''
            my_location = self.activity.properties['Location'].value

            for location in self.home.locations:
                if my_location in location['names']:
                    self.value = location['Grid Prec']

        if self.name == 'Description':
            self.value = self.activity.content.text
            self.value = self.check(self.value)

        if self.name == 'Orientation':
            self.value = 'Anti-regime'

            if self.activity.content.contains('regime forces'):
                self.value = 'Pro-regime'
                self.y = 'Contains "regime force." '
            else:
                self.y = 'Does not contain "regime forces." '

            if(
                self.activity.content.contains('air') or
                self.activity.content.contains('helicopter')
            ):
                self.value = 'Pro-regime'

            self.value = self.check(self.value)

        if self.name == 'Ground':
            if self.activity.content.contains('clashes'):
                self.value = 'Complex'
                self.y = 'Contains "clashes." '

                if self.activity.content.contains('died', 'killed', 'dead'):
                    self.value = 'DF'
                    self.y += 'Contains "died," "killed," or "dead." '

            self.value = self.check(self.value)

        if self.name == 'Air':
            if self.activity.content.contains('air'):
                self.value = 'UNK Strike'
            if self.activity.content.contains('helicopter'):
                self.value = 'Rotary Wing Strike'
            if self.activity.content.contains('targeted a fighter-jet'):
                self.value = 'Ground-to-Air'

            self.value = self.check(self.value)

            if self.value:
                self.activity.properties['Orientation'].value = 'Pro-Regime'
            if self.value == 'Ground-to-Air':
                self.activity.properties['Orientation'].value = 'Anti-Regime'

        if self.name == 'Blast':
            if self.activity.content.contains('bomb ', 'IED', 'bomber'):
                self.value = 'IED'
            if self.activity.content.contains('car bomb ', 'VBIED'):
                self.value = 'VBIED'
            if self.activity.content.contains('suicide'):
                self.value = 'SVEST'

            self.value = self.check(self.value)

        if self.name == 'Targeted':
            if self.activity.content.contains('execut'):
                self.value = 'Execution'

            self.value = self.check(self.value)

        if self.name == 'Tactical':
            if self.activity.content.contains('ambush'):
                self.value = 'Ambush'
            if self.activity.content.contains('seize', 'taken'):
                self.value = 'Seize'
            if self.activity.content.contains('raid'):
                if not self.activity.content.contains('air raid'):
                    self.value = 'Raid'

            self.value = self.check(self.value)

        if self.name == 'Outcome':
            if self.activity.properties['Blast'].value:
                self.value = 'Effective'
            else:
                self.value = ''

            self.value = self.check(self.value)

        if self.name == 'Full Text':
            self.value = self.post.content.text

        if self.name == 'URL':
            self.value = self.post.link

        if self.name == 'Source Text':
            self.value = (
                'Syrian Observatory for Human Rights Facebook Page ' +
                self.post.date.strftime('%B %d %Y')
            )

        if self.name == 'Country Team':
            self.value = 'MESP-Syria'

        if self.name == 'Date Begin':
            self.value = self.post.short_date

        if self.name == 'Date End':
            self.value = self.post.short_date

        if self.name == 'Posted Date':
            self.value = self.post.time

    def check(self, value):

        while True:
            answer = input(
                '\nContent:\n' + self.activity.content.text + '\n' +
                '\nIs "' + self.value + '" the correct ' + self.name +
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
                self.activity.restart = True
                return ''
            else:
                return answer
