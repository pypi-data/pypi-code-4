
import stream
import whiffenv

class IdComponent(stream.StreamComponent):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "IdComponent"+repr((self.name, self.file_path))
    def dump(self):
        if self.name is None:
            return "{{id/}}"
        return "{{id %s/}}" % (repr(self.name),)
    def bound_copy(self, in_stream, arguments, root_application, responding_path, path_remainder):
        return self
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment:
            env = update_environment(env)
        status = "200 OK"
        header_list = [ ("Content-Type", "text/plain") ] # XXXX ???
        name = self.name
        full_prefix = env.get(whiffenv.FULL_CGI_PREFIX)
        if full_prefix is None:
            if name is None:
                raise ValueError, "no default {{id/}} known at this location "+repr(self)
            payload = name
        else:
            payload = full_prefix
            if name is not None:
                payload = full_prefix + name
        start_response(status, header_list)
        return [payload]


