from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime
from .activity import Activity


class Post():
    def __init__(self, home, link):
        self.home = home
        self.link = link

        self.data = urlopen(self.link)
        self.data = self.data.read()
        self.data = BeautifulSoup(self.data)
        self.data = str(self.data)

        self.date = self.search('data-utime="', '"', self.data)
        self.date = int(self.date)
        self.date = datetime.fromtimestamp(self.date).strftime('%Y-%m-%d')

        self.content = self.search(
            '<span class="userContent">', '</span>', self.data
        )
        print('\nPost content:\n' + self.content)
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

        self.sentences = self.clean_content.split('. ')
        self.contents = []

        self.strategic_terms = [
                'clash',
                'bomb ',
                'ied',
                'vbied',
                'air',
                'helicopter',
                'seize',
                'capture',
                'taken over',
                'take control',
                'ambush',
                'raid',
            ]

        for sentence in self.sentences:
            words = sentence.split()

            include = False
            for term in self.strategic_terms:
                if sentence.find(term) != -1:
                    include = True

            if include == True:
                if words[0].lower() in ['he', 'she', 'it', 'we', 'they']:
                    self.contents[-1] += '. ' + sentence
                else:
                    self.contents.append(sentence)

        print(
            '\nAre there ' + str(len(self.contents)) +
            ' activities in this post '
            'with the following contents:'
        )

        for number in range(0, len(self.contents)):
            print('\n' + str(number + 1) + ': ' + self.contents[number])

        answer = input(
            '\n? (If correct, press Enter. '
            'Otherwise, enter the number of activities in this post) '
        )

        while True:
            if answer == '':
                for number in range(0, len(self.contents)):
                    home.activities.append(Activity(
                        self.home, self, self.contents[number], number
                    ))
                break
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
