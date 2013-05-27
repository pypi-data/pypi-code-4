import xmpp


class Send():

    def __init__(self, to, msg, config_dict):
        client = xmpp.Client(config_dict['host'])
        client.connect(server=(config_dict['server'], config_dict['port']))
        client.auth(config_dict['username'],
                    config_dict['password'],
                    config_dict['name'])
        client.sendInitPresence()
        message = xmpp.Message(to, msg)
        message.setAttr('type', 'chat')
        client.send(message)
