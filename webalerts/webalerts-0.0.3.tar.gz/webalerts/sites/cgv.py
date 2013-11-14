# -*- coding: UTF-8 -*-
from collections import Iterable, OrderedDict, namedtuple
from datetime import datetime, timedelta
from logging import getLogger
import re
from textwrap import dedent

import pytz

from webalerts import (Browser, Post, ConfigurationError, LoginError, utcnow,
                       cached, parse_html, urlencode_utf8)


class CGV(object):
    """
    Implementation for `CGV Cinemas`_. Get notified and get the best
    seat! Don't forget setting ``patterns`` to `None` in configuration for this
    site.

    Configuration options:

    ``username``
      CGV username.

    ``password``
      CGV password.

    ``data``
      List of tuples (``movie_name``, ``movie_format``, ``theater_name``,
      ``time_range``, ``date_range``, ``seat_range``).
      You will be notified if any of the specified seats in the specified date
      and time range for the specified movie, format, and theater is found.
      All strings containing non-ASCII characters must be unicode. Movie,
      format, and theater names should be exact matches. It is recommended to
      find those in `the official site`__.

      ``time_range`` is a tuple of length 2, consisting of strings for times in
      HH:MM format. Hour can be larger than 23, so ``'25:00'`` is a valid time string.
      If you do not want to restrict times, set it to `None`.

      ``date_range`` is a list of strings, either date in yyyymmdd format or short
      weekday names such as 'mon', 'fri'. ``'weekdays'`` and ``'weekends'`` are
      shortcuts for ``['mon', 'tue', 'wed', 'thu', 'fri']`` and ``['sat', 'sun']``
      respectively. 'today' is the current date in Korea Standard Time (UTC+9).

      ``seat_range`` is a list of seat names such as 'A1' and 'F18'.

      The following is an example tuple: ``(u'그래비티', 'IMAX3D', u'왕십리', ('18:00', '24:30'), ['1130', 'fri', 'weekends'], ['F16', 'F17', 'G16', 'G17'])``

    .. _`CGV Cinemas`: http://m.cgv.co.kr/

    __ `CGV Cinemas`_

    """

    def __init__(self, config):
        self.config = config
        self.logger = getLogger(__name__).getChild(self.__class__.__name__)
        self._api = CGVAPI(config.get('username'), config.get('password'))
        self._seat_data = {}

    def get_new_posts(self):
        posts = []
        data = self.config.get('data', [])
        if not isinstance(data, Iterable):
            raise ConfigurationError('data should be iterable')

        # Prevent self._seat_data growing indefinitely, by removing old records.
        yesterday = (self._today_in_seoul() - timedelta(days=1)).strftime('%Y%m%d')
        old_keys = []
        for theater, date, play in self._seat_data:
            if date < yesterday:
                old_keys.append((theater, date, play))
        for key in old_keys:
            del self._seat_data[key]

        # Caches for dates and times for a short time
        dates_cache = {}
        times_cache = {}

        for movie_name, movie_format, theater_name, time_r, date_r, seat_r in data:
            movie, format, theater = self._get_objects(movie_name, movie_format, theater_name)
            dates = self._get_dates(dates_cache, movie, format, theater, date_r)
            for date in dates:
                times = self._get_times(times_cache, movie, format, theater, date, time_r)
                for play_state in times:
                    play = play_state.play
                    available_seats = self._api.get_seats(theater.id, date,
                            play.screen_id, play.play_no)
                    new_seats = self._find_new_seats(theater, date, play,
                            available_seats, seat_r)
                    if new_seats:
                        self.logger.debug('New seats found: %s', new_seats)
                        posts.append(self._make_post(movie, format, theater,
                                date, play, new_seats))
        return posts

    def _get_objects(self, movie_name, movie_format, theater_name):
        nones = (None, None, None)

        movies = self._get_movies()
        movie = self._find(movie_name, movies)
        if movie is None:
            self.logger.warning('%s is not found in the movie list', movie_name)
            self.logger.debug('movie list: %s', movies)
            return nones

        formats = self._get_formats(movie.id)
        format = self._find(movie_format, formats)
        if format is None:
            self.logger.warning('%s is not found in the format list', movie_format)
            self.logger.debug('format list for movie_id %s: %s', movie.id, formats)
            return nones

        theaters = self._get_theaters(movie.id, format.id)
        theater = self._find(theater_name, theaters)
        if theater is None:
            self.logger.warning('%s is not found in the theater list', theater_name)
            self.logger.debug('theater list for movie_id %s, format_id %s: %s',
                    movie.id, format.id, theaters)
            return nones

        return movie, format, theater

    # Cache movies, formats, theaters data for 24 hours,
    # because they don't change often.

    @cached(timeout=86400)
    def _get_movies(self):
        return self._api.get_movies()

    @cached(timeout=86400)
    def _get_formats(self, movie_id):
        return self._api.get_formats(movie_id)

    @cached(timeout=86400)
    def _get_theaters(self, movie_id, format_id):
        return self._api.get_theaters(movie_id, format_id)

    def _get_dates(self, cache, movie, format, theater, date_r):
        # Get dates for the given movie, format, theater.
        # Dates are cached so that the same movie, format, theater doesn't
        # request the same data from the server.
        dates_key = (movie.id, format.id, theater.id)
        if dates_key not in cache:
            cache[dates_key] = self._api.get_dates(*dates_key)
        dates = cache[dates_key]
        if not dates:
            self.logger.info('%s (%s) at %s has no schedule for now',
                    movie.name, format.name, theater.name)
            return []
        dates_filtered = self._filter_dates(dates, date_r)
        if not dates_filtered:
            self.logger.info('%s (%s) at %s has no schedule in %s for now',
                    movie.name, format.name, theater.name, date_r)
            self.logger.debug('available dates: %s', dates)
            return []
        return dates_filtered

    WEEKDAY_NUMBERS = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}

    def _filter_dates(self, dates, date_range):
        if date_range is None:
            return dates

        # Resolve date_range to set of weekday numbers
        date_range_resolved = set()
        for date_or_weekday in date_range:
            if date_or_weekday == 'today':
                date_range_resolved.add(self._today_in_seoul().strftime('%Y%m%d'))
            elif date_or_weekday == 'weekdays':
                date_range_resolved.update([0, 1, 2, 3, 4])
            elif date_or_weekday == 'weekends':
                date_range_resolved.update([5, 6])
            elif date_or_weekday in CGV.WEEKDAY_NUMBERS:
                date_range_resolved.add(CGV.WEEKDAY_NUMBERS[date_or_weekday])
            else:  # a date string
                date_range_resolved.add(date_or_weekday)

        dates_filtered = []
        for date in dates:
            weekday = datetime.strptime(date, '%Y%m%d').weekday()
            if date in date_range_resolved or weekday in date_range_resolved:
                dates_filtered.append(date)
        return dates_filtered

    def _get_times(self, cache, movie, format, theater, date, time_r):
        # Get times for the given movie, format, theater, date.
        # Times are cached for the same reason dates are cached.
        times_key = (movie.id, format.id, theater.id, date)
        if times_key not in cache:
            cache[times_key] = self._api.get_times(*times_key)
        times = cache[times_key]
        if not times:
            self.logger.info('%s (%s) at %s on %s has no schedule for now',
                    movie.name, format.name, theater.name, date)
            return []
        times_filtered = self._filter_times(times, time_r)
        if not times_filtered:
            self.logger.info('%s (%s) at %s on %s has no schedule in %s for now',
                    movie.name, format.name, theater.name, date, time_r)
            self.logger.debug('available times: %s', [t.play.time for t in times])
            return []
        return times_filtered

    def _filter_times(self, times, time_range):
        if time_range is None:
            return times
        min_time = time_range[0]
        max_time = time_range[1]
        times_filtered = [t for t in times if t.play.time >= min_time and
                                              t.play.time <= max_time]
        return times_filtered

    def _find_new_seats(self, theater, date, play, available_seats, seat_range):
        available_seats = set(available_seats)
        seat_range = set(seat_range)
        seat_data = self._seat_data.setdefault((theater, date, play), {})
        new_seats = set()
        for seat, notified in seat_data.iteritems():
            if notified and seat not in available_seats:
                seat_data[seat] = False
            elif not notified and seat in available_seats and seat in seat_range:
                seat_data[seat] = True
                new_seats.add(seat)
        for seat in (available_seats & seat_range) - seat_data.viewkeys():
            seat_data[seat] = True
            new_seats.add(seat)
        return sorted(new_seats)

    def _make_post(self, movie, format, theater, date, play, new_seats):
        url = self._reservation_url(movie, format, theater, date, play)
        title = u'New seat(s) found for {0}'.format(movie.name)
        content = dedent(u"""\
            New seat(s) {0} found for {1} ({2}) at {3} starting at {4} on {5}.
        """).format(
            ', '.join(new_seats), movie.name, format.name, theater.name,
            play.time, datetime.strptime(date, '%Y%m%d').strftime('%A, %B %d, %Y')
        ).strip()
        return Post(url, title, content, published=datetime.now())

    def _find(self, name, items):
        for item in items:
            if item.name == name:
                return item

    def _reservation_url(self, movie, format, theater, date, play):
        url = 'http://m.cgv.co.kr/Reservation/Seat.aspx'
        query_dict = OrderedDict([
            ('MovieIdx', movie.id),
            ('CgvCode', format.id),
            ('TheaterCd', theater.id),
            ('PlayYmd', date),
            ('ScreenCd', play.screen_id),
            ('ScreenNm', play.screen_name),
            ('PlayNum', play.play_no),
            ('StartHhmm', play.time.replace(':', '')),
        ])
        return url + '?' + urlencode_utf8(query_dict)

    def _today_in_seoul(self):
        return pytz.utc.localize(utcnow()).astimezone(pytz.timezone('Asia/Seoul'))


