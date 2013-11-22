#!/usr/bin/env python
# coding=utf-8

if __name__ == '__main__':
    from cool_logging import getLogger
    logger = getLogger('testing')

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warn("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    logger.debug("This is a debug message, with a quite long text that "
                 "will certainly exceed the 70 columns limit allowed "
                 "by the custom formatter.\n"
                 "This is another line of text, at last..")

    logger.debug(u"Øk, ñøw let's try with sömë utf8 cháráctérß..")
    logger.debug(u"\xd8k, \xf1\xf8w let's try with s\xf6m\xeb utf8 ch\xe1r\xe1ct\xe9r\xdf..")
