import json


class JinjaRenderer:
    """render jinja2 templates"""
    def __init__(self, jinja_env):
        """

        :param jinja_env:
            instance of jinja2.Environment

        """
        self.jinja_env = jinja_env

    def render(self, handler, **context):
        """Renders handler.template and writes the result to its response"""
        if handler.template:
            self.jinja_env.globals['uri_for'] = handler.uri_for
            template = self.jinja_env.get_template(handler.template)
            handler.response.write(template.render(
                    handler=handler,
                    **context))


class JsonRenderer:
    """render json data"""
    @staticmethod
    def render(handler, **context):
        """write response to handler's reponse """
        handler.response.write(json.dumps(context).replace("</", "<\\/"))


class NoOpRenderer:
    """No operation renderer, to be used when handler writes no response"""
    @staticmethod
    def render(handler, **context):
        pass
