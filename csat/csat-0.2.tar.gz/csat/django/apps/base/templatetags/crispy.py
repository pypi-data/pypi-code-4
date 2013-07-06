from coffin import template
from crispy_forms.templatetags import crispy_forms_tags as crispy

from django.forms.formsets import BaseFormSet
from django.template import Context
from jinja2 import nodes, ext, utils


register = template.Library()


class CrispyExtension(ext.Extension):
    tags = {'crispy', }

    def __init__(self, environment):
        super(CrispyExtension, self).__init__(environment)

        # add the defaults to the environment
        environment.extend(
            fragment_cache_prefix='',
            fragment_cache=None
        )

    def parse(self, parser):
        parser.stream.next()  # Skip tag name

        args = [parser.parse_expression()]

        # If there is a comma, the user provided an helper.
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        return nodes.CallBlock(self.call_method('_render', args), [], [], '')

    @utils.contextfunction
    def _render(self, context, form, helper, caller):
        if helper is None:
            helper = getattr(form, 'helper', crispy.FormHelper())

        is_formset = isinstance(form, BaseFormSet)
        node_context = Context(context.get_all())
        node = crispy.BasicNode(form, helper)
        context_dict = node.get_response_dict(helper, node_context, is_formset)

        node_context.update(context_dict)

        if helper and helper.layout:
            if not is_formset:
                form.form_html = helper.render_layout(
                    form, node_context, template_pack=crispy.TEMPLATE_PACK)
            else:
                forloop = crispy.ForLoopSimulator(form)
                for f in form.forms:
                    node_context.update({'forloop': forloop})
                    form.form_html = helper.render_layout(
                        f, node_context, template_pack=crispy.TEMPLATE_PACK)
                    forloop.iterate()

        if is_formset:
            context_dict.update({'formset': form})
        else:
            context_dict.update({'form': form})

        context = Context(context_dict)

        if context['is_formset']:
            template = crispy.whole_uni_formset_template(crispy.TEMPLATE_PACK)
        else:
            template = crispy.whole_uni_form_template(crispy.TEMPLATE_PACK)

        return template.render(context)

register.tag(CrispyExtension)
