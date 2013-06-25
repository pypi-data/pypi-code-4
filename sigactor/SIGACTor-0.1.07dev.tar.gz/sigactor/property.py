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
            self.province = 'Rif ' + self.post.province
            self.y += self.province + ' comes before "province." '

            self.town = ''
            self.y = 'No town found. '

            if self.post.province in ['Aleppo', 'Hama', 'Homs']:
                self.town = self.post.province
            if self.post.province == 'Raqqah':
                self.town = 'al-Raqqah'
            self.y = 'Town determined by province. '

            self.town = self.parse_location('town', 'city', 'village')

            if self.post.town != '':
                self.town = self.post.town
                self.y = '"' + self.town + '" begins post."'

            for term in ['deir', 'tel']:
                if term in self.activity.clean_words:
                    term_location = self.activity.clean_words.index(term)
                    if len(self.activity.clean_words) > term_location + 1:
                        self.town = (
                            self.activity.words[term_location] +
                            ' ' + self.activity.words[term_location + 1]
                        )
                        self.y = '"' + self.town + '" follows "' + term + '." '
            if self.town == 'the':
                self.value = (
                    self.post.activities[self.number - 1].properties[1].town
                )

            self.neighborhood = self.parse_location(
                'neighborhod', 'neighbourhood'
            )
            if self.neighborhood == 'the':
                self.value = (
                    self.post.activities[self.number - 1].
                    properties[1].neighborhood
                )

            self.area = self.parse_location('area')
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

        if self.name == 'Grid Prec':
            self.value = ''

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
            if self.value == 'Pro-Regime':
                self.activity.orientation = 'Regime'
            else:
                self.activity.orientation = 'Rebel'

        if self.name == 'Ground':
            if self.contains('clashes'):
                self.value = 'Complex'
                self.y = 'Contains "clashes." '

                if self.contains('died', 'killed', 'dead'):
                    self.value = 'DF'
                    self.y += 'Contains "died," "killed," or "dead." '

            self.value = self.check(self.value)
            if self.value != '':
                self.activity.verb = 'Clashes'

        if self.name == 'Air':
            if self.contains('air'):
                self.value = 'UNK Strike'
            if self.contains('helicopter'):
                self.value = 'Rotary Wing Strike'

            self.value = self.check(self.value)
            if self.value != '':
                self.activity.verb = 'Airstrike'

        if self.name == 'Blast':
            if self.contains('bomb ', 'IED'):
                self.value = 'IED'
            if self.contains('car bomb ', 'VBIED'):
                self.value = 'VBIED'

            self.value = self.check(self.value)
            if self.value != '':
                self.activity.verb = self.value

        if self.name == 'Targeted':
            if self.post.contains('execut'):
                self.value = 'Execution'

            self.value = self.check(self.value)
            if self.value != '':
                self.activity.verb = self.value

        if self.name == 'Tactical':
            if self.post.contains('ambush'):
                self.value = 'Ambush'
            if self.post.contains('seize', 'taken'):
                self.value = 'Seize'
            if self.post.contains('raid'):
                self.value = 'Raid'

            self.value = self.check(self.value)

            if self.value != '':
                self.activity.verb = self.value

        if self.name == 'Outcome':
            if self.activity.properties[7] in ['IED', 'VBIED']:
                self.value = 'Effective'
            self.value = self.check(self.value)

        if self.name == 'Full Text':
            self.value = self.post.content

        if self.name == 'URL':
            self.value = self.post.link

        if self.name == 'Source Text':
            self.value = (
                'Syrian Observatory for Human Rights Facebook Page ' +
                str(self.post.short_date)
            )

        if self.name == 'Country Team':
            self.value = 'MESP-Syria'

        if self.name == 'Date Begin':
            self.value = self.post.short_date

        if self.name == 'Date End':
            self.value = self.post.short_date

    def check(self, value):
        while True:
            answer = input(
                "\nIs '" + self.value + "' the correct " + self.name +
                " ? (If correct, press enter. " +
                "Otherwise, enter the correct value or 'n' for none. " +
                "To see why this value was determined, enter 'y') "
            )
            if answer == '':
                return value
            elif answer == 'n':
                return ''
            elif answer == 'y':
                print('\n' + self.y)
            else:
                return answer

    def parse_location(self, *args):
        for arg in args:
            if arg in self.activity.clean_words:
                term_location = self.activity.clean_words.index(arg)

                if len(self.activity.clean_words) > term_location + 2:
                    if self.activity.clean_words[term_location + 1] == 'of':
                        value = self.activity.words[term_location + 2]
                        self.y += (
                            '"' + value + '" occurs after "' + arg + 'of." '
                        )

                        if self.activity.words[term_location + 3][0].isupper():
                            value = (
                                self.activity.words[term_location + 2] + ' ' +
                                self.activity.words[term_location + 3]
                            )

                        if value == 'the':
                            value = ''
                        return value

                value = self.activity.words[term_location - 1]
                if self.activity.words[term_location - 2][0].isupper():
                    value = (
                        self.activity.words[term_location - 2] + ' ' +
                        self.activity.words[term_location - 1]
                    )
                self.y += (
                    '"' + value + '" appears before "' + arg + '." '
                )

                if value == 'the':
                            value = ''
                return value
        return ''

    def contains(self, *args):
        for arg in args:
            isinstance(arg, str)
            if self.activity.clean_content.find(arg) != -1:
                self.y = 'Contains "' + arg + '." '
                return True
        return False
