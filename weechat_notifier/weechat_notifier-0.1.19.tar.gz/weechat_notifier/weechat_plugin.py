import weechat
# May need to do the following to get the library into the 2.7 python as weechat uses python 2.x
# sudo pip install --install-option="--install-purelib=/usr/lib/python2.7/site-packages" --ignore-installed weechat_notifier
from weechat_notifier import irc_message_processor as imp 

seconds_listen_channel = 5*60 # seconds
my_username = u"fenton"

imp.init( {u"username":u"fenton", u"monitor_time": 5*60} )

def my_print_cb(data, buffer, date, tags, displayed, highlight, prefix, message):
    who = prefix.encode(u'ascii',u'ignore')[0:]
    chan = weechat.buffer_get_string(buffer, u"name").split(u'.')
    if len (chan) > 1:
        chan = chan[1]
    if len (chan) > 1:
        chan = chan[1:]
    message = message.split(u':')
    if len(message) > 1:
        message = message[1]
    message_is_to_me = is_message_for_me(highlight)
    incoming_message = { u"from_who": who,
                         u"channel" : chan,
                         u"message" : message,
                         u"to_me"   : message_is_to_me }
    actions = imp.generate_actions_from_irc_message(incoming_message)
    imp.perform_actions(actions, weechat.prnt)
    return weechat.WEECHAT_RC_OK

def is_message_for_me(highlight):
    if highlight == u"1":
        return True
    else:
        return False

weechat.register(u"Chat_Notifier", u"FlashCode", u"1.0", u"GPL3", u"Test script", u"", u"")
weechat.prnt(u"", u"Hello, from python script!")
# hook = weechat.hook_print(u"", u"", u"", 1, u"my_print_cb", u"")
