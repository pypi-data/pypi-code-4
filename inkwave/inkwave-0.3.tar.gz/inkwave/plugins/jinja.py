try:
    import jinja2
except ImportError:
    raise

import os
from inkwave.core import (
    env,
    TemplateEngine,
)


class JinjaTemplateEngine(TemplateEngine):
    def __init__(self):
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.join(env.root, 'templates'))
        )
        for k, v in self.helpers.items():
            self.jinja_env.globals[k] = v

    def render(self, name, data):
        t = self.jinja_env.get_template(name)
        return t.render(**data)
