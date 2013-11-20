from seantis.people import _
from seantis.plonetools import tools


class TranslatableException(Exception):

    def __repr__(self):
        return 'TranslatableException({})'.format(self.message)

    def __init__(self, message):
        self.message = message

    def translate(self, request):
        return tools.translator(request)(self.message)


class ContentImportError(TranslatableException):

    def __repr__(self):
        base = 'ContentImportError(message="{}", rownumber={}, colname="{}")'
        return base.format(self.message, self.rownumber, self.colname or '')

    def __init__(self, message, rownumber=None, colname=None):
        super(ContentImportError, self).__init__(message)
        self.rownumber = rownumber
        self.colname = colname

    def translate_position(self, request):
        particles = []

        if self.rownumber:
            particles.append(_(u'Row ${row}', mapping=dict(
                row=self.rownumber
            )))

        if self.colname:
            particles.append(_(u'Column ${column}', mapping=dict(
                column=self.colname
            )))

        translate = tools.translator(request)
        return u', '.join(map(translate, particles))

    def translate(self, request):
        message = super(ContentImportError, self).translate(request)
        position = self.translate_position(request)

        if not position:
            return message
        else:
            return u'{} ({})'.format(message, position)
