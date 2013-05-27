'''
Errors and exceptions
'''

class MailError(Exception):
    '''
    An error which should be mailed back to the sender
    '''
    def __init__(self, msg):
        super(MailError, self).__init__(msg)
