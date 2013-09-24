from ilogue.readable.matcher import Matcher
import datetime


class DatetimeMatcher(Matcher):
    FORMAT = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self):
        super(DatetimeMatcher, self).__init__()
        self.expType = datetime.datetime

    def asString(self):
        self.expType = str
        return self

    def withinOneSecondOf(self, exp):
        assert isinstance(exp, datetime.datetime)
        self.exp = exp
        self.allowedDiff = datetime.timedelta(seconds=1)
        return self

    def matchFor(self, other):
        self.match = DatetimeMatch()
        try:
            self.matchType(other)
            other = self.matchFormatAndConvert(other)
            diff = self.exp - other
            if abs(diff) > self.allowedDiff:
                self.match = DatetimeMatch().exceeds(other, diff, self.exp)
        except MismatchException:
            pass
        return self.match

    def matchType(self, other):
        if not isinstance(other, self.expType):
            self.match = DatetimeMatch().wrongType(self.expType, type(other))
            raise MismatchException()

    def matchFormatAndConvert(self, other):
        if isinstance(other, str):
            try:
                other = datetime.datetime.strptime(other, self.FORMAT)
            except ValueError as err:
                self.match = DatetimeMatch().wrongFormat(err)
                raise MismatchException()
        return other


class MismatchException(Exception):
    pass


class DatetimeMatch():
    successful = True
    msg = 'Successful DatetimeMatch'

    def wrongFormat(self, err):
        self.successful = False
        self.msg = err.message
        return self

    def wrongType(self, expType, actType):
        self.successful = False
        self.msg = ("Type mismatch, expected {0}, but got {1}."
            .format(str(expType), str(actType)))
        return self

    def exceeds(self, other, diff, exp):
        self.successful = False
        self.msg = ("Datetime {0} differs by {1} from {2}."
            .format(other, diff, exp))
        return self

    def __str__(self):
        return self.msg


if __name__ == '__main__':
    print(__doc__)
