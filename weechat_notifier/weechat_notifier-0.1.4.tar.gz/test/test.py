#!/usr/bin/env python
import pdb
import irc_message_processor as imp 
import time

def display_actions(actions):
    print( "RESPONSE:" )
#    pdb.set_trace()
    for action in actions:
        print( "  ==> " + action["action"].__name__ )
        action_args = action["arguments"]
        for param, value in action_args.items():
            print ( "\t+ " + param + ": " + value )

def display_incoming_message(im):
    global start_time
    elapsed = time.time() - start_time
    print( "INCOMING MESSAGE: +" + str(round(elapsed)) + "(s)" )
    print( "\t[from]: "  + im["from_who"] + "   [to me]: " + str(im["to_me"]) + "   [channel]: " + im["channel"])
    print( "\t[message]: " + im["message"])

def display_state():
    print("MONITORING CHANNELS:")
    for channel, monitored_since in imp.monitored_channels.items():
        elapsed = time.time() - monitored_since
        print ( "\t" + channel + ", for: " + str(round(elapsed)) + " of " + str(imp.seconds_listen_channel) + "(s)" )

def printall(incoming_message, response_actions):
    display_incoming_message(incoming_message)
    display_actions(response_actions)
    display_state()

def print_sep(dur):
    print("-------------------------------")
    time.sleep(dur)

imp.init( { "username": "fenton", "monitor_time": 5 } )
start_time = time.time()

incoming_message = { "from_who": "fenton",
                     "channel" : "lisp",
                     "message" : "john clean up your mess!",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
# pdb.set_trace()
printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

print_sep(2)

incoming_message = { "from_who": "john",
                     "channel" : "lisp",
                     "message" : "this is barrys mess!",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

print_sep(4)

incoming_message = { "from_who": "barry",
                     "channel" : "lisp",
                     "message" : "Let me look",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

print_sep(2)

incoming_message = { "from_who": "barry",
                     "channel" : "lisp",
                     "message" : "Fenton this is really your mess!",
                     "to_me"   : True }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

print_sep(2)

incoming_message = { "from_who": "fenton",
                     "channel" : "lisp",
                     "message" : "Ok I'll clean it up",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

