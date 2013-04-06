# -*- coding: utf-8 -*-
"""
Logging management for Dynamic DynamoDB
"""
import os.path
import logging


class Logger:
    """ Logging class """
    def __init__(self, name='dynamic-dynamodb', level='info',
                 log_file=None, dry_run=False):
        """ Instanciate the logger

        :type name: str
        :param name: Logger name
        :type level: str
        :param level: Log level [debug|info|warning|error]
        :type log_file: str
        :param log_file: Path to log file (if any)
        :type dry_run: bool
        :param dry_run: Add dry-run to the output
        """
        # Set up the logger
        self.logger = logging.getLogger(name)
        if level.lower() == 'debug':
            self.logger.setLevel(logging.DEBUG)
        elif level.lower() == 'info':
            self.logger.setLevel(logging.INFO)
        elif level.lower() == 'warning':
            self.logger.setLevel(logging.WARNING)
        elif level.lower() == 'error':
            self.logger.setLevel(logging.ERROR)
        else:
            self.logger.setLevel(logging.INFO)

        # Formatting
        if dry_run:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - dryrun - %(message)s')
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler
        if log_file:
            file_handler = logging.FileHandler(os.path.expanduser(log_file))
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, *args, **kwargs):
        """ Log on debug level """
        self.logger.debug(*args, **kwargs)

    def error(self, *args, **kwargs):
        """ Log on error level """
        self.logger.error(*args, **kwargs)

    def info(self, *args, **kwargs):
        """ Log on info level """
        self.logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """ Log on warning level """
        self.logger.warning(*args, **kwargs)
