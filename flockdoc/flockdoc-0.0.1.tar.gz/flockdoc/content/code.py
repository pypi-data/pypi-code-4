"functions for handling code"
from itertools import groupby
from markdown import markdown
import os
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter

from . import Page
from ..renderer import env

class CodePage(object):
    LANGUAGES = {
        "py": {"name": "Python", "short": set(["#"])},
        "js": {"name": "JavaScript", "short": set(["//"])},
        "php": {"name": "PHP", "short": set(["//", "#"])},
        "rb": {"name": "Ruby", "short": set(["#"])},
    }

    def __init__(self, filename, content):
        self.filename, self.content = filename, content
        self.filetype = self.detect_filetype()

    def detect_filetype(self, filename=None):
        'detect a filetype to get comments'
        filename = filename or self.filename

        for ext in reversed(filename.split('.')):
            if ext in self.LANGUAGES:
                return ext

        raise ValueError('Cannot handle "%s". Unknown filetype.' % filename)

    def segment_lines(self):
        'segment lines into groups of comment and code'
        short = self.LANGUAGES[self.filetype]["short"]

        groups = groupby(
            self.content.strip().split('\n'),
            lambda line: any(line.lstrip().startswith(comment) for comment in short) and 'comment' or 'code'
        )

        for category, group in groups:
            yield category, '\n'.join(group)

    def render(self, template='layouts/code.html'):
        'render code content, returning filename and content'
        segments = list(self.segment_lines())
        short = self.LANGUAGES[self.filetype]["short"]

        lexer = get_lexer_for_filename(self.filename)
        formatter = HtmlFormatter()

        sections = []
        for i in range(0, len(segments), 2):
            section = dict(segments[i:i+2])

            # render comments to markdown
            comments = []
            for line in section.get('comment', '').split('\n'):
                line = line.lstrip()

                for symbol in short:
                    line = line.lstrip(symbol)

                comments.append(line)

            section['comment'] = markdown('\n'.join(comments))

            # highlight code with pygments
            if 'code' in section:
                section['code'] = highlight(section['code'], lexer, formatter)
            else:
                section['code'] = ''

            sections.append(section)

        rendered = env.get_template(template).render(
            sections=sections,
            filename=self.filename,
            filetype=self.filetype,
            basename=os.path.basename(self.filename).rsplit('.', 1)[0],
            language=self.LANGUAGES[self.filetype]["name"],
        )

        return self.filename + ".html", rendered
