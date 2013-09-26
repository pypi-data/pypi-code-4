#!/usr/bin/env python
import pdb
import weechat_notifier.irc_message_processor as imp 
import time

start_time = time.time()

def printer(arg):
    print arg

def test_ignore_join_leave():
    fenton_writes_on_lisp()
    imp.print_sep(sleep_seconds = 0)
    incoming_message = { "from_who": "abcdef",
                         "channel" : "lisp",
                         "message" : "john has joined #lisp",
                         "to_me"   : False }
    pdb.set_trace()
    response_actions = imp.generate_actions_from_irc_message(incoming_message,printer)

    imp.printall(incoming_message, response_actions,start_time)
    # imp.perform_actions(response_actions,printer)

def fenton_writes_on_lisp():
    # I write a question on channel #lisp
    imp.init( { "username": "fenton", "monitor_time": 5 } )

    incoming_message = { "from_who": "fenton",
                         "channel" : "lisp",
                         "message" : "john clean up your mess!",
                         "to_me"   : False }
    response_actions = imp.generate_actions_from_irc_message(incoming_message,printer)
    # pdb.set_trace()
    imp.printall(incoming_message, response_actions,start_time)
    imp.perform_actions(response_actions,printer)

def test_system():
    fenton_writes_on_lisp()

    # Wait 2 seconds
    imp.print_sep(sleep_seconds = 2)
    
    incoming_message = { "from_who": "john",
                         "channel" : "lisp",
                         "message" : "this is barrys mess!",
                         "to_me"   : False }
    response_actions = imp.generate_actions_from_irc_message(incoming_message,printer)
    imp.printall(incoming_message, response_actions,start_time)
    imp.perform_actions(response_actions,printer)
    
    imp.print_sep(sleep_seconds = 4)
    
    incoming_message = { "from_who": "barry",
                         "channel" : "lisp",
                         "message" : "Let me look",
                         "to_me"   : False }
    response_actions = imp.generate_actions_from_irc_message(incoming_message,printer)
    imp.printall(incoming_message, response_actions,start_time)
    imp.perform_actions(response_actions,printer)
    
    imp.print_sep(sleep_seconds = 2)
    
    incoming_message = { "from_who": "barry",
                         "channel" : "lisp",
                         "message" : "Fenton this is really your mess!",
                         "to_me"   : True }
    response_actions = imp.generate_actions_from_irc_message(incoming_message,printer)
    imp.printall(incoming_message, response_actions,start_time)
    imp.perform_actions(response_actions,printer)
    
    imp.print_sep(sleep_seconds = 2)
    
    incoming_message = { "from_who": "fenton",
                         "channel" : "lisp",
                         "message" : "Ok I'll clean it up",
                         "to_me"   : False }
    response_actions = imp.generate_actions_from_irc_message(incoming_message,printer)
    imp.printall(incoming_message, response_actions,start_time)
    imp.perform_actions(response_actions,printer)



# test_system()
test_ignore_join_leave()
