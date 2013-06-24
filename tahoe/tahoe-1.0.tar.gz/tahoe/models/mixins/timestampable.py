"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import datetime


def TimestampMixin(db):
    class TimestampMixin(object):
        """
        Makes a model trackable by time.

        Adds ``created_at``, ``updated_at``, and ``deleted_at`` fields
        to a model and sets up all the tracking.

        Also allows for a model to be soft deleted.

        Use the ``query_active()`` method in place of the ``query`` object
        when querying for items to only get back items which have not
        been soft deleted.
        """
        NOW_FN = datetime.datetime.utcnow
        created_at = db.Column(db.DateTime, default=NOW_FN)
        updated_at = db.Column(db.DateTime, default=NOW_FN, onupdate=NOW_FN)
        deleted_at = db.Column(db.DateTime)

        @classmethod
        def query_active(cls):
            return cls.query.filter_by(deleted_at=None)

        def is_deleted(self):
            if self.deleted_at:
                return True
            return False

        def mark_deleted(self):
            self.deleted_at = self.NOW_FN()

        def mark_undeleted(self):
            self.deleted_at = None

    return TimestampMixin
