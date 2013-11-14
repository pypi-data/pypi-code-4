from datetime import datetime
from textwrap import dedent

from mock import Mock
import pytest

from webalerts import Post
from webalerts.notifications.email import EmailNotification
import webalerts.notifications.email


class TestEmailNotification(object):

    def setup(self):
        self.email = EmailNotification(config={
            'to_addrs': ['user1@example.com', 'user2@example.com'],
            'from_addr': 'notifier@foo.net',
            'host': 'foo.net',
            'port': 1234,
            'template': dedent(u"""\
                <a href="{url}">{title}</a> at {published}
                <div>{content}</div>
            """),
            'style': "p { font-size: 12px; }",
            'layout': dedent(u"""\
                <style>{style}</style>
                {body}
            """),
        })
        self.SMTP = webalerts.notifications.email.SMTP = Mock()
        self.sendmail = webalerts.notifications.email.sendmail = Mock()

    @pytest.mark.parametrize('secure', [(True,), (False,)])
    def test_notify(self, secure):
        if secure:
            self.email.config['secure'] = True
        self.email.notify([
            Post(
                '/a/animals',
                'Animals in the Wild',
                'Dogs, Cats, ...',
                published=datetime(2013, 1, 1, 10, 43),
            ),
            Post(
                '/asdf',
                'Foo',
                'Bar',
                published=datetime(2013, 1, 2, 22, 30, 12),
            ),
            Post(
                '/html&escape',
                '&_&',
                '<plain text>',
                published=datetime(2013, 1, 5, 0, 10),
            ),
            Post(
                '/escape2',
                'X',
                'safe tag!\nunsafe attributes!\nunsafe!',
                content_html=dedent("""\
                    <p>safe tag!</p>
                    <p style="font-size: 100px">unsafe attributes!</p>
                    <a onclick="alert('hi!')" href="javascript:alert('hi!')">unsafe!</a>
                    <script type="text/javascript">alert("unsafe code!");</script>
                """),
                published=datetime(2013, 1, 5, 0, 20),
            ),
        ])
        self.SMTP.assert_called_with('foo.net', 1234)
        conn = self.sendmail.call_args[0][0]
        if secure:
            conn.ehlo.assert_called_with()
            conn.starttls.assert_called_with()
        else:
            conn.connect.assert_called_with()
        assert self.sendmail.call_args[0][1] == 'notifier@foo.net'
        assert self.sendmail.call_args[0][2] == ['user1@example.com', 'user2@example.com']
        assert self.sendmail.call_args[0][3] == u'Animals in the Wild and 3 more'
        assert self.sendmail.call_args[0][4] == dedent(u"""\
            <style>p { font-size: 12px; }</style>
            <a href="/a/animals">Animals in the Wild</a> at 2013-01-01 10:43:00
            <div>Dogs, Cats, ...</div>

            <a href="/asdf">Foo</a> at 2013-01-02 22:30:12
            <div>Bar</div>

            <a href="/html&amp;escape">&amp;_&amp;</a> at 2013-01-05 00:10:00
            <div>&lt;plain text&gt;</div>

            <a href="/escape2">X</a> at 2013-01-05 00:20:00
            <div><div><p>safe tag!</p>
            <p>unsafe attributes!</p>
            <a href="">unsafe!</a>

            </div></div>

        """)
        conn.quit.assert_called_with()
