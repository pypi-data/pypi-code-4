import weechat
import time
import pdb
from gi.repository import Notify
from subprocess import call

monitored_channels = {} # "channel_name": time_i_last_chatted
def generate_actions_from_irc_message(args):
    global monitored_channels

    from_who = args[u"from_who"]
    channel = args[u"channel"]
    message = args[u"message"]
    to_me = args[u"to_me"]

    actions_todo = []
    from_me = i_wrote_message(from_who)

    if to_me:
        alert_title, alrt_msg = construct_alert(from_who, channel, message)
        actions_todo.append({u"action": display_alert, 
                             u"arguments": {u"alert_title": alert_title, 
                                           u"alert_message": alrt_msg,
                                           u"urgency": u"high"}} )
        actions_todo.append({u"action": play_sound,
                             u"arguments": {u"sound_file": u"irc-message"}})

    remove_expired_channels(monitored_channels)

    if from_me:
        monitored_channels[channel] = time.time()

    monitoring_channel = monitored_channel( channel, monitored_channels )
    if not to_me and not from_me and monitoring_channel:
        elapsed_time = get_elapsed_time_on_channel(channel, monitored_channels)
        alert_title, alrt_msg = construct_alert(from_who, channel, message, elapsed_time)
        actions_todo.append({u"action": display_alert,
                             u"arguments": {u"alert_title": alert_title, 
                                           u"alert_message": alrt_msg,
                                           u"urgency": u"low"}} )
    return actions_todo

def construct_alert(frm, channel, msg, elapsed=None):
    alert_title = frm + u"@" + channel + u":"
    message = msg
    if elapsed:
        message += u" (" + unicode(round(seconds_listen_channel - elapsed)) + u"s left)"
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
        function = action[u"action"]
        arguments = action[u"arguments"]
        function(arguments)
    
def play_sound(args):
    filename = u"~/bin/sounds/" + args[u'sound_file'] + u".ogg"    
    call([u"play", u"-q", filename])    

def i_wrote_message(who):
    # search for string 'fenton' in who string
    if who == my_username or who[1:] == my_username:
        return True
    else:
        return False

def display_alert(args):
    alert_title = args[u'alert_title']
    alert_message = args[u'alert_message']
    urgency = args[u'urgency']
    msg=Notify.Notification.new (alert_title, alert_message, u"dialog-information")
    # msg.show ()
    cmd = construct_notification_command(alert_title, alert_message, urgency)
#    pdb.set_trace()
    call(cmd)    

def construct_notification_command( title, body, urgency ):
    # notify-send -h string:bgcolor:#ff0000 -h string:fgcolor:#ff444 'Hello world!' 'This is an example notification.' --icon=dialog-information
    cmd = [u"notify-send"]
    if urgency == u"high":
        cmd += [u"-h",u"string:bgcolor:#ff0000",u"-h",u"string:fgcolor:#ffffff"]
    if urgency == u"low":
        cmd += [u"-h",u"string:bgcolor:#000000",u"-h",u"string:fgcolor:#888888"]
    cmd += [title,body]
    return cmd

def init(args): # in_my_username, in_seconds_listen_channel):
    global my_username
    global seconds_listen_channel
    my_username = args[u"username"]
    seconds_listen_channel = args[u"monitor_time"]

Notify.init (u"Notify Init")

seconds_listen_channel = 5*60 # seconds
my_username = u"fenton"


init( {u"username":u"fenton", u"monitor_time": 5*60} )

def my_print_cb(data, buffer, date, tags, displayed, highlight, prefix, message):
    who = prefix.encode(u'ascii',u'ignore')[0:]
    channel = weechat.buffer_get_string(buffer, u"name").split(u'.')[1][1:]
    message = message.split(u':')
    if len(message) > 1:
        message = message[1]
    message_is_to_me = is_message_for_me(highlight)
    incoming_message = { u"from_who": who,
                         u"channel" : channel,
                         u"message" : message,
                         u"to_me"   : message_is_to_me }
    actions = generate_actions_from_irc_message(incoming_message)
    perform_actions(actions)
    return weechat.WEECHAT_RC_OK

def is_message_for_me(highlight):
    if highlight == u"1":
        display_alert(u"message IS for me")
        return True
    else:
        display_alert(u"message is NOT for me")
        return False

weechat.register(u"Chat_Notifier", u"FlashCode", u"1.0", u"GPL3", u"Test script", u"", u"")
weechat.prnt(u"", u"Hello, from python script!")
hook = weechat.hook_print(u"", u"", u"", 1, u"my_print_cb", u"")
