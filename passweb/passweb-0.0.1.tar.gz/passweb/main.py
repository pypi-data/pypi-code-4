#!/usr/bin/env python

from yota import Form
from yota.nodes import EntryNode, PasswordNode, SubmitNode, TextareaNode

from jinja2 import Environment, FileSystemLoader

from circuits.web import Controller, Logger, Server, Static


env = Environment(loader=FileSystemLoader("templates"))


def render_template(name, **ctx):
    template = env.get_template(name)
    return template.render(**ctx)


class LoginForm(Form):

    title = "Login"

    username = EntryNode()
    password = PasswordNode()
    login = SubmitNode()

    def success_header_generate(self):
        self.start.add_error({"message": "Successful Login!"})


class SignupForm(Form):

    title = "Signup"

    firstname = EntryNode(title="First Name")
    lastname = EntryNode(title="Last Name")
    email = EntryNode()

    username = EntryNode()
    password = PasswordNode()
    confirm = PasswordNode()

    signup = SubmitNode()

    def success_header_generate(self):
        self.start.add_error({"message": "Successful Login!"})


class ContactForm(Form):

    title = "Contact Us"

    firstname = EntryNode(title="First Name")
    lastname = EntryNode(title="Last Name")
    email = EntryNode()

    message = TextareaNode()

    send = SubmitNode()

    def success_header_generate(self):
        self.start.add_error({"message": "Thank you for contacting us!"})


class Root(Controller):

    def index(self):
        login = LoginForm()
        signup = SignupForm()

        return render_template(
            "index.html",
            login=login.render(),
            signup=signup.render()
        )

    def login(self, *args, **kwargs):
        form = LoginForm()

        if self.request.method == "POST":
            success, out = form.validate_render(kwargs)
        else:
            out = form.render()

        return render_template("forms/basic.html", form=out)

    def signup(self, *args, **kwargs):
        form = SignupForm()

        if self.request.method == "POST":
            success, out = form.validate_render(kwargs)
        else:
            out = form.render()

        return render_template("forms/basic.html", form=out)

    def contact(self, *args, **kwargs):
        form = ContactForm()

        if self.request.method == "POST":
            success, out = form.validate_render(kwargs)
        else:
            out = form.render()

        return render_template("forms/basic.html", form=out)

    def features(self):
        return render_template("pages/features.html")

    def pricing(self):
        return render_template("pages/pricing.html")

    def blog(self):
        return render_template("pages/blog.html")


def main():
    app = Server(("0.0.0.0", 9000))

    Static().register(app)
    Logger().register(app)
    Root().register(app)

    app.run()


if __name__ == "__main__":
    main()
