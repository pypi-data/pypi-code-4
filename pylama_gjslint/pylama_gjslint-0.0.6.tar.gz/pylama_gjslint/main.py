from pylama import lint


class Linter(lint.Linter):

    """ Check code with gjlint. """

    def allow(self, path):
        return path.endswith('.js')

    @staticmethod
    def run(path, **meta):  # noqa
        """ gjlint code checking.

        :return list: List of errors.

        """
        from .closure_linter import gjslint

        errors = []
        records_iter = gjslint.main(["", path])

        import re
        regExErrStr = re.compile(r'Line\s(\d+),\s(E:\d+):\s(.*)')
        for record in records_iter:
            matchErrStr = re.match(regExErrStr, record.error_string)
            if matchErrStr:
                errors.append(dict(
                    type=matchErrStr.group(2),
                    lnum=matchErrStr.group(1),
                    # due to errors filtering type is combined with the text
                    text=" ".join([matchErrStr.group(2), matchErrStr.group(3)])
                ))

        return errors
