"""Read only support for a vMessage mailbox."""

import io
import re
import mailbox
import email.utils

linesep = b'\r\n'

class Mailbox(mailbox._singlefileMailbox):
    """A vMessage mailbox."""

    def __init__(self, path, factory=None, create=True):
        """Initialize a vMessage mailbox."""
        mailbox._singlefileMailbox.__init__(self, path, factory, create)

    def _generate_toc(self):
        """Generate key-to-(start, stop) table of contents."""
        starts, stops = [], []
        self._file.seek(0)
        while True:
            line_pos = self._file.tell()
            line = self._file.readline()
            if line == b'BEGIN:VMSG' + linesep:
                if len(stops) < len(starts):
                    stops.append(line_pos)
                starts.append(line_pos)
            elif line == b'END:VMSG' + linesep:
                stops.append(self._file.tell())
            elif not line:
                stops.append(line_pos)
                break
        self._toc = dict(enumerate(zip(starts, stops)))
        self._next_key = len(self._toc)
        self._file_length = self._file.tell()

    def get_message(self, key):
        """Return a Message representation or raise a KeyError."""
        start, stop = self._lookup(key)
        self._file.seek(start)
        state = 0
        vcard = None
        originators = []
        recipients = []
        vmessage_property = io.BytesIO()
        vmessage_body_property = dict()
        vmessage_body_content = io.BytesIO()
        while True:
            line = self._file.readline()
            if not line:
                break
            elif state == 0: # reading <vmessage-object>
                if line == b'BEGIN:VMSG' + linesep:
                    state = 1
            elif state == 1: # reading <vmessage-property>
                if line == b'BEGIN:VCARD' + linesep:
                    vcard = io.BytesIO()
                    state = 2
                elif line == b'BEGIN:VENV' + linesep:
                    state = 3
                else:
                    vmessage_property.write(line.replace(linesep, b'\n'))
            elif state == 2: # reading <vmessage-originator>
                if line == b'BEGIN:VCARD' + linesep:
                    if vcard: # syntax error, but ...
                        originators.append(vCard(vcard))
                    vcard = io.BytesIO()
                elif line == b'END:VCARD' + linesep:
                    if vcard:
                        originators.append(vCard(vcard))
                        vcard = None
	        elif line == b'BEGIN:VENV' + linesep:
                    state = 3
                else:
                    if vcard:
                        vcard.write(line.replace(linesep, b'\n'))
            elif state == 3: # reading <vmessage-envelope>
                if line == b'BEGIN:VBODY' + linesep:
                    if vcard: # syntax error, but ...
                        recipients.append(vCard(vcard))
                    state = 4
                elif line == b'BEGIN:VCARD' + linesep:
                    if vcard: # syntax error, but ...
                        recipients.append(vCard(vcard))
                    vcard = io.BytesIO()
                elif line == b'END:VCARD' + linesep:
                    if vcard:
                        recipients.append(vCard(vcard))
                        vcard = None
                else:
                    if vcard:
                        vcard.write(line.replace(linesep, b'\n'))
            elif state == 4 or state == 5: # reading <vmessage-content>
                if line == b'END:VBODY' + linesep:
                    state = 6
                elif state == 4: # reading <vmessage-body-property>
                    if line.startswith(b'CHARSET='):
                        vmessage_body_property['CHARSET'] = line.replace(b'CHARSET=', b'').strip()
                    elif line.startswith(b'ENCODING='):
                        vmessage_body_property['ENCODING'] = line.replace(b'ENCODING=', b'').strip()
                    else:
                        vmessage_body_content.write(line.replace(linesep, b'\n'))
                        state = 5
                else:
                    vmessage_body_content.write(line.replace(linesep, b'\n'))
        msg = Message(vmessage_body_content.getvalue())
        if not 'Content-Transfer-Encoding' in msg and 'ENCODING' in vmessage_body_property:
            msg['Content-Transfer-Encoding'] = vmessage_body_property['ENCODING']
        if not msg.get_param('charset') and 'CHARSET' in vmessage_body_property:
            msg.set_param('charset', vmessage_body_property['CHARSET'])
        vmessage_property.seek(0)
        for line in vmessage_property:
            name, value, params = parse_header(line)
            msg.set_property(name.strip(), value.strip(), params)
        msg.set_originators(originators)
        msg.set_recipients(recipients)
        if not "From" in msg:
            msg["From"] = ','.join([vcard.formataddr() for vcard in originators])
        if not "To" in msg:
            msg["To"] = ','.join([vcard.formataddr() for vcard in recipients])
        return msg