class CGVAPI(object):

    def __init__(self, username=None, password=None):
        self.logger = getLogger(__name__).getChild(self.__class__.__name__)
        self._browser = CGVBrowser(username, password)

    def get_movies(self):
        response = self._browser.get_page('movie_list')
        doc = parse_html(response.content)
        items = []
        for a in doc.cssselect('table.list tbody tr .subject a'):
            try:
                id = re.search(r'MovieIdx=(\d+)', a.attrib['href'], re.I).group(1)
                name = a.text_content().strip()
            except (IndexError, KeyError, AttributeError):
                self.logger.warning('Markup is not as expected', exc_info=True)
            else:
                items.append(Movie(id=id, name=name))
        return items

    def get_formats(self, movie_id):
        response = self._browser.get_page('format_list', movie_id=movie_id)
        doc = parse_html(response.content)
        items = []
        for a in doc.cssselect('ul.movielist2 > li.movielist2 > a'):
            try:
                id = re.search(r'CgvCode=(\d+)', a.attrib['href'], re.I).group(1)
                name = re.search(r'\(([^)]+)\)', a.text_content().strip(), re.I).group(1)
            except (IndexError, KeyError, AttributeError):
                self.logger.warning('Markup is not as expected', exc_info=True)
            else:
                items.append(Format(id=id, name=name))
        return items

    def get_theaters(self, movie_id, format_id):
        response = self._browser.get_page('theater_list', movie_id=movie_id, format_id=format_id)
        doc = parse_html(response.content)
        items = []
        for a in doc.cssselect('#areaTheater ul.theaterlist > li.theaterlist > a'):
            try:
                regex = r"'(\d{{4}})'\s*,\s*'{0}'\s*,\s*'{1}'".format(format_id, movie_id)
                id = re.search(regex, a.attrib['href'], re.I).group(1)
                name = a.text_content()
            except (IndexError, KeyError, AttributeError):
                self.logger.warning('Markup is not as expected', exc_info=True)
            else:
                items.append(Theater(id=id, name=name))
        return items

    def get_dates(self, movie_id, format_id, theater_id):
        response = self._browser.get_page('date_list',
                movie_id=movie_id, format_id=format_id, theater_id=theater_id)
        doc = parse_html(response.content)
        items = []
        for a in doc.cssselect('table.month td:not(.disabled) a'):
            try:
                date = re.search(r'PlayYmd=(\d{8})', a.attrib['href'], re.I).group(1)
            except (IndexError, KeyError, AttributeError):
                self.logger.warning('Markup is not as expected', exc_info=True)
            else:
                items.append(date)
        return items

    def get_times(self, movie_id, format_id, theater_id, date):
        response = self._browser.get_page('time_list',
                movie_id=movie_id, format_id=format_id, theater_id=theater_id, date=date)
        doc = parse_html(response.content)
        items = []
        for a in doc.cssselect('ul.time-list > li.time-list > a'):
            try:
                href = a.attrib['href']
                id = re.search(r'ScreenCd=(\d+)', href, re.I).group(1)
                play_no = int(re.search(r'PlayNum=(\d+)', href, re.I).group(1))
                m = re.search(ur"""
                    (?P<time>\d{2}:\d{2})
                    \s*-\s*
                    (?P<screen_name>[^/]+)/(?P<play_no>\d+)회
                    \s*
                    \(좌석:(?P<current_seats>\d+)/(?P<total_seats>\d+)\)
                """, a.text_content(), re.VERBOSE | re.I)
                screen_name = m.group('screen_name')
                time = m.group('time')
                current_seats = int(m.group('current_seats'))
                total_seats = int(m.group('total_seats'))
            except (IndexError, KeyError, AttributeError, ValueError):
                self.logger.warning('Markup is not as expected', exc_info=True)
            else:
                items.append(PlayState(Play(id, play_no, screen_name, time),
                        current_seats, total_seats))
        return items

    def get_seats(self, theater_id, date, screen_id, play_no):
        response = self._browser.get_page('seat_list',
                theater_id=theater_id, date=date, screen_id=screen_id, play_no=play_no)
        doc = parse_html(response.content)
        items = []
        for td in doc.cssselect('#seat_table td.pointer'):
            try:
                seat = td.attrib['seatname']
            except KeyError:
                self.logger.warning('Markup is not as expected', exc_info=True)
            else:
                items.append(seat)
        return items


