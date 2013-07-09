
import stream

class TextComponent(stream.StreamComponent):
    def __init__(self, text):
        self.text = text
    def __repr__(self):
        return "TextComponent"+repr((self.file_path, self.text.strip()[:20]+"..."))
    def dump(self):
        return self.text
    def white(self):
        return self.text.strip()==""
    def lstrip(self):
        return TextComponent(self.text.lstrip())
    def rstrip(self):
        return TextComponent(self.text.rstrip())
    def bound_copy(self, in_stream, arguments, root_application, responding_path, path_remainder):
        return self
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        status = "200 OK"
        header_list = [ ("Content-Type", "text/plain") ] # XXXX ???
        theArg = self.text
        payload = stream.mystr(theArg)
        start_response(status, header_list)
        return [payload]

def whiteComponent(component):
    if isinstance(component, TextComponent):
        return component.white()
    return False

def rstrip(component):
    if isinstance(component, TextComponent):
        return component.rstrip()
    return component

def lstrip(component):
    if isinstance(component, TextComponent):
        return component.lstrip()
    return component
