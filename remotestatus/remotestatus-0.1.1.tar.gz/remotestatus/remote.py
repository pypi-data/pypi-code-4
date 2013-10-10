import json

from django.core.mail import send_mail

from paramiko import SSHClient
from paramiko.transport import ChannelException

from remotestatus.conf import DEFAULT_PROXY_HOSTNAME, DEFAULT_PROXY_USERNAME, \
    DEFAULT_PROXY_PORT, DEFAULT_KEY_FILE, DEFAULT_KNOWN_HOSTS_FILE, \
    USERS_TO_NOTIFY, NOTIFICATION_EMAIL_ADDRESS
from remotestatus.models import StatusHistory, RemoteBoxModel


class RemoteManager(object):
    """
    This class is used as a singleton and maintains an
    internal registry of 'discovered' and parsed `RemoteBoxes`
    according to the project's config.
    """
    def __init__(self):
        self.registry = {}

    def register_remote_box(self, remote_box):
        self.registry.update({remote_box.nickname: remote_box})

    def notify_admin(self, unreachable_remotes, invalid_procs):
        """
        Notify the necessary users with a rollup email regarding
        the remote boxes that were invalid.

        Expects a two lists of RemoteBoxes that were unreachable or
        have expected procs that are not running.
        """
        total_down = len(unreachable_remotes) + len(invalid_procs)

        # Build message body
        body = '''%(count)d of your remote boxes are currently unreachable or
        have expected processes that are not running.\n\n

        Unreachable Boxes: %(unreachable)s
        Reachable But Invalid Processes: %(invalid_procs)s
        ''' % {
            'count': total_down,
            'unreachable': '\n'.join([i.nickname for i in unreachable_remotes]),
            'invalid_procs': '\n'.join([i.nickname for i in invalid_procs])
        }

        send_mail(
            'ResponseStatus: %d of your remote boxes are down.' % total_down,
            body,
            NOTIFICATION_EMAIL_ADDRESS,
            USERS_TO_NOTIFY,
            fail_silently=False
        )

remote_manager = RemoteManager()

class RemoteBox(object):
    """
    An instance of remote connection, used to make calls to remote boxes
    to check their status and the status of any optional processes
    we expect them to be running.

    Assumes we're working with a proxy host and tunneling to the remote
    boxes.
    """
    def __init__(self, nickname, description, remote_username,
        remote_password,
        remote_port, forwarded_port, processes=[]):
        self.nickname = nickname
        self.description = description
        self.remote_username = remote_username
        self.remote_password = remote_password
        self.remote_port = remote_port
        self.remote_username = remote_username
        self.forwarded_port = forwarded_port
        self.processes = processes

    def check_remote_status(self):
        """
        Make a call to check the status of a box and to optionally
        check the status of any processes specified in the config
        for the particular box.

        Returns a tuple of statuses:
            1. Box Status: True/False if the box is reachable/unreachable
            2. Process Statuses: A dictionary of processes (keyed by
               self.processes) and each of their statuses (True/False
               if they are running/not running).
        Sample Response:
            >>> box = RemoteBox(...., processes=['foo', 'bar'])
            >>> box.check_remote_status()
            >>>
            >>> # Box is up; `foo` is running; `bar` is not running
            >>> (True, {'foo': True, 'bar': False})
        """
        box_status = False
        proc_statuses = {}

        # Create the client and connect to proxy server
        # NOTE: I would love to move this connection logic to a
        #       `get_client()` method but it appears paramiko's SSHClient
        #       disconnects after it loses scope - even if attempting to
        #       save the `client` as a class variable. Any refactor help
        #       would be appreciated.
        #           - http://stackoverflow.com/a/17317516/329902
        try:
            proxy_client = SSHClient()
            proxy_client.load_host_keys(DEFAULT_KNOWN_HOSTS_FILE)
            proxy_client.connect(
                DEFAULT_PROXY_HOSTNAME,
                port=DEFAULT_PROXY_PORT,
                username=DEFAULT_PROXY_USERNAME,
                key_filename=DEFAULT_KEY_FILE
            )
            print 'connected to proxy'

            # Get the transport and find create a `direct-tcpip` channel
            transport = proxy_client.get_transport()
            dest_addr = ('0.0.0.0', self.remote_port)
            src_addr = ('127.0.0.1', self.forwarded_port)
            channel = transport.open_channel("direct-tcpip", dest_addr, src_addr)

            # Create a connection to the remote box through the tunnel
            remote_client = SSHClient()
            remote_client.load_host_keys(DEFAULT_KNOWN_HOSTS_FILE)
            remote_client.connect(
                'localhost',
                port=self.forwarded_port,
                username=self.remote_username,
                password=self.remote_password,
                sock=channel
            )
            print 'connected to remote host'

            # The remote box is up
            box_status = True

        # If we cannot connect to the box, assume that all processes are down as well
        except ChannelException:
            for proc in self.processes:
                proc_statuses.update({proc: False})
            return (box_status, proc_statuses)

        # Box is up, check the status of each process in the list
        for proc in self.processes:
            print 'checking process: `%s`' % proc
            x, stdout, e = remote_client.exec_command('ps aux | grep %s | grep -v grep' % proc)
            out = stdout.readlines()
            print 'out', out
            print '-------'
            proc_statuses.update({proc: len(out) > 0})

        return (box_status, proc_statuses)

    def save_status_history(self, call_round, status):
        """
        Update the StatusHistory table with the RemoteBox's status findings.
        Takes a `call_round` so we can group this StatusHistory record with
        similar records made at the same time.
        """
        # Normalize the remote box based on its nickname
        remote_box, _ = RemoteBoxModel.objects.get_or_create(nickname=self.nickname)

        # Create a new StatusHistory record
        StatusHistory.objects.create(
            call_round=call_round,
            remote_box=remote_box,
            description=self.description,
            box_status=status[0],
            processes_output=json.dumps(status[1])
        )

    def is_reachable(self, status):
        " Returns True/False based on whether or not the remote box was up. "
        return status[0]

    def has_valid_procs(self, status):
        " Returns True/false based on whether or not the remote is running its expected procs. "
        return False not in [i for i in status[1].values()]