class CGVBrowser(Browser):

    BASE_URL = 'http://m.cgv.co.kr'
    QUERY_PATHS = {
        'movie_list': ('/Movie/MovieList.aspx', None),
        'format_list': ('/Reservation/MovieList.aspx', OrderedDict([
            ('movie_id', 'MovieIdx'),
        ])),
        'theater_list': ('/Reservation/TheaterList.aspx', OrderedDict([
            ('movie_id', 'MovieIdx'),
            ('format_id', 'CgvCode'),
        ])),
        'date_list': ('/Reservation/DateList.aspx', OrderedDict([
            ('movie_id', 'MovieIdx'),
            ('format_id', 'CgvCode'),
            ('theater_id', 'TheaterCd'),
        ])),
        'time_list': ('/Reservation/Time.aspx', OrderedDict([
            ('movie_id', 'MovieIdx'),
            ('format_id', 'CgvCode'),
            ('theater_id', 'TheaterCd'),
            ('date', 'PlayYmd'),
        ])),
        'seat_list': ('/Reservation/Seat.aspx', OrderedDict([
            ('theater_id', 'TheaterCd'),
            ('date', 'PlayYmd'),
            ('screen_id', 'ScreenCd'),
            ('play_no', 'PlayNum'),
        ])),
    }
    LOGIN_PATH = '/Member/Login.aspx'

    def _login(self, username, password):
        login_url = CGVBrowser.BASE_URL + CGVBrowser.LOGIN_PATH
        login_page = self._request(login_url)
        doc = parse_html(login_page.content)
        try:
            viewstate = doc.cssselect('[name="__VIEWSTATE"]')[0].attrib['value']
            eventvalidation = doc.cssselect('[name="__EVENTVALIDATION"]')[0].attrib['value']
        except (IndexError, AttributeError):
            raise LoginError('Cannot find necessary tokens')
        data = {
            '__VIEWSTATE': viewstate,
            '__EVENTVALIDATION': eventvalidation,
            'Login$tbUserID': username,
            'Login$tbPassword': password,
            'Login$ibLogin.x': 45,
            'Login$ibLogin.y': 37,
        }
        response = self._request(login_url, method='post', data=data)
        doc = parse_html(response.content)
        if not doc.cssselect('body'):
            raise LoginError()

    def _login_required(self, response):
        doc = parse_html(response.content)
        return doc.cssselect('.member_login')


Movie = namedtuple('Movie', 'id name')
Format = namedtuple('Format', 'id name')
Theater = namedtuple('Theater', 'id name')
Play = namedtuple('Play', 'screen_id play_no screen_name time')
PlayState = namedtuple('PlayState', 'play current_seats total_seats')
