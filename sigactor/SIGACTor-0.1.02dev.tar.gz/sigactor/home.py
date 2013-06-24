from datetime import datetime
import csv
import feedparser
from post import Post


class Home():
    def __init__(self):
        self.feed = feedparser.parse('http://www.facebook.com/feeds/page.php?format=atom10&id=121855461256134')
        print(self.feed['feed']['title'])

        print(
            '\nWelcome to SIGACTor, currently available '
            'for the Syria team and reading posts from the '
            "Syrian Observatory for Human Rights' Facebook Page."
        )

        self.properties = [
            'Title',
            'Location',
            'Lat-Long',
            'Grid Prec',
            'Description',
            'Orientation',
            'Ground',
            'Blast',
            'Air',
            'Targeted',
            'Tactical',
            'Outcome',
            'Full Text',
            'URL',
            'Source Text',
            'Country Team',
            'Date Begin',
            'Date End',
        ]

        print('\nPreparing CSV...')
        self.today = datetime.now()
        self.document_title = self.today.strftime('%Y-%m-%dT%H-%M') + '.csv'

        self.csvwrite(self.properties)

        self.unchecked_values = [
            'Title',
            'Lat-Long',
            'Grid Prec',
            'Full Text',
            'URL',
            'Source Text',
            'Country Team',
            'Date Begin',
            'Date End',
        ]

        self.posts = []
        self.activities = []

        while True:
            answer = input(
                '\nPlease enter a permalink to a post '
                "from the Syrian Observatory for Human Rights' "
                'Facebook page. (To finish entering posts, press Enter) '
            )
            if answer == '':
                break
            elif answer[:40] == 'https://www.facebook.com/syriaohr/posts/':
                self.posts.append(Post(self, answer))
            else:
                answer = input(
                    '\nInvalid answer. (Please enter a link to permalink '
                    'to a post from the '
                    "Syrian Observatory for Human Rights' "
                    'Facebook page, or press Enter '
                    'to finish entering posts.) '
                )

        print(
            '\nSaved CSV as', self.document_title,
        )

    def csvwrite(self, values):
        with open(self.document_title, 'a', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, dialect='excel')
            csvwriter.writerow(values)
