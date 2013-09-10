__title__ = 'django-lime.__init__'
__version__ = '0.3'
__build__ = 0x000003
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('send_email',)

from six import string_types

from django.core.mail import EmailMultiAlternatives
from django.template import loader, Context

from lime.helpers import site

def _render_content(context, template):
    """
    Renders context of the e-mail. If no template specified, simply returns the context back, otherwise loads context
    into the specified template.
    """
    if template:
        t = loader.get_template(template)
        return t.render(Context(context))
    return context

def send_email(subject, from_email, to, context, plain_template, html_template=None, bcc=None):
    """
    Sends an e-mail. Additionally might send an html version as an attachment.

    :param str subject: E-mail subject. Example value "Subject".
    :param str from_email: E-mail from. Example value "john@doe.com".
    :param str|list to: E-mail to. Example values: "johh@doe.com", ["johh@doe.com", "someone@example.com"].
    :param dict context: Content of the e-mail. Dictionary with values available in template context.
    :param str plain_template: Plain e-mail template. Path to plain template.
    :param str html_template: HTML e-mail template. Path to HTML template.
    :param str|list bcc: E-mail bcc. Example values: "johh@doe.com", ["johh@doe.com", "someone@example.com"].

    :example:
    >>> from lime import send_email
    >>>
    >>> send_email(
    >>>         subject = _('Sample subject'),
    >>>         from_email = form.cleaned_data['from_email'],
    >>>         to = form.cleaned_data['to_email'],
    >>>         context = {
    >>>             'url': next,
    >>>             'full_name': form.cleaned_data['to_name'],
    >>>             'from_name': form.cleaned_data['from_name'],
    >>>             'message': form.cleaned_data['message']
    >>>         },
    >>>         plain_template = 'tellafriend/mail/tellafriend.txt',
    >>>         html_template = 'tellafriend/mail/tellafriend.html'
    >>>     )
    """
    # Add the defaults to the context
    context.update({
        'site_name': site.name,
        'domain': site.domain,
        'site_team': site.team,
        'site_logo': site.logo
    })

    if isinstance(to, string_types):
        to_list = [to]
    else:
        to_list = to

    bcc_list = []
    if bcc:
        if isinstance(bcc, string_types):
            bcc_list = [bcc]
        else:
            bcc_list = bcc

    text_content = _render_content(context, plain_template)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_list, bcc_list)

    if html_template:
        html_content = _render_content(context, html_template)
        msg.attach_alternative(html_content, "text/html")

    msg.send()
