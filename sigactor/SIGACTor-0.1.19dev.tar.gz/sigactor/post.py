from .activity import Activity
from .content import Content
from datetime import datetime
import dateutil.tz
from .manual_activity import ManualActivity


class Post():
    def __init__(self, home, item, date):
        self.home = home
        self.item = item

        self.date = date
        self.now = datetime.now(dateutil.tz.tzlocal())
        self.local_timezone = self.now.tzinfo
        self.local_date = self.date.astimezone(self.local_timezone)
        self.short_date = self.local_date.strftime('%Y-%m-%d')
        self.time = self.local_date.strftime('%Y-%m-%d-%H%M')

        self.link = self.item['link']

        self.content = self.item['content']

        while(
            self.content.find('<a') != -1 and
            self.content.find('</a>') != -1
        ):
            link_begins = self.content.find('<a')
            link_ends = self.content.find('</a>') + 4
            self.content = self.content.replace(
                self.content[link_begins:link_ends], ''
            )

        self.content = self.content.replace('<br/>', '')

        self.content = Content(self.content)

        self.province = self.content.locate('province')

        for term in ['reef', 'rif']:
            if self.content.contains(term):
                self.province = self.content.locate(term)

        if not self.province:
            sentence = Content(self.content.sentences[0])
            if sentence.is_proper(0):
                self.province = sentence.words[0]

        self.strategic_terms = [
            'clash',
            'bomb ',
            ' ied ',
            'vbied',
            'air',
            'helicopter',
            'seize',
            'capture',
            'taken over',
            'take control',
            'ambush',
            'raid',
            'suicide',
            'jet',
        ]

        self.contents = []
        self.strategic_sentences = []
        if not(self.content.clean_text.startswith(
            'final death toll for'
        )):
            for sentence in self.content.sentences:
                include = False

                sentence = Content(sentence)

                for term in self.strategic_terms:
                    if sentence.contains(term):
                        include = True

                if include:
                    if(
                        sentence.clean_words[0] in
                        ['he', 'she', 'it', 'we', 'they'] and
                        len(self.strategic_sentences) > 1
                    ):
                        self.strategic_sentences[-1] += '. ' + sentence.text
                    else:
                        self.strategic_sentences.append(sentence.text)

        self.elements = [
            ['factory', 'factories'],
            ['church', 'churches'],
            ['mosque', 'mosques'],
            ['hospital', 'hospitals'],
            ['military hospital', 'military hospitals'],
            ['prison', 'prisons'],
            ['airport', 'airports'],
            ['civilian airport', 'civilian airports'],
            ['military airport', 'military airports'],
            ['road', 'roads'],
            ['street', 'streets'],
            ['highway', 'highways'],
            ['area', 'areas'],
            ['neighborhood', 'neighborhoods'],
            ['neighbourhood', 'neighbourhoods'],
            ['village', 'villages'],
            ['suburb', 'suburbs'],
            ['town', 'towns'],
            ['city', 'cities'],
            ['province', 'provinces'],
        ]

        for sentence in self.strategic_sentences:
            sentence = Content(sentence)

            for element in self.elements:
                if sentence.contains(element[1]):
                    pass

        answer = self.layout()

        while True:
            if answer == '':
                for number in range(0, len(self.strategic_sentences)):
                    home.activities.append(Activity(
                        self.home,
                        self,
                        self.strategic_sentences[number],
                        number
                    ))
                break
            if answer == 'q':
                self.home.stop = True
                break
            if answer == 'm':
                self.home.activities.append(ManualActivity(home))
                answer = self.layout()
                continue
            try:
                answer = int(answer)
            except ValueError:
                answer = input(
                    '\nInvalid answer. '
                    '(Press Enter if the activities are divided correctly '
                    'or enter the correct number of activities) '
                )
                continue
            else:
                answer = int(answer)
                self.strategic_sentences = []
                for number in range(0, answer):
                    text = input(
                        '\nEnter the content of activity ' +
                        str(number + 1) + ': '
                    )
                    self.strategic_sentences.append(text)
                answer = ''

    def layout(self):
        print('\nPost content (' + self.time + '):\n' + self.content.text)

        print(
            '\nAre there', str(len(self.strategic_sentences)),
            'activities in this post',
            'with the following contents:'
        )

        for number in range(0, len(self.strategic_sentences)):
            print(
                '\n' + str(number + 1) + ': ' +
                self.strategic_sentences[number]
            )

        return input(
            '\n? (If correct, press Enter. '
            'Otherwise, enter the number of activities in this post. '
            'Enter "m" to enter an activity manually, or '
            'enter "q" to finish entering posts) '
        )
