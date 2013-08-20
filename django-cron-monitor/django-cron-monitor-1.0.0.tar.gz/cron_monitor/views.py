from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.contrib.auth import logout
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
import datetime
import times
from email.mime.text import MIMEText
import smtplib
from tzlocal import get_localzone
from cStringIO import StringIO
from cron_monitor.models import (Job, Record, Log, EmailConditions,
                                 EmailSettings)
from cron_monitor.models import GlobalEmailAddress
from cron_monitor.forms import SettingsForm
from xml.sax.saxutils import escape
import json


def index(request):
    """
    The home page.
    Displays all jobs, all those jobs' records, and those records' statuses.
    Additionally, has links to update email settings and addresses.
    """
    # Obtain a relevant context for the template to render.
    jobs = Job.objects.all()
    data = {'jobs': jobs,
            'update': EmailSettings.objects.all().exists()}
    if data['update']:
        data['settings'] = EmailSettings.objects.all()[0]
    return render(request, 'cron_monitor/index.html', data)


def logout_view(request):
    """ Logouts the user and redirects to the home page. """
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@csrf_exempt
@require_POST
def begin_run(request):
    """
    Called before every run wrapped by monitor.py, this creates
        and stores a record of that run.
    Returns the id of the record, which is later used to update the record.
    Because this needs to be called from outside Django, it is csrf_exempt.
    """
    # Retrieve data from POST request
    name = request.POST['name']
    cmd = request.POST['command']
    emails = request.POST.getlist('emails')
    conditions = json.loads(request.POST['conditions'])
    # If start_time is not in the post, use the current time
    if 'start_time' in request.POST:
        start_time = request.POST['start_time']
    else:
        start_time = datetime.datetime.now()

    # Check if there is a job for the given name.
    # Create it if there isn't one
    try:
        job = Job.objects.get(name=name)
    except Job.DoesNotExist:
        job = Job.objects.create(name=name)
        EmailConditions.objects.create(job=job)
    # Create the record, and update various job attributes.
    record = job.record_set.create(command=cmd,
                                   start_time=start_time)
    job.set_conditions(conditions)
    job.emailconditions.save()
    job.set_addresses(emails)
    job.full_clean()
    job.save()
    # This should only be called by the outside monitor.py
    # So, this does no redirection.
    return HttpResponse(str(record.id))


@csrf_exempt
@require_POST
def finished_run(request):
    """
    Called after every run wrapped by monitor.py, this updates
        the record for the run that was created earlier.
    Because this needs to be called from outside Django, it is csrf_exempt.
    """
    # Obtain the record id
    rid = request.POST['rec_id']
    try:
        rid = int(rid)
    except ValueError:
        # This error could be better
        raise ValidationError("ID given to finish was not an integer")

    # Update the record
    record = get_object_or_404(Record, pk=rid)
    record.exit_code = request.POST['exit_code']
    # If run_time is not in the post, compare the current time
    # to the start time. This is less accurate (server connection delays.)
    if 'run_time' in request.POST:
        record.run_time = request.POST['run_time']
    else:
        td = datetime.datetime.now() - record.start_time
        record.run_time = td.total_seconds()

    if request.POST['err_log']:
        record.has_err = True

    # check if there is any output
    if request.POST['out_log'] or request.POST['err_log']:
        # If there is, merge stdout and stderr together and save to logs
        # stdout and stderr are timestamped, which makes merging possible
        timestamp = (request.POST['timestamp'] == 'True')
        plain, html = StringIO(), StringIO()
        merge(timestamp,
              StringIO(request.POST['out_log']),
              StringIO(request.POST['err_log']),
              plain,
              html)
        record.log_set.create(log_name=request.POST['plain_log_name'],
                              log_text=plain.getvalue(),
                              log_type=Log.PLAIN_LOG_TYPE)
        record.log_set.create(log_name=request.POST['html_log_name'],
                              log_text=html.getvalue(),
                              log_type=Log.HTML_LOG_TYPE)
        plain.close()
        html.close()

    # save record, check for email notification
    record.full_clean()
    record.save()
    check_send_emails(record)
    # Again, only called by monitor.py. May give more info later
    return HttpResponse("Updated record of job run")


