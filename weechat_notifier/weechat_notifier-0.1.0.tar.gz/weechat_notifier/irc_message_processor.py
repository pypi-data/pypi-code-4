import time
import pdb
from gi.repository import Notify
from subprocess import call

monitored_channels = {} # "channel_name": time_i_last_chatted
def generate_actions_from_irc_message(args):
    global monitored_channels

    from_who = args["from_who"]
    channel = args["channel"]
    message = args["message"]
    to_me = args["to_me"]

    actions_todo = []
    from_me = i_wrote_message(from_who)

    if to_me:
        alert_title, alrt_msg = construct_alert(from_who, channel, message)
        actions_todo.append({"action": display_alert, 
                             "arguments": {"alert_title": alert_title, 
                                           "alert_message": alrt_msg,
                                           "urgency": "high"}} )
        actions_todo.append({"action": play_sound,
                             "arguments": {"sound_file": "irc-message"}})

    remove_expired_channels(monitored_channels)

    if from_me:
        monitored_channels[channel] = time.time()

    monitoring_channel = monitored_channel( channel, monitored_channels )
    if not to_me and not from_me and monitoring_channel:
        elapsed_time = get_elapsed_time_on_channel(channel, monitored_channels)
        alert_title, alrt_msg = construct_alert(from_who, channel, message, elapsed_time)
        actions_todo.append({"action": display_alert,
                             "arguments": {"alert_title": alert_title, 
                                           "alert_message": alrt_msg,
                                           "urgency": "low"}} )
    return actions_todo

def construct_alert(frm, channel, msg, elapsed=None):
    alert_title = frm + "@" + channel + ":"
    message = msg
    if elapsed:
        message += " (" + str(round(seconds_listen_channel - elapsed)) + "s left)"
    return alert_title, message

def get_elapsed_time_on_channel(channel, monitored_channels):
    last_chatted = monitored_channels[channel]
    return time.time() - last_chatted

def remove_expired_channels( monitored_channels ):
    expired_channels = []
    for mon_channel, last_chatted in monitored_channels.items():
        elapsed_time_since_i_chatted = time.time() - last_chatted
        if elapsed_time_since_i_chatted > seconds_listen_channel:
            expired_channels.append( mon_channel )
    for channel in expired_channels:
        monitored_channels.pop(channel, time.time())

def monitored_channel(channel, monitored_channels):
    for mon_channel, last_chatted in monitored_channels.items():
        if channel == mon_channel:
            elapsed_time_since_i_chatted = time.time() - last_chatted
            if elapsed_time_since_i_chatted < seconds_listen_channel:
                return True
    return False

def perform_actions(action_list):
    for action in action_list:
        function = action["action"]
        arguments = action["arguments"]
        function(arguments)
    
def play_sound(args):
    filename = "~/bin/sounds/" + args['sound_file'] + ".ogg"    
    call(["play", "-q", filename])    

def i_wrote_message(who):
    # search for string 'fenton' in who string
    if who == my_username or who[1:] == my_username:
        return True
    else:
        return False

def display_alert(args):
    alert_title = args['alert_title']
    alert_message = args['alert_message']
    urgency = args['urgency']
    msg=Notify.Notification.new (alert_title, alert_message, "dialog-information")
    # msg.show ()
    cmd = construct_notification_command(alert_title, alert_message, urgency)
#    pdb.set_trace()
    call(cmd)    

def construct_notification_command( title, body, urgency ):
    # notify-send -h string:bgcolor:#ff0000 -h string:fgcolor:#ff444 'Hello world!' 'This is an example notification.' --icon=dialog-information
    cmd = ["notify-send"]
    if urgency == "high":
        cmd += ["-h","string:bgcolor:#ff0000","-h","string:fgcolor:#ffffff"]
    if urgency == "low":
        cmd += ["-h","string:bgcolor:#000000","-h","string:fgcolor:#888888"]
    cmd += [title,body]
    return cmd

def init(args): # in_my_username, in_seconds_listen_channel):
    global my_username
    global seconds_listen_channel
    my_username = args["username"]
    seconds_listen_channel = args["monitor_time"]

Notify.init ("Notify Init")

seconds_listen_channel = 5*60 # seconds
my_username = "fenton"


