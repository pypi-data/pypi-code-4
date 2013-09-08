import time, pdb
from subprocess import call

seconds_listen_channel = 5*60 # seconds
my_username = u"fenton"

monitored_channels = {} # "channel_name": time_i_last_chatted

def generate_actions_from_irc_message(args):
    # Generate a list of action based on input args.  The design of this
    # code is to run the generate_actions_from_irc_message method with a
    # give set of inputs: from_who, channel, message, and to_me?.  Based on
    # these inputs some actions will be generated...like send me a
    # notification if the message is on a channel I'm monitoring, or play a
    # sound if a message is directly to me.
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


# This method dispatches to the required action.  Each action takes a
# hash/dict as an argument, this contains the actual arguments.
def perform_actions(action_list, printer):
    for action in action_list:
        function = action[u"action"]
        arguments = action[u"arguments"]
        function(arguments, printer)

#######################
# THE ACTIONS

def display_alert(args,printer):
    alert_title = args[u'alert_title']
    alert_message = args[u'alert_message']
    urgency = args[u'urgency']
    # msg=Notify.Notification.new (alert_title, alert_message, u"dialog-information")
    # msg.show ()
    cmd = construct_notification_command(alert_title, alert_message, urgency)
    #    pdb.set_trace()
    printer ("The Command:", str(cmd))
    call(cmd)    
    
def play_sound(args,printer):
    a = 1
    filename = u"~/bin/sounds/" + args[u'sound_file'] + u".ogg"    
    cmd = [u"play", u"-q", filename]
    printer ("The Command:", str(cmd))
    #call(cmd)


##########################
## HELPERS

def monitored_channel(channel, monitored_channels):
    for mon_channel, last_chatted in monitored_channels.items():
        if channel == mon_channel:
            elapsed_time_since_i_chatted = time.time() - last_chatted
            if elapsed_time_since_i_chatted < seconds_listen_channel:
                return True
    return False


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

def i_wrote_message(who):
    # search for string 'fenton' in who string
    if who == my_username or who[1:] == my_username:
        return True
    else:
        return False

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

# Notify.init (u"Notify Init")


def display_actions(actions):
    print( "RESPONSE:" )
#    pdb.set_trace()
    for action in actions:
        print( "  ==> " + action["action"].__name__ )
        action_args = action["arguments"]
        for param, value in action_args.items():
            print ( "\t+ " + param + ": " + value )

def display_incoming_message(im, start_time):
    elapsed = time.time() - start_time
    print( "INCOMING MESSAGE: +" + str(round(elapsed)) + "(s)" )
    print( "\t[from]: "  + im["from_who"] + "   [to me]: " + str(im["to_me"]) + "   [channel]: " + im["channel"])
    print( "\t[message]: " + im["message"])

def display_state():
    print("MONITORING CHANNELS:")
    for channel, monitored_since in monitored_channels.items():
        elapsed = time.time() - monitored_since
        print ( "\t" + channel + ", for: " + str(round(elapsed)) + " of " + str(seconds_listen_channel) + "(s)" )

def printall(incoming_message, response_actions, start_time):
    display_incoming_message(incoming_message, start_time)
    display_actions(response_actions)
    display_state()

def print_sep(dur):
    print("-------------------------------")
    time.sleep(dur)