def html_escape(text):
    """
    Escapes the text for html.
    Django does this automatically, but for our use case we need to sometimes
        do it manually.
    """
    # The standard escape from xml.sax.saxutils does &, <, and >.
    # Table accounts for others.
    escape_table = {'"': "&quot;",
                    "'": "&#x27;",
                    "/": "&#x2F;"}
    return escape(text, escape_table)


def get_time_and_text(line):
    """
    Takes a line of the format "time text" and returns
        a tuple of the time and the text
    """
    if line:
        tokens = line.split(' ', 1)
        if len(tokens) != 2:
            raise ValueError("get_time_and_text() could not split %s" % line)
        return float(tokens[0]), tokens[1]
    else:
        return None, None


def local_time_string(time):
    """ Converts a Unix timestamp into a readable string in local time """
    now = times.to_universal(time)
    return times.format(now, get_localzone())


def merge(timestamp, f_out, f_err, f_plain_merged, f_html_merged):
    """
    Merges the lines from f_out and f_err together.
    Assumes f_out and f_err are in chronological order.
    We need to modify lines for html coloring,
        but having plain text is useful as well.
    So, we write the lines to two different string buffers.
    Returns nothing, have to access string buffers to get data.
    """
    def write(line, time, out):
        if timestamp:
            line = '%s %s' % (local_time_string(time), line)
        f_plain_merged.write(line)
        if out:
            f_html_merged.write('<span class="stdout">%s</span>'
                                % html_escape(line))
        else:
            f_html_merged.write('<span class="stderr">%s</span>'
                                % html_escape(line))
    # Compare line times to find printing order
    t_out, o_line = get_time_and_text(f_out.readline())
    t_err, e_line = get_time_and_text(f_err.readline())
    while o_line and e_line:
        if t_out < t_err:
            write(o_line, time=t_out, out=True)
            t_out, o_line = get_time_and_text(f_out.readline())
        else:
            write(e_line, time=t_err, out=False)
            t_err, e_line = get_time_and_text(f_err.readline())

    # Add the rest
    if o_line:
        while o_line:
            write(o_line, time=t_out, out=True)
            t_out, o_line = get_time_and_text(f_out.readline())
    else:
        while e_line:
            write(e_line, time=t_err, out=False)
            t_err, e_line = get_time_and_text(f_err.readline())
    # Clean up
    f_out.close()
    f_err.close()


@require_POST
def delete_record(request):
    """ Deletes a record from the database. """
    rid = request.POST['rec_id']
    try:
        rid = int(rid)
    except ValueError:
        return HttpResponseBadRequest("ID given to delete was not an integer")

    record = get_object_or_404(Record, pk=rid)
    record.delete()
    # If the job that owns this now has 0 records, delete it too
    if record.job.record_set.count() == 0:
        record.job.delete()
    return HttpResponseRedirect(reverse('index'))


@require_POST
def delete_job(request):
    """ Delete a job and all records for that job. """
    jid = request.POST['job_id']
    try:
        jid = int(jid)
    except ValueError:
        return HttpResponseBadRequest(
            "ID given to delete job was not an integer"
        )

    job = get_object_or_404(Job, pk=jid)
    job.delete()
    return HttpResponseRedirect(reverse('index'))


def see_html_log(request, rec_id):
    """ Display the html log for the cron run. """
    # rec_id is typechecked in urls.py (the regex only accepts numbers)
    record = get_object_or_404(Record, pk=rec_id)
    html_log = record.html_log()
    response = render(request,
                      'cron_monitor/styled_log.html',
                      {'log': html_log})
    response['Content-Disposition'] = 'filename=%s' % html_log.log_name
    return response


