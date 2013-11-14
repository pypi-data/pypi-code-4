import logging

import pytest

from webalerts import SiteException, NotificationException, cached
from webalerts.app import App, Post
import webalerts.app


class TestApp(object):

    def setup(self):
        logging.basicConfig(level=logging.ERROR)

        # Mock time functions
        self.now = 0
        def current_time():
            return self.now
        def sleep(seconds):
            self.now += seconds
        webalerts.app.current_time = current_time
        webalerts.app.sleep = sleep

        class MockSite(object):
            def __init__(self, config):
                self.config = config
                self._counter = 0
            def get_new_posts(self):
                all_posts = self.config['mock_posts']
                if self._counter < len(all_posts):
                    posts = all_posts[self._counter]
                    self._counter += 1
                    if posts is None:
                        raise SiteException('mock exception')
                    return posts
                else:
                    return []

        self.notifications = {}
        test = self
        class MockNotification(object):
            def __init__(self, config):
                self.config = config
            def notify(self, posts):
                if self.config.get('mock_exception'):
                    raise NotificationException('mock exception')
                test.notifications.setdefault(self.config['mock_name'], []).extend(posts)

        self.app = App(config={
            'patterns': ['[fF]oo', 'apple'],
            'check_interval': 2,
            'notify_interval': 6,
            'sites': {
                'foo_forum': {
                    'class': MockSite,
                    'mock_posts': [
                        [],
                        [   #4
                            Post('url', 'title', 'content', published=10),
                            Post('foo', 'wine bar', 'hello, world!', published=13),
                            Post('http://foo.com', 'About Foo', 'Lorem ipsum ...', published=14),
                        ],
                        [   #6
                            Post('/apple', 'Fruits', 'apple, ...', published=25),
                        ],
                        None,  #8
                        [   #10
                            Post('/fruit', 'apple', 'red', published=44),
                        ],
                    ],
                },
                'bar': {
                    'class': MockSite,
                    'patterns': ['bar', 's?abre'],
                    'check_interval': 1,
                    'mock_posts': [
                        [   #1
                            Post('foo', 'Foo', 'foo', published=5),
                            Post('bar', 'Bar', 'bar', published=6),
                        ],
                        [   #2
                            Post('/fox', 'Fox', 'The quick brown fox ...', published=11),
                        ],
                        [   #3
                            Post('http://b.co/sorceress', 'Sorceress', '...', published=12),
                            Post('http://b.co/barbarian', 'Barbarian', '...', published=12),
                        ],
                        [],
                        None,  #5
                        [],
                        [   #7
                            Post('http://b.co/archer', 'Archer', 'Lorem ipsum ...', published=32),
                            Post('http://b.co/sabre', 'Sabre', 'Lorem ipsum ...', published=36),
                        ],
                    ],
                },
                'any': {
                    'class': MockSite,
                    'patterns': None,
                    'check_interval': 3,
                    'mock_posts': [
                        [  #3
                            Post('url', 'title', 'content', published=7),
                            Post('url', 'title2', 'content2', published=8),
                            Post('url', 'title3', 'content3', published=9),
                        ],
                    ],
                },
            },
            'notifications': {
                'sms': {
                    'class': MockNotification,
                    'mock_name': 'sms',
                },
                'twitter': {
                    'class': MockNotification,
                    'notify_interval': 1,
                    'mock_name': 'twitter',
                },
                'grouchy_notifier': {
                    'class': MockNotification,
                    'notify_interval': 2,
                    'mock_exception': True,
                }
            },
        })

    def test_run(self):
        g = self.app._run()
        next(g)  #1
        assert self.now == 0
        assert self.notifications.get('sms', []) == []
        assert self.notifications.get('twitter', []) == [
            Post('bar', 'Bar', 'bar', published=6),
        ]
        self.notifications.clear()
        next(g)  #2
        assert self.now == 60.1
        next(g)  #3
        assert self.now == 120.1
        assert self.notifications.get('sms', []) == []
        assert self.notifications.get('twitter', []) == [
            Post('url', 'title', 'content', published=7),
            Post('url', 'title2', 'content2', published=8),
            Post('url', 'title3', 'content3', published=9),
            Post('http://b.co/barbarian', 'Barbarian', '...', published=12),
        ]
        self.notifications.clear()
        next(g)  #4
        assert self.now == 180.1
        assert self.notifications.get('sms', []) == []
        assert self.notifications.get('twitter', []) == [
            Post('http://foo.com', 'About Foo', 'Lorem ipsum ...', published=14),
        ]
        self.notifications.clear()
        next(g)
        next(g)  #6
        assert self.notifications.get('sms', []) == [
            Post('bar', 'Bar', 'bar', published=6),
            Post('url', 'title', 'content', published=7),
            Post('url', 'title2', 'content2', published=8),
            Post('url', 'title3', 'content3', published=9),
            Post('http://b.co/barbarian', 'Barbarian', '...', published=12),
            Post('http://foo.com', 'About Foo', 'Lorem ipsum ...', published=14),
            Post('/apple', 'Fruits', 'apple, ...', published=25),
        ]
        assert self.notifications.get('twitter', []) == [
            Post('/apple', 'Fruits', 'apple, ...', published=25),
        ]
        self.notifications.clear()
        next(g)  #7
        assert self.notifications.get('sms', []) == []
        assert self.notifications.get('twitter', []) == [
            Post('http://b.co/sabre', 'Sabre', 'Lorem ipsum ...', published=36),
        ]
        self.notifications.clear()
        next(g)
        next(g)
        next(g)  #10
        assert self.notifications.get('sms', []) == []
        assert self.notifications.get('twitter', []) == [
            Post('/fruit', 'apple', 'red', published=44),
        ]
        self.notifications.clear()
        next(g)
        next(g)  #12
        assert self.notifications.get('sms', []) == [
            Post('http://b.co/sabre', 'Sabre', 'Lorem ipsum ...', published=36),
            Post('/fruit', 'apple', 'red', published=44),
        ]
        assert self.notifications.get('twitter', []) == []
        self.notifications.clear()
        next(g)  #13
        assert self.now == 720.1
        assert self.notifications.get('sms', []) == []
        assert self.notifications.get('twitter', []) == []

    def test_run_config_error(self):
        self.app.config['sites'] = 'foo'
        with pytest.raises(StopIteration):
            next(self.app._run())


class TestPost(object):

    def test_content_html_safe(self):
        post = Post('url', 'title', 'content', content_html="""<html>
<head>
<title>Title!</title>
<style>* { font-size: 200px; }</style>
</head>
<body class="unsafe">
<p>safe tag!</p>
<p style="font-size: 100px">unsafe attributes!</p>
<a onclick="alert('hi!')" href="javascript:alert('hi!')">unsafe!</a>
<script type="text/javascript">alert("unsafe code!");</script>
<iframe src="http://unsafe.com"></iframe>
</body>
</html>""")
        assert post.content_html_safe == """<div>

Title!



<p>safe tag!</p>
<p>unsafe attributes!</p>
<a href="">unsafe!</a>



</div>"""
