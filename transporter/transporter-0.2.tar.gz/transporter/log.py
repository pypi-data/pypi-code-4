import logging


def get_logger(name=None, file_name=None):

    from tornado.options import options
    options.logging = None

    if not name:
        name = __name__
    logger = logging.getLogger(name)
    formatter = logging.Formatter('%(name)s >>> %(asctime)s %(levelname)s - %(message)s')
    if file_name:
        handler = logging.FileHandler('server.log')
        logger.addHandler(handler)
        handler.setFormatter(formatter)
    #else:
    #    ch = logging.StreamHandler()
    #    ch.setFormatter(formatter)
    #    logger.addHandler(ch)

    logger.setLevel(logging.DEBUG)
    logger.debug("returning logger")
    return logger