class Message(mailbox.Message):
    """Message with vMessage-specific properties."""

    def __init__(self, message=None):
        """Initialize a vMessage message instance."""
        self._properties = dict()
        self._property_params = dict()
        self._originators = []
        self._recipients = []
        mailbox.Message.__init__(self, message)

    def set_property(self, header, value, params):
        """Set a vMessage property."""
        self._properties[header] = value
        self._property_params[header] = params

    def get_property(self, header):
        """Get a vMessage property."""
        return self._properties.get(header)

    def get_property_params(self, header):
        """Get vMessage property parameters."""
        return self._property_params.get(header)

    def get_property_param(self, header, name):
        """Get a vMessage property parameter."""
        if header in self._property_params:
            return self._property_params.get(header).get(name)
        else:
            return None

    def set_originators(self, originators):
        """Set a list of originator vCards."""
        self._originators = originators

    def get_originators(self):
        """Get a list of originator vCards."""
        return self._originators

    def set_recipients(self, recipients):
        """Set a list of recipient vCards."""
        self._recipients = recipients

    def get_recipients(self):
        """Get a list of recipient vCards."""
        return self._recipients

    def _explain_to(self, message):
        """Copy vMessage-specific state to message insofar as possible."""
        if isinstance(message, mailbox.MaildirMessage):
            if self.get_property('X-IRMC-STATUS') == 'UNREAD':
                message.set_subdir('cur')
            else:
                message.set_subdir('cur')
                message.add_flag('S')
        elif isinstance(message, mailbox._mboxMMDFMessage):
            if self.get_property('X-IRMC-STATUS') == 'READ':
                message.add_flag('R')
            message.set_from('MAILER-DAEMON')
        elif isinstance(message, mailbox.MHMessage):
            if self.get_property('X-IRMC-STATUS') == 'UNREAD':
                message.add_sequence('unseen')
        elif isinstance(message, mailbox.BabylMessage):
            if self.get_property('X-IRMC-STATUS') == 'UNREAD':
                message.add_label('unseen')
        elif isinstance(message, Message): # vmessage.Message
            for name in self._properties.iterkeys():
                message.set_property(name, self._properties[name], self._property_params[name])
            message.set_originators(self._originators)
            message.set_recipients(self._recipients)
        elif isinstance(message, mailbox.Message):
            pass
        else:
            raise TypeError('Cannot convert to specified type: %s' %
                            type(message))


class vCard(dict):
    """A vCard. """

    def __init__(self, fp):
        """Initialize a vCard instance."""
        self._raw = fp.getvalue()
        self._params = dict()
        fp.seek(0)
        for line in fp:
            name, value, params = parse_header(line)
            if name:
                self[name] = value
                self._params[name] = params

    def get_params(self, header):
        """Return header parameters."""
        return self._params.get(header)

    def get_param(self, header, name):
        """Return a header parameter."""
        return self._params.get(header).get(name) if header in self._params else None

    def formataddr(self):
        return email.utils.formataddr((self["N"], self["EMAIL"] if self["EMAIL"] else self["TEL"]))


def parse_header(header):
    """Parse a vMessage-style header, e.g. 'HEADERNAME;param1=value1;param2=value2:HEADERVALUE'.
       Return a tuple of (name, value, params)."""
    m = re.match("([^;]*)(?:;(.*))?:(.*)", header)
    if m.group(2):
        params = dict()
        for param in m.group(2).split(';'):
            kv = param.split('=')
            params[kv[0]] = kv[1]
        return m.group(1), m.group(3), params
    else:
        return m.group(1), m.group(3), None

