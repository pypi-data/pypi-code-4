#!/usr/bin/env python2
import time, pdb
from subprocess import call

seconds_listen_channel = 5*60 # seconds
my_username = "fenton"
debug = True
monitored_channels = {} # "channel_name": time_i_last_chatted
the_printer = None

def generate_actions_from_irc_message(args,printer):
    # Generate a list of action based on input args.  The design of this
    # code is to run the generate_actions_from_irc_message method with a
    # give set of inputs: from_who, channel, message, and to_me?.  Based on
    # these inputs some actions will be generated...like send me a
    # notification if the message is on a channel I'm monitoring, or play a
    # sound if a message is directly to me.
    global monitored_channels
    global the_printer
    the_printer = printer
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
        if debug:
            printer("Now monitoring channel: " + channel, str(monitored_channels[channel]))

    monitoring_channel = monitored_channel( channel, monitored_channels )
    if not to_me and not from_me and channel == "test":
        printer("Monitoring channel" + channel, str(monitoring_channel))

    if debug:
        printer("", "to_me: " + str(to_me) + ", from_me: " + str(from_me) + ", monitoring_channel: " + str(monitoring_channel))

    if not to_me and not from_me and monitoring_channel:
        elapsed_time = get_elapsed_time_on_channel(channel, monitored_channels)
        alert_title, alrt_msg = construct_alert(from_who, channel, message, elapsed_time)
        actions_todo.append({"action": display_alert,
                             "arguments": {"alert_title": alert_title, 
                                           "alert_message": alrt_msg,
                                           "urgency": "low"}} )
        if debug:
            printer("Monitoring Channel Msg" + channel, "channels: " + str(monitored_channels))
                    
    return actions_todo


# This method dispatches to the required action.  Each action takes a
# hash/dict as an argument, this contains the actual arguments.
def perform_actions(action_list, printer):
    for action in action_list:
        function = action["action"]
        arguments = action["arguments"]
        function(arguments, printer)

#######################
# THE ACTIONS

def display_alert(args,printer):
    alert_title = args['alert_title']
    alert_message = args['alert_message']
    urgency = args['urgency']
    if debug: 
        printer ("title/message/urgency", str(alert_title) + "/" + str(alert_message) + "/" + str(urgency))
    cmd = construct_notification_command(alert_title, alert_message, urgency)
    # pdb.set_trace()
    if debug: 
        printer ("The Command:", str(cmd))
    call(cmd)    
    
def play_sound(args,printer):
    a = 1
    filename = "~/bin/sounds/" + args['sound_file'] + ".ogg"    
    cmd = ["play", "-q", filename]
    if debug: 
        printer ("The Command:", str(cmd))
    call(cmd)


#########################
## TESTS

def _tests():
    test_trim_leading_dashes()
    test_begins_with_dash ()

def test_trim_leading_dashes():
    strng = "-abc"
    result = trim_leading_dashes(strng)
    assert result == "abc"
    strng = "--abc"
    result = trim_leading_dashes(strng)
    assert result == "abc"
    strng = "abc"
    result = trim_leading_dashes(strng)
    assert result == "abc"

def test_begins_with_dash ():
    strng = "-abc"
    result = begins_with_dash(strng)
    assert result == True
    strng = "--abc"
    result = begins_with_dash(strng)
    assert result == True
    strng = "abc"
    result = begins_with_dash(strng)
    assert result == False
    
##########################
## HELPERS

def trim_leading_dashes(strng):
    # pdb.set_trace()
    while begins_with_dash(strng):
        strng = strng[1:]
    return strng

def begins_with_dash(strng):
    if strng[0] == '-':
        return True
    return False

def monitored_channel(channel, monitored_channels):
    for mon_channel, last_chatted in monitored_channels.items():
        if channel == mon_channel:
            elapsed_time_since_i_chatted = time.time() - last_chatted
            if elapsed_time_since_i_chatted < seconds_listen_channel:
                return True
    return False


def construct_alert(frm, channel, msg, elapsed=None):
    global the_printer
    alert_title = frm + "@" + channel + ":"
    message = msg
    if elapsed:
        message += " (" + str(round(seconds_listen_channel - elapsed)) + "s left)"
    if debug:
        the_printer("",message)
    message = trim_leading_dashes(message)
    alert = trim_leading_dashes(alert_title)
    return alert, message

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
    cmd = ["notify-send"]
    if urgency == "high":
        cmd += ["-h","string:bgcolor:#ff0000","-h","string:fgcolor:#ffffff"]
    if urgency == "low":
        cmd += ["-h","string:bgcolor:#000000","-h","string:fgcolor:#888888"]
    cmd.append(title)
    cmd.append(body)
    return cmd

def init(args): # in_my_username, in_seconds_listen_channel):
    global my_username
    global seconds_listen_channel
    my_username = args["username"]
    seconds_listen_channel = args["monitor_time"]

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

if __name__ == '__main__':
    _tests()
