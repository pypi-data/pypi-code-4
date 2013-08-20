from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from Crypto.Cipher import AES
import base64


class Job(models.Model):
    """
    A container for all cron runs of the same name.
    Also stores the conditions under which an email should be sent,
    as well as a list of addresses to send to.
    """
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return u'%s' % self.name

    def set_addresses(self, address_list):
        """
        Sets the list of email addresses to the list given.
        address_list is a list of email address strings.
        """
        def make_address(add):
            e = EmailAddress()
            e.address = add
            return e
        address_models = map(make_address, address_list)
        self.emailaddress_set.all().delete()
        self.emailaddress_set.add(*address_models)

    def set_conditions(self, conditions):
        """ Sets the conditions under which to send an email. """
        for key in conditions:
            setattr(self.emailconditions, key, conditions[key])

    def clean(self):
        """
        A job must have at least one record.
        """
        if self.record_set.count() == 0:
            raise ValidationError(u'%s has no records.' % unicode(self))


class EmailConditions(models.Model):
    """
    Stores the conditions for when to send emailss.
    """
    email_on_bad_exit = models.BooleanField(default=True)
    email_on_stderr = models.BooleanField(default=False)
    job = models.OneToOneField(Job)


class EmailAddress(models.Model):
    """
    An email address. Essentially a Wrapper for EmailField and ForeignKey.
    """
    address = models.EmailField()
    job = models.ForeignKey(Job)


class GlobalEmailAddress(models.Model):
    """
    Another email field wrapper.
    These addresses are sent emails for every cron run that needs email output.
    """
    address = models.EmailField()


class EmailSettings(models.Model):
    """
    A data store for various server-side email settings.
    Allows customization for who to send emails as.
    There should always be exactly one instance of this model.
    """
    # A random 16 byte key. Do not expose.
    KEY = settings.SECRET_KEY[:16]
    email_host = models.CharField(max_length=200, default='localhost')
    email_port = models.IntegerField(default=25)
    email_host_user = models.CharField(max_length=200,
                                       blank=True, null=True)
    # This field is encrypted with AES while in the database.
    # The password should always be accessed with get_password().
    # Accessing directly gives the encrypted password instead.
    email_host_password = models.CharField(max_length=200,
                                           blank=True, null=True)
    use_tls = models.BooleanField()

    def pad(self, s):
        """
        AES requires the message have a length that is a multiple
            of the block size.
        This pads the string given to make that true.
        """
        bs = AES.block_size
        return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

    def unpad(self, s):
        """ Unpads the given string. """
        return s[0:-ord(s[-1])]

    def encrypt(self, password):
        """ Returns an encrypted password. """
        cipher = AES.new(EmailSettings.KEY)
        pw = cipher.encrypt(self.pad(password))
        # Django requires that saved strings are unicode.
        # Converting to unicode directly leads to errors.
        # Encode in Base64, then in unicode
        return unicode(base64.b64encode(pw))

    def decrypt(self, ciphertext):
        """ Returns the decrypted password. """
        text = base64.b64decode(ciphertext)
        cipher = AES.new(EmailSettings.KEY)
        return self.unpad(cipher.decrypt(text))

    def save(self, *args, **kwargs):
        """
        Encrypts the password before saving.
        Calling save() after the password is encrypted
            will lead to errors.
        """
        if self.email_host_password:
            self.email_host_password = self.encrypt(self.email_host_password)
        super(EmailSettings, self).save(*args, **kwargs)

    def get_password(self):
        """
        Decrypts and returns the stored password.
        """
        if self.email_host_password:
            return self.decrypt(self.email_host_password)
        else:
            return self.email_host_password

    def get_absolute_url(self):
        return reverse('settings_update', args=[self.pk])


class Record(models.Model):
    """
    Every time monitor.py runs a command, it creates a record.
    This contains information about that command.
    Start time, run time, exit code, and output are stored.
    """
    command = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    exit_code = models.IntegerField(blank=True, null=True)
    # Run time is in seconds
    run_time = models.DecimalField(decimal_places=5,
                                   max_digits=200,
                                   blank=True,
                                   null=True)
    has_err = models.BooleanField(default=False)
    job = models.ForeignKey(Job)

    class Meta:
        ordering = ['-start_time']

    def __unicode__(self):
        return u'%s, %s' % (self.command, str(self.start_time))

    def plain_log(self):
        """ Returns a plain text log, or None if there is no output. """
        try:
            return self.log_set.get(log_type=Log.PLAIN_LOG_TYPE)
        except Log.DoesNotExist:
            pass

    def html_log(self):
        """ Returns an html log, or None if there is no output. """
        try:
            return self.log_set.get(log_type=Log.HTML_LOG_TYPE)
        except Log.DoesNotExist:
            pass

    def clean(self):
        """
        If the record has an exit code, it must have a run time, and vice versa
        Both could be 0, so check against None instead
        """
        if self.exit_code is None and self.run_time is not None:
            raise ValidationError("Record has a run time, but no exit code")
        if self.exit_code is not None and self.run_time is None:
            raise ValidationError("Record has an exit code, but no run time")
        # A record should have 0 logs or 2 logs.
        # If a record has two logs, one should be of type PLAIN_LOG_TYPE
        # And the other of type HTML_LOG_TYPE
        num_logs = self.log_set.count()
        if num_logs not in (0, 2):
            raise ValidationError("Record must have 0 or 2 logs.")
        if num_logs == 2:
            # Assume that the logs are valid
            logs = self.log_set.all()
            if logs[0].log_type == logs[1].log_type:
                raise ValidationError("Record has two logs of the same type")


class Log(models.Model):
    """
    A wrapper for the name and text of an output log.
    """
    NULL_LOG_TYPE = 0  # A known to be wrong log type, for use in tests
    PLAIN_LOG_TYPE = 1
    HTML_LOG_TYPE = 2
    VALID_LOG_TYPES = (PLAIN_LOG_TYPE, HTML_LOG_TYPE)
    log_name = models.CharField(max_length=200)
    log_text = models.TextField()
    log_type = models.IntegerField()
    record = models.ForeignKey(Record)

    def __unicode__(self):
        if self.log_type == Log.PLAIN_LOG_TYPE:
            return u'%s, text log' % self.log_name
        elif self.log_type == Log.HTML_LOG_TYPE:
            return u'%s, html log' % self.log_name
        else:
            return u'%s, invalid log' % self.log_name

    def clean(self):
        if self.log_type not in Log.VALID_LOG_TYPES:
            raise ValidationError('Log has an invalid log type')

    def get_absolute_url(self):
        """ Used in displaying the logs. """
        if self.log_type == Log.HTML_LOG_TYPE:
            return reverse('html_log', args=[self.record.pk])
        elif self.log_type == self.PLAIN_LOG_TYPE:
            return reverse('plain_log', args=[self.pk])
        else:
            raise ValueError("Tried to get url of an invalid log")
