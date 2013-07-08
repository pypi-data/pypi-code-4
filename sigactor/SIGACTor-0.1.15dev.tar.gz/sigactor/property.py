class Property():
    def __init__(self, home, post, activity, name):
        self.home = home
        self.post = post
        self.activity = activity
        self.name = name

        self.value = ''
        self.y = ''

        if self.name not in self.home.unchecked_values:
            print('\nContent:\n' + self.activity.content)

        if self.name == 'Title':
            self.value = ''

        if self.name == 'Location':
            self.province = self.locate('province')
            if self.post.province != '':
                self.province = 'Rif ' + self.post.province
            self.y += self.province + ' comes before "province." '

            self.town = ''
            if self.post.province in ['Aleppo', 'Hama', 'Homs']:
                self.town = self.post.province
                self.y += 'Town determined by province. '
            if self.post.province == 'Raqqah':
                self.town = 'al-Raqqah'
                self.y += 'Town determined by province. '
            if self.post.province == 'Dimashq':
                self.town = 'Damascus'
                self.y += 'Town determined by province. '

            self.town = self.locate('town', 'city', 'village')

            for term in ['deir', 'tel']:
                if term in self.activity.clean_words:
                    index = self.activity.clean_words.index(term)
                    if len(self.activity.clean_words) > index + 1:
                        self.town = (
                            self.activity.words[index] +
                            ' ' + self.activity.words[index + 1]
                        )
                        self.y += (
                            '"' + self.town + '" follows "' + term + '." '
                        )
            if self.town == 'the':
                self.value = (
                    self.post.activities[self.number - 1].properties[1].town
                )

            self.neighborhood = self.locate(
                'neighborhood',
                'neighbourhood',
            )
            if self.neighborhood == 'the':
                self.value = (
                    self.post.activities[self.number - 1].
                    properties[1].neighborhood
                )

            self.area = self.locate('area', )
            if self.area == 'the':
                self.value = (
                    self.post.activities[self.number - 1].properties[1].area
                )

            if self.area == '':
                self.y += '"Area" does not occur. '
            if self.neighborhood == '':
                self.y += '"Neighborhood" does not occur. '
            if self.town == '':
                self.y += '"Town" does not occur. '
            if self.province == '':
                self.y += '"Province" does not occur.'

            for term in [
                self.area, self.neighborhood, self.town, self.province
            ]:
                if term != '':
                    self.value += term + ', '
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
            self.value = self.activity.content
            self.value = self.check(self.value)

        if self.name == 'Orientation':
            self.value = 'Anti-regime'

            if self.contains('regime forces'):
                self.value = 'Pro-regime'
                self.y = 'Contains "regime force." '
            else:
                self.y = 'Does not contain "regime forces." '

            if self.contains('air') or self.contains('helicopter'):
                self.value = 'Pro-regime'

            self.value = self.check(self.value)

        if self.name == 'Ground':
            if self.contains('clashes'):
                self.value = 'Complex'
                self.y = 'Contains "clashes." '

                if self.contains('died', 'killed', 'dead'):
                    self.value = 'DF'
                    self.y += 'Contains "died," "killed," or "dead." '

            self.value = self.check(self.value)

        if self.name == 'Air':
            if self.contains('air'):
                self.value = 'UNK Strike'
            if self.contains('helicopter'):
                self.value = 'Rotary Wing Strike'
            if self.contains('targeted a fighter-jet'):
                self.value = 'Ground-to-Air'

            self.value = self.check(self.value)

            if self.value != '':
                self.activity.properties['Orientation'].value = 'Pro-Regime'
            if self.value == 'Ground-to-Air':
                self.activity.properties['Orientation'].value = 'Anti-Regime'

        if self.name == 'Blast':
            if self.contains('bomb ', 'IED', 'bomber'):
                self.value = 'IED'
            if self.contains('car bomb ', 'VBIED'):
                self.value = 'VBIED'
            if self.contains('suicide'):
                self.value = 'SVEST'

            self.value = self.check(self.value)

        if self.name == 'Targeted':
            if self.post.contains('execut'):
                self.value = 'Execution'

            self.value = self.check(self.value)

        if self.name == 'Tactical':
            if self.post.contains('ambush'):
                self.value = 'Ambush'
            if self.post.contains('seize', 'taken'):
                self.value = 'Seize'
            if self.post.contains('raid'):
                self.value = 'Raid'

            self.value = self.check(self.value)

        if self.name == 'Outcome':
            if self.activity.properties['Blast'].value != '':
                self.value = 'Effective'
            else:
                self.value = ''

            self.value = self.check(self.value)

        if self.name == 'Full Text':
            self.value = self.post.content

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

    def locate(self, *args):
        value = ''
        for arg in args:
            if arg in self.activity.clean_words:
                index = self.activity.clean_words.index(arg)

                if len(self.activity.clean_words) > index + 2:
                    if self.activity.clean_words[index + 1] == 'of':
                        if self.activity.words[index + 2] != 'the':
                            value = self.activity.words[index + 2]
                        self.y += (
                            '"' + value + '" occurs after "' + arg + 'of." '
                        )

                        if len(self.activity.clean_words) > index + 3:
                            if (
                                self.activity.words
                                [index + 3][0].isupper()


                            ):
                                value = (
                                    self.activity.words[index + 2] +
                                    ' ' +
                                    self.activity.words[index + 3]
                                )

                        if self.activity.words[index - 1][0].isupper():
                            if value != '':
                                value = (
                                    self.activity.words[index - 1] +
                                    ', ' + value
                                )
                            else:
                                value = self.activity.words[index - 1]

                        if self.activity.words[index - 2][0].isupper():
                            value = (
                                self.activity.words[index - 2] + ' ' + value
                            )

                        if value == 'the':
                            value = ''
                        return value

                value = self.activity.words[index - 1]
                if self.activity.words[index - 2][0].isupper():
                    value = (
                        self.activity.words[index - 2] + ' ' +
                        self.activity.words[index - 1]
                    )
                self.y += (
                    '"' + value + '" appears before "' + arg + '." '
                )

                if value == 'the':
                    value = ''
                return value

        value = ''
        return value

    def contains(self, *args):
        for arg in args:
            if self.activity.clean_content.find(arg) != -1:
                self.y = 'Contains "' + arg + '." '
                return True
        return False
