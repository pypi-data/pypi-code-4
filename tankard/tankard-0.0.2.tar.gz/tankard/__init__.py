import inspect
import re

from werkzeug import cached_property

from flask import get_flashed_messages
from flask import render_template
from flask import redirect
from flask import request
from flask import url_for
from flask import jsonify
from flask import Flask
from flask import flash

import wtforms


class Tankard(Flask):

    def get(self, *args, **kwargs):
        kwargs["methods"] = ["GET", "HEAD"]
        return self.route(*args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs["methods"] = ["PUT"]
        return self.route(*args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs["methods"] = ["POST"]
        return self.route(*args, **kwargs)

    def delete(self, *args, **kwargs):
        kwargs["methods"] = ["DELETE"]
        return self.route(*args, **kwargs)

    def options(self, *args, **kwargs):
        kwargs["methods"] = ["OPTIONS"]
        return self.route(*args, **kwargs)

    def trace(self, *args, **kwargs):
        kwargs["methods"] = ["TRACE"]
        return self.route(*args, **kwargs)

    @property
    def view_file_re(self):
        raise NotImplementedError

    @cached_property
    def _compiled_view_file_re(self):
        return re.compile(self.view_file_re)

    def _find_view_in_stack(self):
        frame = inspect.currentframe()
        while frame is not None:
            tb = inspect.getframeinfo(frame)
            if self._compiled_view_file_re.match(tb.filename):
                return tb.function
            frame = frame.f_back

    def autorender(self, **kwargs):
        view_name = self._find_view_in_stack()
        if not view_name:
            return self.render("view_name_unknown.html", **kwargs)
        template_name = view_name + ".html"
        return self.render(template_name, **kwargs)

    def render_form(self, form_class):
        return self.render(form=form_class(request.form))

    def render(self, *args, **kwargs):
        if len(args) == 0:
            return self.autorender(**kwargs)
        elif len(args) == 1 and args[0].__class__ == wtforms.form.FormMeta:
            return self.render_form(args[0])
        else:
            return render_template(*args, **kwargs)

    def redirect(self, *args, **kwargs):
        return redirect(*args, **kwargs)

    def url_for(self, *args, **kwargs):
        return url_for(*args, **kwargs)

    def jsonify(self, *args, **kwargs):
        return jsonify(*args, **kwargs)

    def re_url_for(self, *args, **kwargs):
        return self.redirect(self.url_for(*args, **kwargs))

    def back(self):
        return self.redirect(request.referrer or self.url_for("home"))

    def get_flashed_messages(self, *args, **kwargs):
        return get_flashed_messages(*args, **kwargs)

    def flash(self, *args, **kwargs):
        return flash(*args, **kwargs)

    def info(self, msg):
        return self.flash(msg, "info")

    def err(self, msg):
        return self.flash(msg, "error")
