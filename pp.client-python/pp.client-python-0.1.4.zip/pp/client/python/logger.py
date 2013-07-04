################################################################
# pp.client - Produce & Publish Python Client
# (C) 2013, ZOPYX Ltd, Tuebingen, Germany
################################################################

import logbook

LOG = logbook.Logger('pp.client.python')
def getLogger(debug=0):
    LOG.level = logbook.DEBUG if debug else logbook.INFO
    return LOG
