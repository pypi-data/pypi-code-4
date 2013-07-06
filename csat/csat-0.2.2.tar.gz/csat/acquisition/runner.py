import sys
import os
import argparse
import abc

from csat import logging, tasks


class RunnerBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, collector):
        self.collector = collector

    def build_base_parser(self, parser):
        parser.add_argument('-v', '--verbose', default=list(),
                            action='append_const', const=1, help='Increments '
                            'the verbosity (can be used multiple times).')
        parser.add_argument('-q', '--quiet', default=list(),
                            action='append_const', const=1, help='Decrements '
                            'the verbosity (can be used multiple times).')
        parser.add_argument('-o', '--output', default='-', help='Path to the '
                            'resulting GraphML file. A single - makes the '
                            'graph to be written to stdout. The default is to'
                            ' write the graph to stdout.')

        return parser

    def build_parser(self, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        base_parser = self.build_base_parser(parser)
        parser = self.collector.build_parser(base_parser)
        return parser

    @abc.abstractmethod
    def get_task_manager(self):
        pass

    def get_logger(self):
        # Setup logging
        logfile = os.getenv('CSAT_LOGFILE')
        logger = logging.LoggingSubsystem(logfile=logfile)
        logger.start()

        return logger

    def configure_logger(self, logger, args):
        # Set the verbosity level
        logger.increment_verbosity(len(args.verbose) - len(args.quiet))
        logger.capture_stdout()

    def run_as_subcommand(self, args):
        self.logger = self.get_logger()
        self.args = args
        return self._run()

    def run(self, arguments=None):
        if not arguments:
            arguments = sys.argv[1:]

        self.logger = self.get_logger()
        self.args = self.build_parser().parse_args(arguments)
        return self._run()

    def _run(self):
        # Build argument parser and parse command line
        self.configure_logger(self.logger, self.args)

        # Execute command
        self.log = self.logger.get_logger('runner')
        self.log.info('Starting collection process...')

        task_manager = self.get_task_manager()
        try:
            collector = self.collector.build_collector(
                task_manager,
                self.logger.get_logger('collector'),
                self.args
            )
            graph = collector.run()
            self.write_graph(graph)
        except Exception:
            self.log.critical('Collection process failed', exc_info=True)
            res = 1
        except KeyboardInterrupt:
            # TODO: Should we setup a signal handler for this for when we
            # run native code?
            print ''
            self.log.warn('SIGINT Received, terminating execution...')
            res = 1
        else:
            self.log.info('Collection process terminated.')
            res = 0
        finally:
            for task in task_manager.tasks:
                if task.status not in (task.COMPLETED, task.FAILED):
                    task.status = task.FAILED
                    task.statusText = ('Task failed to complete before process'
                                       ' termination.')

        # Shutdown logging
        self.logger.stop(res)
        return res

    def write_graph(self, graph):
        if self.args.output == '-':
            graph.write_graphml(sys.__stdout__)
        else:
            with open(self.args.output, 'wb') as fh:
                graph.write_graphml(fh)
            self.log.info('Graph written to {}.'.format(self.args.output))


class ConsoleRunner(RunnerBase):
    def build_base_parser(self, parser):
        parser = super(ConsoleRunner, self).build_base_parser(parser)

        parser.add_argument('-p', '--no-progress', action='store_true',
                            help='Disable interactive progress reporting.')

        return parser

    def get_task_manager(self):
        if self.args.no_progress or not sys.__stderr__.isatty():
            return tasks.TaskManager()
        else:
            terminal = tasks.VT100Terminal(sys.__stderr__)
            return tasks.ConsoleTaskManager(terminal)


class RemoteRunner(RunnerBase):
    def get_task_manager(self):
        return tasks.JsonRPCTaskManager(sys.__stderr__)


def get_runner_class():
    if sys.__stderr__.isatty():
        runner_class = ConsoleRunner
    else:
        runner_class = RemoteRunner
    return runner_class


def get_runner(*args, **kwargs):
    return get_runner_class(*args, **kwargs)


if __name__ == '__main__':
    from twisted import plugin
    from csat import collectors
    from csat.acquisition import base

    print list(plugin.getPlugins(base.ICollector, collectors))

    #get_runner(PipermailCollector()).run()