def see_plain_log(request, log_id):
    """ Displays the plain text log correspond to the given id. """
    response = HttpResponse(content_type='text/plain')
    # log_id is typechecked by the regex as well
    log = get_object_or_404(Log, pk=log_id)
    response['Content-Disposition'] = 'filename=%s' % log.log_name
    response.write(log.log_text)
    return response


def check_send_emails(record):
    """
    Checks whether to send email notifications for the given cron run.
    If it should, then send those emails.
    """
    # Obtain email conditions.
    conditions = record.job.emailconditions
    # Check the conditions and records to see if email should be sent.
    exit_code = record.exit_code
    should_send = (conditions.email_on_bad_exit and exit_code != 0) or \
                  (conditions.email_on_stderr and record.has_err)
    if should_send:
        # Format the email
        log = record.plain_log().log_text if record.plain_log() else ''
        # Better start_time printing here?
        subject = 'Failed %s at %s' % (record.command, str(record.start_time))
        message = 'The command "%s" that ran at %s has failed.\n\n' \
                  'Exit code: %d\n\n' \
                  'Log:\n%s' \
                  % (record.command, str(record.start_time), exit_code, log)
        # Obtains job addresses and global addresses, put together
        address_list = map(lambda ea: ea.address,
                           record.job.emailaddress_set.all())
        address_list.extend(map(lambda gea: gea.address,
                                GlobalEmailAddress.objects.all()))
        if address_list:
            send_email(subject, message, address_list)


def send_email(subject, message, addresses):
    """
    Sends an email to every person in addresses.
    One update could be to send an email to each person individually,
        instead of sending to the entire list. Sending to the entire list
        makes it more likely to go to spam.
    """
    if not EmailSettings.objects.all().exists():
        print 'Email settings are not configured, so no emails can be sent.'
        return
    sender = 'monitor@localhost'  # Default sender, can be changed if desired
    settings = EmailSettings.objects.all()[0]
    session = smtplib.SMTP(settings.email_host, settings.email_port)
    # Some preliminary connections
    if settings.use_tls:
        session.ehlo()
        session.starttls()
        session.ehlo()
    if settings.email_host_user and settings.email_host_password:
        # Reobtain login name and password
        session.login(settings.email_host_user, settings.get_password())
        sender = settings.email_host_user

    # Construct email headers and send the email
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(addresses)
    session.sendmail(msg['From'], addresses, msg.as_string())
    session.quit()


class SettingsCreate(CreateView):
    """
    A view for creating email settings.
    This should only be linked if Django detects that no email settings exist.
    This page is only accessible if the user is logged in,
        and if that user has permission to create EmailSettings objects.
    However, if both of those are true,
        and the user accesses this page directly through the address bar,
        this allows for creation of more than 1 EmailSettings.
    TODO fix that
    """
    model = EmailSettings
    form_class = SettingsForm
    template_name_suffix = '_add_form'
    success_url = reverse_lazy('index')


class SettingsUpdate(UpdateView):
    """
    A view for updating an EmailSettings object.
    Like SettingsCreate, this is behind a login and permission required page.
    """
    model = EmailSettings
    form_class = SettingsForm
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('index')


class GlobalEmailListView(ListView):
    """
    Displays the list of email addresses that are notified of every cron run
        that produces output.
    """
    model = GlobalEmailAddress
    context_object_name = 'address_list'


class GlobalEmailCreate(CreateView):
    """
    A view for creating a GlobalEmailAddress.
    Redirects to the list of global email addresses on success.
    Also behind a login and permission required wall.
    """
    model = GlobalEmailAddress
    success_url = reverse_lazy('global')


@require_POST
def global_email_delete(request):
    """
    Deletes all GlobalEmailAddresses that are specified in the POST request.
    Redirects to the list of global email addresses when done.
    Behind a login and permission required wall.
    """
    for key in request.POST:
        try:
            key = int(key)
            GlobalEmailAddress.objects.get(pk=key).delete()
        except ValueError:
            pass
        except GlobalEmailAddress.DoesNotExist:
            pass
    return HttpResponseRedirect(reverse('global'))
