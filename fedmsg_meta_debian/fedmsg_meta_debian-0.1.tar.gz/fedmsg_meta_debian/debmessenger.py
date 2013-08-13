# Copyright (C) 2013 Simon Chopin <chopin.simon@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from fedmsg.meta.base import BaseProcessor

from fedmsg_meta_debian.utils import format_from

class DebChangesProcessor(BaseProcessor):
    __name__ = "debmessenger.package.upload"
    __description__ = "Debian uploaded packages"
    __link__ = "http://ftpmaster.debian.org"
    __docs__ = "http://ftpmaster.debian.org"
    __obj__ = "Uploads"

    def title(self, msg, **config):
        return "Package upload"

    def subtitle(self, msg, **config):
        return '{name} uploaded {source} ({version}) to {distribution}'.format(
                name=format_from(msg['msg']['Changed-By']),
                source=msg['msg']['Source'],
                distribution=msg['msg']['Distribution'],
                version=msg['msg']['Version'],
        )

    def link(self, msg, **config):
        return 'http://packages.qa.debian.org/{}'.format(msg['msg']['Source'])

    def packages(self, msg, **config):
        return set([msg['msg']['Source']])

class DebBugProcessor(BaseProcessor):
    __name__ = "debmessenger.bug"
    __description__ = "Debian BTS reports"
    __link__ = "http://bugs.debian.org"
    __docs__ = "http://bugs.debian.org"
    __obj__ = "Bugs"

    event2title = {
        'report': "New bug report",
        'closed': "Bug closed",
        'followup': "Bug followup",
    }

    event2subtitle = {
        'report': "{person} filed {subject}",
        'closed': "{subject}",
        'followup': "{person} followed up on {subject}",
    }

    def title(self, msg, **config):
        event = msg['topic'].split('.')[-1]
        return self.event2title.get(event, event)

    def subtitle(self, msg, **config):
        event = msg['topic'].split('.')[-1]
        return self.event2subtitle[event].format(
            person=format_from(msg['msg']['from']),
            subject=msg['msg']['title']
        )

    def link(self, msg, **config):
        return 'http://bugs.debian.org/{}'.format(msg['msg']['nb'])

    def packages(self, msg, **config):
        return set([msg['msg']['source']])
