from __future__ import absolute_import

import unittest


class testMixin(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_successful_validate(self):
        from datetime import datetime
        from minos.mixin import MinosMixin
        from minos.validators import (
            PresenceValidator,
            MinimumPresenceValidator,
            NumericalityValidator,
            LengthValidator,
            DatetimeValidator,
            InclusionValidator,
            WithValidator,
            EmailValidator,
            JSONValidator,
        )

        class testClass(MinosMixin):
            datetime_field = None
            email_field = None
            toaster_field = None
            json_field = None
            long_ass_field = None
            fruit_field = None
            numeric_field = None
            stuff = None
            trunk = None

            def mobster_check(self):
                return "loot" in self.trunk and not "bodies" in self.trunk

            validators = [
                DatetimeValidator('datetime_field'),
                EmailValidator('email_field'),
                InclusionValidator('toaster_field', in_=['white', 'wheat', 'rye']),
                JSONValidator('json_field'),
                LengthValidator('long_ass_field', greater_than=10),
                MinimumPresenceValidator(['kitchen_field', 'football_field', 'fruit_field']),
                NumericalityValidator('numeric_field', integer_only=True),
                PresenceValidator('stuff'),
                WithValidator('stuff', with_='mobster_check')
            ]

            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        kitchen_sink = testClass(
            datetime_field=datetime.now(),
            email_field='test@uber.com',
            toaster_field='rye',
            json_field=u'{"a": 1, "c": true, "b": "true", "d": "2013-02-18T12:44:07.065691"}',
            long_ass_field='this is a long string.',
            fruit_field='apple',
            numeric_field=1337,
            stuff='magic.',
            trunk='whole lotta loot in the trunk.'
            )

        valid = kitchen_sink.validate()
        self.assertTrue(valid)

    def test_unsuccessful_validate(self):
        from datetime import datetime
        from minos.mixin import MinosMixin
        from minos.errors import FormValidationError
        from minos.validators import (
            PresenceValidator,
            MinimumPresenceValidator,
            NumericalityValidator,
            LengthValidator,
            DatetimeValidator,
            InclusionValidator,
            WithValidator,
            EmailValidator,
            JSONValidator,
            )

        class testClass(MinosMixin):
            datetime_field = None
            email_field = None
            toaster_field = None
            json_field = None
            long_ass_field = None
            fruit_field = None
            numeric_field = None
            stuff = None
            trunk = None

            validators = [
                DatetimeValidator('datetime_field'),
                EmailValidator('email_field'),
                InclusionValidator('toaster_field', in_=['white', 'wheat', 'rye']),
                JSONValidator('json_field'),
                LengthValidator('long_ass_field', greater_than=10),
                MinimumPresenceValidator(['kitchen_field', 'football_field', 'fruit_field']),
                NumericalityValidator('numeric_field', integer_only=True),
                PresenceValidator('stuff'),
                WithValidator('stuff', with_='mobster_check')
            ]

            def mobster_check(self):
                return "loot" in self.trunk and not "bodies" in self.trunk

            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        kitchen_sink = testClass(
            datetime_field=datetime.now(),
            email_field='test@uber.com',
            toaster_field='rye',
            json_field=u'{"a": 1, "c": true, "b": "true", "d": "2013-02-18T12:44:07.065691"}',
            long_ass_field='this is a long string.',
            fruit_field='apple',
            numeric_field=1337.5,
            stuff='magic.',
            trunk='whole lotta bodies in the trunk.'
            )

        self.assertRaises(FormValidationError, kitchen_sink.validate)
