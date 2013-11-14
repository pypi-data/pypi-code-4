# -*- coding: UTF-8 -*-
from datetime import datetime
import os
import time

from mock import Mock
import pytest

from webalerts import LoginError, Post
from webalerts.sites.cgv import CGV, CGVAPI, Movie, Format, Theater, Play, PlayState
import webalerts.sites.cgv
from ...helpers import mock_function, MockRequest


__dir__ = os.path.abspath(os.path.dirname(__file__))


class TestCGV(object):

    def setup(self):
        self.cgv = CGV(config={
            'data': [
                ('Gravity', 'IMAX3D', 'Wangsimni',
                 ('12:00', '24:30'), ['20131128', 'fri', 'weekends'],
                 ['B2', 'B3', 'C2', 'C3']),
            ],
        })
        self.movies = [
            Movie('77200', 'Gravity'),
            Movie('76959', 'Thor: The Dark World'),
        ]
        self.formats = [
            Format('20004109', 'SOUNDX'),
            Format('20004051', 'IMAX3D'),
        ]
        self.theaters = [
            Theater('0014', 'Sangam'),
            Theater('0074', 'Wangsimni'),
        ]
        self.dates = {(m.id, f.id, t.id): [] for m in self.movies
                for f in self.formats for t in self.theaters}
        self.times = {}
        self.seats = {}
        self.cgv._api.get_movies = Mock(return_value=self.movies)
        self.cgv._api.get_formats = Mock(return_value=self.formats)
        self.cgv._api.get_theaters = Mock(return_value=self.theaters)
        self.cgv._api.get_dates = mock_function(self.dates)
        self.cgv._api.get_times = mock_function(self.times)
        self.cgv._api.get_seats = mock_function(self.seats)

        # Fake the current time roughly to 2013-11-25
        webalerts.sites.cgv.utcnow = lambda: datetime(2013, 11, 25, 12)

    def test_get_new_posts(self):
        self.dates.update({
            ('77200', '20004051', '0074'): [
                '20131127', '20131128', '20131129', '20131130',
            ],
            ('77200', '20004109', '0074'): ['20131128'],
            ('77200', '20004051', '0014'): ['20131128'],
            ('76959', '20004051', '0074'): ['20131130'],
        })
        self.times.update({
            ('77200', '20004051', '0074', '20131127'): [
                PlayState(Play('009', 1, 'IMAX #1', '07:30'), 16, 16),
                PlayState(Play('009', 3, 'IMAX #1', '15:30'), 5, 16),
            ],
            ('77200', '20004051', '0074', '20131128'): [
                PlayState(Play('009', 2, 'IMAX #1', '11:30'), 5, 16),
                PlayState(Play('009', 4, 'IMAX #1', '19:30'), 1, 16),
            ],
            ('77200', '20004051', '0074', '20131129'): [
                PlayState(Play('009', 1, 'IMAX #1', '07:30'), 6, 16),
                PlayState(Play('009', 3, 'IMAX #1', '15:30'), 0, 16),
                PlayState(Play('009', 5, 'IMAX #1', '23:30'), 0, 16),
            ],
            ('77200', '20004051', '0074', '20131130'): [
                PlayState(Play('009', 1, 'IMAX #1', '12:00'), 4, 16),
            ],
        })
        self.seats.update({
            ('0074', '20131127', '009', 1): make_seats(['A', 'B', 'C', 'D'], [1, 2, 3, 4]),
            ('0074', '20131127', '009', 3): ['A1', 'A4', 'B2', 'D1', 'D3'],

            ('0074', '20131128', '009', 2): ['A1', 'A4', 'B3', 'B4', 'C3'],
            ('0074', '20131128', '009', 4): ['A1'],

            ('0074', '20131129', '009', 1): ['A2', 'C2', 'C3', 'C4', 'D1', 'D2'],
            ('0074', '20131129', '009', 3): [],
            ('0074', '20131129', '009', 5): [],

            ('0074', '20131130', '009', 1): ['A4', 'B1', 'B2', 'C2'],
        })
        rv = self.cgv.get_new_posts()
        assert len(rv) == 1
        assert rv[0].url == ('http://m.cgv.co.kr/Reservation/Seat.aspx?'
                             'MovieIdx=77200&CgvCode=20004051&TheaterCd=0074&'
                             'PlayYmd=20131130&ScreenCd=009&ScreenNm=IMAX+%231&'
                             'PlayNum=1&StartHhmm=1200')
        assert rv[0].title == 'New seat(s) found for Gravity'
        assert rv[0].content == 'New seat(s) B2, C2 found for Gravity (IMAX3D) at Wangsimni starting at 12:00 on Saturday, November 30, 2013.'
        assert self.cgv.get_new_posts() == []

        self.dates.update({
            ('77200', '20004051', '0074'): [
                '20131129', '20131130', '20131201', '20131202',
            ],
        })
        self.times.update({
            ('77200', '20004051', '0074', '20131129'): [
                PlayState(Play('009', 3, 'IMAX #1', '15:30'), 1, 16),
                PlayState(Play('009', 5, 'IMAX #1', '23:30'), 1, 16),
            ],
            ('77200', '20004051', '0074', '20131130'): [
                PlayState(Play('009', 1, 'IMAX #1', '12:00'), 0, 16),
            ],
            ('77200', '20004051', '0074', '20131201'): [
                PlayState(Play('009', 1, 'IMAX #1', '12:00'), 1, 16),
            ],
            ('77200', '20004051', '0074', '20131202'): [
                PlayState(Play('009', 1, 'IMAX #1', '12:00'), 1, 16),
            ],
        })
        self.seats.update({
            ('0074', '20131129', '009', 3): ['C3'],
            ('0074', '20131129', '009', 5): ['D1'],
            ('0074', '20131130', '009', 1): [],
            ('0074', '20131201', '009', 1): ['B2'],
            ('0074', '20131202', '009', 1): ['B2'],
        })
        rv = self.cgv.get_new_posts()
        assert len(rv) == 2
        assert '20131129' in rv[0].url
        assert 'New seat(s) C3 found' in rv[0].content
        assert '20131201' in rv[1].url
        assert 'New seat(s) B2 found' in rv[1].content
        assert self.cgv.get_new_posts() == []

        self.times.update({
            ('77200', '20004051', '0074', '20131130'): [
                PlayState(Play('009', 1, 'IMAX #1', '12:00'), 3, 16),
            ],
        })
        self.seats.update({
            ('0074', '20131130', '009', 1): ['B2', 'B3', 'B4'],
        })
        rv = self.cgv.get_new_posts()
        assert len(rv) == 1
        assert '20131130' in rv[0].url
        assert 'New seat(s) B2, B3 found' in rv[0].content


