from templated_email.backends import vanilla_django
from django.template import Context, Template
from templated_email.backends.database.models import EmailTemplate


class TemplateBackend(vanilla_django.TemplateBackend):
    def _render_email(self, template_name, context,
                      template_dir=None, file_extension=None):
        response = {}
        errors = {}
        render_context = Context(context, autoescape=False)

        template = EmailTemplate.objects.get(name=template_name)
        response['subject'] = Template(template.subject).render(render_context)
        response['plain'] = Template(template.text_message).render(render_context)
        response['html_message'] = Template(template.html_message).render(render_context)

        if response == {}:
            raise vanilla_django.EmailRenderException("Couldn't render email parts. Errors: %s"
                                       % errors)

        return response
