#!/usr/bin/env python

import os
import sys
import time
import datetime
import requests
import argparse
from ConfigParser import ConfigParser
import subprocess
import json


def read_config(filename):
    """
    Does the following:
    1. ConfigParser tries to read the filename given
    2. If filename is None, or there is no file with that name,
        then read the default file (~/.cronmonrc)
    3. If the default file does not exist, create it with the defaults
        that are shown below.
    """
    cp = ConfigParser()
    cp.add_section('Server')
    cp.add_section('Logging')
    cp.add_section('Email')
    cp.set('Server', 'domain', 'http://localhost:8000')
    cp.set('Server', 'app_url', 'cron-monitor')
    cp.set('Logging', 'timestamp', 'False')
    cp.set('Email', 'email_list', '')
    cp.set('Email', 'email_on_bad_exit', 'True')
    cp.set('Email', 'email_on_stderr', 'False')
    if not filename or not cp.read(filename):
        default = os.path.expanduser('~')
        default = os.path.join(default, '.cronmonrc')
        if not cp.read(default):
            with open(default, 'w') as cfg:
                cp.write(cfg)
    return cp


def notify_of_start(args, server, emails, email_conditions):
    """
    Sends a post request that notifies the server that a run is about to start.
    """
    start = str(datetime.datetime.now())
    payload = {'start_time': start,
               'command': ' '.join(args.script_args)}
    payload['name'] = args.name if args.name else payload['command']
    payload['emails'] = emails
    # json is used only to make sending the dict easier
    payload['conditions'] = json.dumps(email_conditions)

    # Ideally this would take the url from urls.py, but that's not an option
    # Client-server separation and all that.
    r = requests.post('%s/begin' % server, data=payload)
    # Check that request passed.
    r.raise_for_status()

    # The returned request gives the record id, nothing more
    try:
        rec_id = int(r.text)
    except ValueError:
        raise ValueError("monitor.py did not receive a valid id: %s" % r.text)
    return rec_id


def run_process(command, timestamp):
    """
    Runs the given command, sending a POST request to the server on completion.

    The goal here is to both be able to see whether a line of output
    is from stdout or stderr, while having the log be one continuous chunk
    in chronological order.

    To do this, both stdout and stderr are piped to a script
    that adds a timestamp to each line. The lines are merged
    server-side upon run completion.
    """
    start_time = time.time()
    script_path = os.path.join(os.path.dirname(__file__), 'timestamper.py')
    # By default, stdout is fully buffered.
    # The stdbuf utility makes it line buffered. This will not always work,
    #   but if the child process is specifying fully buffered,
    #   there isn't much that can be done anyways.
    stdbuf = "stdbuf -oL -eL".split()
    p1 = subprocess.Popen(stdbuf + command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    p2 = subprocess.Popen(['python', script_path],
                          stdin=p1.stdout,
                          stdout=subprocess.PIPE)
    p3 = subprocess.Popen(['python', script_path],
                          stdin=p1.stderr,
                          stdout=subprocess.PIPE)
    # Python documentation says this is needed
    # for a SIGPIPE signal to be received/
    p1.stdout.close()
    p1.stderr.close()
    p1.wait()
    run_time = time.time() - start_time
    # Just to be safe, probably don't need these waits.
    p2.wait()
    p3.wait()
    payload = {'exit_code': p1.returncode,
               'run_time': run_time,
               'out_log': p2.stdout.read(),
               'err_log': p3.stdout.read(),
               'timestamp': str(timestamp)}
    p2.stdout.close()
    p3.stdout.close()
    return payload


def notify_of_end(server, payload):
    """ Sends the given payload in a POST request to the server. """
    r = requests.post('%s/finish' % server, data=payload)
    r.raise_for_status()


def get_emails(args, config):
    """
    If the emails command line argument is specified, returns
    a list of those emails.

    Otherwise, returns a list of all emails from the config file

    Both are in the form of comma separated strings.
    """
    # Removed whitespace, filter out all empty strings.
    if args.emails:
        args_emails = [t.strip() for t in args.emails.split(',')]
        args_emails = filter(lambda s: s, args_emails)
        return args_emails
    else:
        config_emails = [t.strip() for t in
                         config.get('Email', 'email_list').split(',')]
        config_emails = filter(lambda s: s, config_emails)
        return config_emails


def get_conditions(config):
    """
    Takes a parsed config file, and converts it into a dictionary.
    Although somewhat useless now, it could be useful if more conditions
        for email notification are wanted.
    """
    attributes = {
        'email_on_bad_exit': config.getboolean('Email', 'email_on_bad_exit'),
        'email_on_stderr': config.getboolean('Email', 'email_on_stderr')
    }
    return attributes


def watch(args):
    """
    Main entrypoint of the script.

    Calls the given command in args,
         while sending relevant information to the server.
    """
    if not args.script_args:
        raise ValueError("monitor.py was not given a command to run")
    parsed_config = read_config(args.config)

    # Command line arguments take precedence over the config file
    domain = args.domain or parsed_config.get('Server', 'domain')
    app_url = args.appurl or parsed_config.get('Server', 'app_url')

    # If args.time is False, it should still override
    timestamp = args.time if args.time is not None \
        else parsed_config.getboolean('Logging', 'timestamp')

    server = '%s/%s' % (domain, app_url)
    emails = get_emails(args, parsed_config)
    email_conditions = get_conditions(parsed_config)

    rec_id = notify_of_start(args, server, emails, email_conditions)
    payload = run_process(command=args.script_args,
                          timestamp=timestamp)
    # Add to returned payload and send to server
    payload['rec_id'] = rec_id
    job_name = '_'.join(args.script_args)
    # If there is any output, add log names as well
    if payload['out_log'] or payload['err_log']:
        payload['plain_log_name'] = '%s_%d.log' % (job_name, rec_id)
        payload['html_log_name'] = "%s_%d.html" % (job_name, rec_id)

    notify_of_end(server, payload)


def main():
    """
    Defines command line arguments, parsing them for watch.
    Placing this in its own function makes testing easier
    """
    description = "Wrapper that monitors scripts"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('script_args',
                        nargs=argparse.REMAINDER,
                        help='the command to run')
    parser.add_argument('--name',
                        help='a name for the command.'
                             ' The default is the command itself.')
    parser.add_argument('--config',
                        help='use CONFIG as the config file.'
                             ' The default is ~/.cronmonrc')
    parser.add_argument('--domain',
                        help='connect to DOMAIN.'
                             ' The default comes from the config file.')
    parser.add_argument('--appurl',
                        help='url path to the installed app.'
                             ' The default comes from the config file.')
    parser.add_argument('-t', '--time',
                        action='store_true',
                        help='prepends a timestamp to every line of output.')
    parser.add_argument('--emails',
                        help='A comma separated string of email addresses. '
                             'These emails are used when figuring out who '
                             'to send emails to. The emails specified '
                             'are for only this run.')
    watch(parser.parse_args(sys.argv[1:]))

if __name__ == '__main__':
    main()
