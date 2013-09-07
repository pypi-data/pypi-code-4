#!/usr/bin/env python
import pdb
import irc_message_processor as imp 
import time



imp.init( { "username": "fenton", "monitor_time": 5 } )
start_time = time.time()

incoming_message = { "from_who": "fenton",
                     "channel" : "lisp",
                     "message" : "john clean up your mess!",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
# pdb.set_trace()
imp.printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

imp.pring_sep(2)

incoming_message = { "from_who": "john",
                     "channel" : "lisp",
                     "message" : "this is barrys mess!",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
imp.printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

imp.pring_sep(4)

incoming_message = { "from_who": "barry",
                     "channel" : "lisp",
                     "message" : "Let me look",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
imp.printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

imp.pring_sep(2)

incoming_message = { "from_who": "barry",
                     "channel" : "lisp",
                     "message" : "Fenton this is really your mess!",
                     "to_me"   : True }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
imp.printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

imp.pring_sep(2)

incoming_message = { "from_who": "fenton",
                     "channel" : "lisp",
                     "message" : "Ok I'll clean it up",
                     "to_me"   : False }
response_actions = imp.generate_actions_from_irc_message(incoming_message)
imp.printall(incoming_message, response_actions)
imp.perform_actions(response_actions)