class TestCGVAPIWithAuth(object):

    def setup(self):
        setup_api(self, 'john', 'pass')

    def test_get_movies(self):
        rv = self.api.get_movies()
        expected = [
            ('77200', u'그래비티'),
            ('77232', u'동창생'),
            ('76959', u'토르 : 다크 월드'),
            ('77206', u'노브레싱'),
            ('77207', u'공범'),
            ('77270', u'더 퍼지'),
            ('77254', u'세이프 헤이븐'),
            ('77271', u'올 이즈 로스트'),
            ('77252', u'잉투기'),
            ('77220', u'소녀'),
            ('77205', u'캡틴 필립스'),
            ('77245', u'디스커넥트'),
            ('77234', u'미스터 노바디'),
            ('77251', u'친구2'),
            ('77317', u'붉은 가족'),
            ('77175', u'화이 : 괴물을 삼킨 아이'),
            ('39360', u'만추'),
            ('76829', u'소원'),
            ('77221', u'라 붐'),
            ('77225', u'킥 애스2: 겁 없는 녀석들'),
        ]
        assert [(item.id, item.name) for item in rv] == expected

    def test_get_formats(self):
        rv = self.api.get_formats('77200')
        expected = [
            ('20004110', '3D,SOUNDX'),
            ('20004109', 'SOUNDX'),
            ('20004069', '4DX 3D,SOUNDX'),
            ('20004068', '4DX 3D'),
            ('20004049', u'디지털'),
            ('20004051', 'IMAX3D'),
            ('20004050', '3D'),
        ]
        assert [(item.id, item.name) for item in rv] == expected

    def test_get_theaters(self):
        expected = [
            ('0014', u'상암'),
            ('0074', u'왕십리'),
            ('0013', u'용산'),
            ('0012', u'수원'),
            ('0054', u'일산'),
            ('0002', u'인천'),
            ('0005', u'서면'),
            ('0128', u'울산삼산'),
            ('0058', u'대구'),
            ('0007', u'대전'),
            ('0090', u'광주터미널'),
        ]
        rv = self.api.get_theaters('77200', '20004051')
        assert [(item.id, item.name) for item in rv] == expected

    def test_get_dates(self):
        rv = self.api.get_dates('77200', '20004051', '0074')
        expected = ['20131107', '20131108', '20131109', '20131110']
        assert rv == expected

    def test_get_times(self):
        rv = self.api.get_times('77200', '20004051', '0074', '20131108')
        assert rv[0] == PlayState(Play('009', 1, u'IMAX관', '07:30'), 165, 303)
        assert [info.play.time for info in rv] == [
            '07:30',
            '09:30',
            '11:30',
            '13:30',
            '15:30',
            '17:30',
            '19:30',
            '21:35',
            '23:40',
            '25:40',
        ]

    def test_get_times_preparing(self):
        assert self.api.get_times('77200', '20004051', '0074', '20131113') == []

    def test_get_seats(self):
        assert self.api.get_seats('0074', '20131109', '009', 6) == [
            'A06', 'A07', 'A26', 'A27', 'H32', 'J01', 'K01'
        ]


class TestCGVAPIWithoutAuth(object):

    def setup(self):
        setup_api(self, 'abcd', '1234')

    def test_get_seats(self):
        with pytest.raises(LoginError):
            self.api.get_seats('0074', '20131109', '009', 6)


def setup_api(self, username, password):
    self.api = CGVAPI(username, password)
    self.api._browser._request = MockRequest()
    self.api._browser._request.from_yaml(os.path.join(__dir__, 'pages.yaml'))


def make_seats(alpha, numeric):
    return ['{0}{1}'.format(a, n) for a in alpha for n in numeric]
