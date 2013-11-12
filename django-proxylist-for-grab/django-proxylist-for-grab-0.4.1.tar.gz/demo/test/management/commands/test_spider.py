# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from grab.spider.base import Task
from proxylist.grabber import Spider


class SimpleSpider(Spider):
    initial_urls = ['http://www.lib.ru/']

    def task_initial(self, grab, task):
        grab.set_input('Search', 'linux')
        grab.submit(make_request=False)
        yield Task('search', grab=grab)

    def task_search(self, grab, task):
        if grab.doc.select('//b/a/font/b').exists():
            for elem in grab.doc.select('//b/a/font/b/text()'):
                print elem.text()


class Command(BaseCommand):
    help = 'Simple Spider'

    def handle(self, *args, **options):
        bot = SimpleSpider()
        bot.run()
        print bot.render_stats()
