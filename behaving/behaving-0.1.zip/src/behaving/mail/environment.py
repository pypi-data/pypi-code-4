import logging
import os

from behaving.fsinspector import FSInspector

logger = logging.getLogger('behaving')


def before_all(context):
    if not hasattr(context, 'mail_path'):
        path = os.path.join(os.getcwd(), 'mail')
        try:
            if not os.path.isdir(path):
                os.mkdir(path)
            logger.info('No default mail path for mailmock is specified. Using %s' % path)
        except OSError:
            logger.error('No default mail path for mailmock is specified. Unable to create %s' % path)
            exit(1)
        context.mail_path = path
    context.mail = FSInspector(context.mail_path)
    context.mail.clear()


def before_feature(context, feature):
    pass


def before_scenario(context, scenario):
    pass


def after_feature(context, feature):
    pass


def after_scenario(context, scenario):
    context.mail.clear()


def after_all(context):
    pass
