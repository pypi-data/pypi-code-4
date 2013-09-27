#--coding: utf8--
import re
import warnings
import os.path

from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils.writers.html4css1 import Writer
import docutils.nodes

from pyscrum.core import Task, Story, Board


class RstLoader(object):
    """
    Загрузчик историй из .rst-файла.
    """
    def get_board(self, filename):
        stories = self.parse(open(filename).read().decode('utf-8'))
        return Board(os.path.basename(filename), stories)

    def parse(self, content):
        settings = OptionParser(components=(Parser, Writer)) \
                   .get_default_values()
        doc = new_document('doc', settings)
        parser = Parser()
        parser.parse(content, doc)

        stories = []
        for node in doc:
            if isinstance(node, docutils.nodes.section):
                # Каждая секция - это история
                if isinstance(node[0], docutils.nodes.title):
                    story_title = node.pop(0).astext()
                else:
                    warnings.warn('Найдена история без заголовка: %r' % node)
                    continue

                tasks = []
                points = None
                if isinstance(node[-1], docutils.nodes.bullet_list):
                    # Задачи расположены в списке в конце истории
                    tasklist = node.pop()
                    for line in tasklist:
                        line = line.astext()
                        # Оценка задачи указывается в круглых скобках в самом
                        # конце, слово "дней" опционально.
                        match = re.search(ur'^.+\((\d+)[^\)]{0,5}\)$', line,
                                          re.UNICODE | re.DOTALL)
                        if match:
                            points = int(match.group(1))
                            line = re.sub(ur'^(.+?)\(\d+[^\)]{0,5}\)$', r'\1',
                                          line)
                        else:
                            points = 0

                        # Ответственный указывается перед задачей и отделяется
                        # двоеточием.
                        match = re.search(ur'^\+?([\w]+):\s*(.+)$', line,
                                          re.UNICODE | re.DOTALL)
                        if match:
                            person = match.group(1)
                            task_title = match.group(2)
                            state = Task.WORK
                        else:
                            task_title = line
                            person = None
                            state = Task.NEW

                        if line.startswith('+'):
                            state = Task.DONE

                        task = Task(task_title, state, person=person, points=points)
                        tasks.append(task)

                # Все остальное в истории - ее описание.
                writer = Writer()
                pseudo_doc = new_document(story_title, settings)
                pseudo_doc.children = [node]
                writer.document = pseudo_doc
                writer.translate()
                description = ''.join(writer.body)

                stories.append(Story(story_title, description, tasks))

        return stories


class StringRstLoader(RstLoader):
    """
    Загрузчик историй из строки с текстом в формате RST.
    """
    def get_board(self, content):
        stories = self.parse(content.decode('utf-8'))
        return Board('', stories)
