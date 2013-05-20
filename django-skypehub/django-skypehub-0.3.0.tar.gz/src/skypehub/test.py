class MockChat(object):
    def __init__(self, name, topic=None):
        self.Name = name
        self.Topic = topic

    def SendMessage(self, message):
        pass


class MockSkype(object):
    def __init__(self, **options):
        self.options = options
        self.chats = []

    def get_chats(self):
        return self.chats

    Chats = property(get_chats)

    def CreateChatWith(self, name):
        chat = MockChat('#%s/$test;test' % name)
        self.add_chat(chat)
        return chat

    def add_chat(self, chat):
        self.chats.append(chat)