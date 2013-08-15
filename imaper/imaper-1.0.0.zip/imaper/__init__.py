from imapclient import IMAPClient, DELETED, SEEN, FLAGGED
from .parser import parse_email

__version__ = "1.0.0"
__all__ = ['Imaper', 'Message']

class Imaper:
    """Connects to the IMAP server with the given information.

    :param hostname: The IMAP server to connect to.
    :param username: The username to login with.
    :param password: The password to use.
    :param port: Server port (default=143)
    :param ssl: Use SSL? (default=False)
    :param connect: Whether to connect immediately (default=True)
    :param folder: Which folder to connect to (default='INBOX')
    """

    def __init__(self, hostname, username, password, port=143, ssl=False,
                 connect=True, folder='INBOX'):
        self.hostname = hostname
        self.port = port
        self.ssl = ssl
        self.username = username
        self.password = password
        self.folder = folder

        if connect:
            self.connect()
        else:
            self.server = None

    def connect(self):
        """Opens the connection and logs in to the IMAP server."""
        self.server = IMAPClient(self.hostname, use_uid=True, ssl=self.ssl)
        self.server.login(self.username, self.password)

        if isinstance(self.folder, str):
            self.select_folder(self.folder)

    def select_folder(self, folder):
        """Selects the given folder on the IMAP connection.  This is
        the folder which all future commands will be ran against.

        :param folder: The folder to select.
        """
        self.folder = self.server.select_folder(folder)

    def message_count(self):
        """The total number of messages in the selected folder.

        :return: Number of messages.
        """
        return int(self.folder[u'EXISTS'])

    def unread_count(self):
        """The number of unread messages in the selected folder.

        :return: Number of unread messages.
        """
        return len(self.server.search(_build_criteria(unread=True)))

    def read_count(self):
        """The number of messages in the selected folder that are
        marked as read.

        :return: Number of read messages.
        """
        return self.message_count() - self.unread_count()

    def messages(self, **criteria):
        """A Generator that iterates over the messages in the current
        folder.

        Each message is yielded as a :class:`Message` object.

        :param criteria: The search criteria to use (passed through
                         to :func:`_build_criteria`).
        """
        messages = self.server.search(_build_criteria(**criteria))
        response = self.server.fetch(messages, [
            'BODY.PEEK[]',
            'FLAGS',
            'RFC822.SIZE'
        ])

        for msgid, data in response.iteritems():
            email_object = parse_email(str(data[u'BODY[]']))
            email_object['msgid'] = msgid
            email_object['size'] = data[u'RFC822.SIZE']
            email_object['flags'] = data[u'FLAGS']
            yield Message(self, **email_object)


class Message(object):
    """Builds the message.

    :param mb: The Imaper instance that this message came from.
    :param properites: The message properites.
    """

    def __init__(self, mb, **properties):
        self.mb = mb
        self.__dict__.update(properties)
        self._parse_flags()

    def keys(self):
        """Gets all the property names as a list.

        :return: A list of the message property names.
        """
        return self.__dict__.keys()

    def delete(self):
        """Marks this message as deleted."""
        self.add_flags(DELETED)

    def undelete(self):
        """unnarks this message as deleted."""
        self.remove_flags(DELETED)

    def mark_read(self):
        """Marks this message as read."""
        self.add_flags(SEEN)

    def mark_unread(self):
        """Marks this message as unread."""
        self.remove_flags(SEEN)

    def mark_flagged(self):
        """Marks this message as flagged."""
        self.add_flags(FLAGGED)

    def unmark_flagged(self):
        """Unmarks this message as flagged."""
        self.remove_flags(FLAGGED)

    def add_flags(self, flags):
        """Adds the given flags to this message

        :param flags: Either a string containing a single flag or a
                      list of flags.
        """
        resp = self.mb.server.add_flags(self.msgid, flags)
        self.flags = resp.get(1, (None,))
        self._parse_flags()

    def remove_flags(self, flags):
        """Removes the given flags to this message

        :param flags: Either a string containing a single flag or a
                      list of flags.
        """
        resp = self.mb.server.remove_flags(self.msgid, flags)
        self.flags = resp.get(1, (None,))
        self._parse_flags()

    def _parse_flags(self):
        """Parses the flags tuple into more usable properties."""
        self.flagged = FLAGGED in self.flags
        self.deleted = DELETED in self.flags
        self.read = SEEN in self.flags

    def __repr__(self):
        return repr(self.__dict__)


def _build_criteria(
        deleted=False,
        unread=False,
        sent_from=False,
        sent_to=False,
        date_gt=False,
        date_lt=False):
    """Builds the criteria list for an IMAP search call.

    :param deleted: Include deleted messages.
    :param unread: Include only unread messages.
    :param sent_from: Only messages with the given 'from' address.
    :param sent_to: Only messages with the given 'to' address.
    :param date_gt: Only messages sent *after* the given date.
    :param date_lt: Only messages sent *before* the given date.
    :return: A list of criteria
    """
    if deleted:
        query = ['ALL']
    else:
        query = ['NOT DELETED']

    if unread:
        query = ['UNSEEN']

    if sent_from:
        query.append('FROM "{0}"'.format(sent_from))

    if sent_to:
        query.append('TO "{0}")'.format(sent_to))

    if date_gt:
        query.append('SINCE "{0}"'.format(date_gt))

    if date_lt:
        query.append('BEFORE "{0}"'.format(date_lt))

    return query
