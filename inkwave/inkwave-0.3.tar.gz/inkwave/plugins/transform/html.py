from lxml import html
from inkwave.core import Transform


class Html(Transform):
    def __init__(self, transformers, *args, **kwargs):
        super(Html, self).__init__(*args, **kwargs)
        self._transformers = transformers

    def transform(self):
        for d in self.source.all():
            doc = html.document_fromstring(d['content'])
            for t in self._transformers:
                t(doc)
            d['content'] = html.tostring(doc, doctype='<!doctype html>')
            yield d


class HtmlTransform:
    def __init__(self):
        pass

    def __call__(self, doc):
        self.transform(doc)

    def transform(self, doc):
        raise NotImplemented('method transform is not implemented')
