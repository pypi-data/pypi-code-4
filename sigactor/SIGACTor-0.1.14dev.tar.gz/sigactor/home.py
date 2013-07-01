import csv
from datetime import datetime
import dateutil.tz
import feedparser
from .manual_activity import ManualActivity
import os
from .post import Post
import urllib.request
import yaml


class Home():
    def __init__(self):
        print(
            '\nWelcome to SIGACTor 0.1.11dev, currently available '
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
        self.csv_title = self.today.strftime('%Y-%m-%d-%H%M') + '.csv'
        self.csv_directory = os.path.join(os.path.expanduser('~'), 'SIGACTS')
        self.csv_path = os.path.join(self.csv_directory, self.csv_title)

        if not os.path.exists(self.csv_directory):
            os.makedirs(self.csv_directory)

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

        sohr = urllib.request.urlopen(
            'http://173.230.141.9/sohr.yaml'
        )

        self.sohr = yaml.load(sohr)

        self.entered_date = input(
            '\nPlease enter a starting time. '
            '(YYYY-MM-DD-hhmm, or enter "m" to manually enter an activity) '
        )

        if self.entered_date == 'm':
            self.activities.append(ManualActivity(self))
        else:
            while True:
                self.entered_date += (
                    datetime.now(dateutil.tz.tzlocal()).strftime('%z')
                )

                try:
                    self.start_date = datetime.strptime(
                        self.entered_date, '%Y-%m-%d-%H%M%z'
                    )
                    break
                except ValueError:
                    self.entered_date = input(
                        '\nInvalid answer. '
                        '(Please enter a date in YYYY-MM-DD-hhmm format) '
                    )

            self.stop = False
            for item in self.sohr:
                if self.stop:
                    break

                item_date = item['date'].strftime('%Y-%m-%dT%H:%M:%S') + '+0000'
                item_date = datetime.strptime(item_date, '%Y-%m-%dT%H:%M:%S%z')

                if item_date >= self.start_date:
                    self.posts.append(Post(self, item, item_date))

        print(
            '\nSaved CSV as', self.csv_path,
        )

    def csvwrite(self, values):
        with open(self.csv_path, 'a') as csvfile:
            csvwriter = csv.writer(csvfile, dialect='excel')
            csvwriter.writerow(values)
