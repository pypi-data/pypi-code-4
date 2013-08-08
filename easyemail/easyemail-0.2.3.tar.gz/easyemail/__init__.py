"""Small lib abstracting creation and sending emails with smtplib.
This is work in progress, please do not use it in production.

"""

from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


class EasyEmail(object):

    """Send prepared email using smtplib buildin capabilities.

    This class aims to abstract sending emails from templates, for now it
    covers only mako templating system but jinja2 is on its way.

    Usage::

        >>> email = EasyEmail()
        >>> email.to = ["roman@sample.com", "roman@sample.eu"]
        >>> email.subject = "Enlarge your library for FREE!"
        >>> email.sender = "kingslawyer@sample.com"
        >>> email.send()

    or::

        >>> email = EasyEmail(
        ...             to="kingslawyer@sample.com",
        ...             subject="No",
        ...             sender="roman@sample.com"
        ...         )
        >>> email.send()

    :param to: Defaults to empty list, can be list of emails or string.
    :param sender: Defaults to empty string - this should contain email
        of the sender (from).
    :param subject: Defaults to empty string - should contain subject of
        the message.

    """

    def __init__(self, to=[], sender='', subject=''):
        self.message = MIMEMultipart('alternative')
        self.subject = subject
        self.to = to
        self.sender = sender

    def attach_image(self, image_content, subtype=None):
        """Attach image binary data to message.

        :param image_content: :py:class:`email.mime.image.MIMEImage`
            parameter `_imagedata`.
        :param _subtype: :py:class:`email.mime.image.MIMEImage`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEImage(image_content, _subtype=subtype))

    def attach_binary(self, binary_data, subtype=None):
        """Attach binary data to message.

        :param binary_data: :py:class:`email.mime.application.MIMEApplication`
            parameter `_data`.
        :param _subtype: :py:class:`email.mime.application.MIMEApplication`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEApplication(binary_data, _subtype=subtype))

    def attach_text(self, text, subtype=None):
        """Attach text data to message.

        :param text: :py:class:`email.mime.text.MIMEText`
            parameter `_text`.
        :param _subtype: :py:class:`email.mime.text.MIMEText`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEText(text, _subtype=subtype))

    def attach_audio(self, audio_data, subtype=None):
        """Attach text data to message.

        :param audio_data: :py:class:`email.mime.audio.MIMEAudio`
            parameter `_audiodata`.
        :param _subtype: :py:class:`email.mime.audio.MIMEAudio`
            parameter `_subtype` (defaults to None).

        """
        self.message.attach(MIMEAudio(audio_data, _subtype=subtype))

    def load_template(self, template_file_path, context, data_type='html',
                      ttype='mako', filelike=None):
        """Load text template and attach to message.

        :param template_file_path: file path to template file.
        :param context: optional context for rendered template.
        :param data_type: mapped as `_subtype` in :func:`attach_text`.
        :param ttype: Template format type (defaults fo `mako`, `jinja2` is
            now an option).
        :param filelike: For easier testing - you can supply StrinIO with
            template to render from it.

        """

        if ttype == 'mako':
            from mako.template import Template
        elif ttype == 'jinja2':
            from jinja2 import Template

        if not filelike:
            template_file = open(template_file_path, 'r')
        else:
            template_file = filelike

        try:
            template = Template(template_file.read()).render(**context)
            self.attach_text(template, data_type)
        except Exception:
            # I have no better idea how to make sure that file fill be closed.
            pass
        finally:
            template_file.close()

    def send(self, connection_type='smtp', authentication=False,
             **smtp_params):
        r"""Send prebuilded message.

        :param connection_type: string with type of connection. Possible
            choices are: `smtp` (default), `ssl` and `tls`.
        :param authentication: `boolean` (default False), set it to True if
            server that you use for sending uses authentication. If this
            parameter is set to True - you need to supply `login` and
            `password` keyword arguments.
        :param \*\*smtp_params: Additional parameters depending on
            `connection_type` chosen. For full list and description please go
            to :py:mod:`smtplib`.

        """

        self._compose()
        smtp_connection = self._connect(
            connection_type, authentication, **smtp_params
        )
        smtp_connection.sendmail(
            from_addr=self.sender,
            to_addrs=self.to,
            msg=self.message.as_string()
        )
        smtp_connection.quit()

    def dump(self):
        """Generate simple testing drop of message.

        Returns string that has all the information that would be sent.

        """

        self._compose()
        dumped = self.message.as_string()

        return dumped

    def _connect(self, connection_type, authentication, **smtp_params):
        r"""Create smtplib connection for different connection types.

        Returns active smtp connection that need to be closed after usage.

        :param connection_type: string with type of connection. Possible
            choices are: `smtp` (default), `ssl` and `tls`.
        :param authentication: `boolean` (default False), set it to True if
            server that you use for sending uses authentication. If this
            parameter is set to True - you need to supply `login` and
            `password` keyword arguments.
        :param \*\*smtp_params: Additional parameters depending on
            `connection_type` chosen. For full list and description please go
            to :py:mod:`smtplib`.

        """

        if connection_type == 'smtp':
            smtp_connection = smtplib.SMTP(
                smtp_params.get('host', 'localhost'),
                smtp_params.get('port', 25),
                smtp_params.get('local_hostname'),
                smtp_params.get('timeout')
            )

        elif connection_type == 'ssl':
            smtp_connection = smtplib.SMTP_SSL(
                smtp_params.get('host'),
                smtp_params.get('port'),
                smtp_params.get('local_hostname'),
                smtp_params.get('keyfile'),
                smtp_params.get('certfile'),
                smtp_params.get('timeout')
            )

        elif connection_type == 'tls':
            smtp_connection = smtplib.SMTP(
                smtp_params.get('host'),
                smtp_params.get('port'),
                smtp_params.get('local_hostname'),
                smtp_params.get('timeout')
            )
            smtp_connection.starttls(
                smtp_params.get('keyfile'),
                smtp_params.get('certfile')
            )

        if authentication:
            smtp_connection.login(
                smtp_params.get('login'),
                smtp_params.get('password')
            )

        return smtp_connection

    def _compose(self):
        """Compose message from object attributes."""

        self.message['Subject'] = self.subject
        self.message['From'] = self.sender
        if isinstance(self.to, list):
            self.message['To'] = ', '.join(self.to)
        else:
            self.message['To'] = self.to
