from .activity import Activity
from bs4 import BeautifulSoup
from datetime import datetime
import dateutil.tz
from .manual_activity import ManualActivity


class Post():
    def __init__(self, home, item, date):
        self.home = home
        self.item = item

        self.date = date
        self.now = datetime.now(dateutil.tz.tzlocal())
        self.timezone_info = self.now.tzinfo
        self.current_date = self.date.astimezone(self.timezone_info)
        self.short_date = self.current_date.strftime('%Y-%m-%d')
        self.time = self.current_date.strftime('%Y-%m-%d-%H%M')

        self.link = self.item['link']
        self.content = self.item['content']

        self.clean_content = self.content.translate(str.maketrans('', '', ':'))
        self.words = self.clean_content.split()

        self.province = ''
        if len(self.words) > 1:
            if 'province' in self.words:
                term_location = self.words.index('province')
                self.province = self.words[term_location - 1]
                if self.words[1] == 'province':
                    term_location = self.clean_content.find('province')
                    self.clean_content = (
                        self.clean_content[term_location + 9:]
                    )

        if self.words[0].lower() in ['rif', 'reef']:
            self.province = self.words[1]
            second_space = self.clean_content.replace(' ', '', 1).find(' ')
            self.clean_content = self.clean_content[second_space + 2:]

        self.town = ''
        if self.words[0].lower() == 'damascus':
            self.province = 'Dimashq'
            if self.clean_content[:8].lower() == 'damascus':
                self.clean_content = self.clean_content[9:]
            self.town = 'Damascus'

        self.clean_content.replace('.<br/>', '. ')
        self.sentences = self.clean_content.split('. ')
        self.contents = []

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
            'fighter-jet',
        ]

        for sentence in self.sentences:
            words = sentence.split()

            include = False
            for term in self.strategic_terms:
                if self.contains(sentence.lower(), term):
                    include = True

            if include:
                if words[0].lower() in ['he', 'she', 'it', 'we', 'they']:
                    self.contents[-1] += '. ' + sentence
                else:
                    self.contents.append(sentence)

        answer = self.layout()   

        while True:
            if answer == '':
                for number in range(0, len(self.contents)):
                    home.activities.append(Activity(
                        self.home, self, self.contents[number], number
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
                self.contents = []
                for number in range(0, answer):
                    content = input(
                        '\nEnter the content of activity ' +
                        str(number + 1) + ': '
                    )
                    self.contents.append(content)
                answer = ''

    def search(self, start_tag, end_tag, subject=None):
        if subject is None:
            subject = self.content
        start = subject.find(start_tag) + len(start_tag)
        end = subject[start:].find(end_tag)
        return subject[start:start + end]

    def contains(self, subject, *args):
        for arg in args:
            if (
                isinstance(arg, str)
            ):
                if subject.find(arg) != -1:
                    return True
            else:
                for element in arg:
                    if subject.find(element) != -1:
                        return True
        return False
    
    def layout(self):
        print('\nPost content (' + self.time + '):\n' + self.content)

        print(
            '\nAre there ' + str(len(self.contents)) +
            ' activities in this post '
            'with the following contents:'
        )

        for number in range(0, len(self.contents)):
            print('\n' + str(number + 1) + ': ' + self.contents[number])

        return input(
            '\n? (If correct, press Enter. '
            'Otherwise, enter the number of activities in this post. '
            'Enter "m" to enter an activity manually, or '
            'enter "q" to finish entering posts) '
        )
