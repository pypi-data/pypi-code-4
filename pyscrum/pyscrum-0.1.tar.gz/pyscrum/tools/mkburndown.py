#!/usr/bin/env python
#--coding: utf8--

import sys
import re
import os.path
from datetime import datetime, timedelta
import shlex
import subprocess
import json

from jinja2 import Environment, PackageLoader

from pyscrum.loaders import StringRstLoader


def guess_dates(filename):
    name, _ = os.path.splitext(os.path.basename(filename))
    matches = re.findall(r'([\d\.]{8,10})', name)
    if matches and len(matches) == 2:
        return [datetime.strptime(x, '%d.%m.%y').date() for x in matches]
    raise ValueError(('Invalid filename: should contain a date range '
                      'dd.mm.yy-dd.mm.yy'))


def points(filename, date):
    """
    Получить общее количество пунктов и кол-во выполненных на определенную
    дату.
    """
    cmd = "git show '@{%s}':./%s" % (date.strftime('%Y.%m.%d'),
                                   os.path.basename(filename))
    args = shlex.split(cmd)
    p = subprocess.Popen(args, cwd=os.path.abspath(os.path.dirname(filename)),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, err) = p.communicate()
    if p.returncode != 0:
        raise Exception('Something gone wrong with git: "%s"' % err)
    loader = StringRstLoader()
    board = loader.get_board(output)

    return board.points, board.done_points


def main():
    filename = sys.argv[1]
    start, end = guess_dates(filename)

    d = start
    today = datetime.today().date()
    actual, days, total_max = [], [], 0
    while d <= end:
        if d <= today:
            total, done = points(filename, d)
            total_max = max(total, total_max)
            actual.append(done)
        days.append(d.strftime('%d.%m'))
        d += timedelta(days=1)

    dailyBurn = float(total_max) / float(len(days))
    ideal = [(i, int(total_max - (dailyBurn * i)))
             for i in range(len(days))]
    # Перевернем график выполненной работы, сделаем - сколько осталось.
    actual = [total_max - x for x in actual]

    if len(actual) > 1 and len(days) > len(actual):
        x1, y1 = 0, actual[0]
        x2, y2 = len(actual) - 1, actual[-1]
        x3 = len(days) - 1
        y3 = y1 + ((y2 - y1) / (x2 - x1)) * (x3 - x1)
        projection = (
            (len(actual) - 1, actual[-1]),
            (len(days) - 1, y3)
        )
    else:
        projection = None

    actual = [(i, x) for i, x in enumerate(actual)]
    days = [(i, x) for i, x in enumerate(days)]

    env = Environment(loader=PackageLoader('pyscrum'))
    template = env.get_template('burndown.html')
    context = {
        'actual': json.dumps(actual),
        'ideal': json.dumps(ideal),
        'days': json.dumps(days),
        'title': os.path.basename(filename),
        'projection': json.dumps(projection),
    }
    print template.render(**context).encode('utf-8')


if __name__ == '__main__':
    main()
