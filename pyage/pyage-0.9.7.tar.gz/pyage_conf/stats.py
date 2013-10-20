import logging
import os
import urllib2
import Pyro4
import time
from datetime import datetime
from pyage.core.inject import Inject, InjectOptional
from pyage.core.statistics import Statistics
from pyage.core.workplace import WORKPLACE

logger = logging.getLogger(__name__)

class GlobalTimeStatistics(Statistics):
    @Inject("ns_hostname")
    @InjectOptional("notification_url")
    def __init__(self):
        super(GlobalTimeStatistics, self).__init__()
        self.fitness_output = open('fitness_pyage' + str(datetime.now()) + '.txt', 'a')
        self.fitness_output.write(
            '# DIMS:' + os.environ['DIMS'] + os.environ["MACHINES"] + ' ' + str(datetime.now()) + '\n')
        self.start = time.time()

    def update(self, step_count, agents):
        try:
            best_fitness = max(a.get_fitness() for a in agents)
            logger.info(best_fitness)
            if step_count % 100 == 0:
                ns = Pyro4.locateNS(self.ns_hostname)
                best_fitness = max(Pyro4.Proxy(w).get_fitness() for w in ns.list(WORKPLACE).values())
                self.append(best_fitness, step_count)
        except:
            logging.exception("")


    def append(self, best_fitness, step_count):
        self.fitness_output.write(str(time.time() - self.start) + ';' + str(abs(best_fitness)) + '\n')

    def summarize(self, agents):
        try:
            if hasattr(self, "notification_url"):
                url = self.notification_url + "?time=%s&agents=%s&conf=%s" % (
                    time.time() - self.start, os.environ['AGENTS'], os.environ['DIMS'])
                logger.info(url)
                urllib2.urlopen(url)

        except:
            logging.exception("")


class NotificationStats(Statistics):
    @Inject("notification_url")
    def __init__(self):
        super(NotificationStats, self).__init__()
        self.start = time.time()


    def update(self, step_count, agents):
        best_fitness = max(a.get_fitness() for a in agents)
        logger.info(best_fitness)

    def summarize(self, agents):
        try:
            if hasattr(self, "notification_url"):
                url = self.notification_url + "?time=%s&agents=%s&conf=%s" % (
                    time.time() - self.start, os.environ['AGENTS'], os.environ['DIMS'])
                logger.info(url)
                urllib2.urlopen(url)

        except:
            logging.exception("")


class MigrationNotificationStatistics(Statistics):
    @Inject("notification_url", "migration")
    def __init__(self):
        super(MigrationNotificationStatistics, self).__init__()
        self.start = time.time()


    def update(self, step_count, agents):
        best_fitness = max(a.get_fitness() for a in agents)
        logger.info(best_fitness)

    def summarize(self, agents):
        try:
            if hasattr(self, "notification_url"):
                url = self.notification_url + "?time=%s&agents=%s&conf=%s" % (
                    time.time() - self.start, os.environ['AGENTS'], str(self.migration.counter))
                logger.info(url)
                urllib2.urlopen(url)

        except:
            logging.exception("")