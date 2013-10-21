from django.forms import Widget
from django.template.loader import render_to_string


class PMLChoiceBase(object):
    def render(self, name, value, attrs=None):
        context = {}
        context['attrs'] = self.attrs
        context['name'] = name
        context['value'] = value
        context['widget'] = self
        context['choices'] = self.choices
        return render_to_string(self.template, context)


class PMLCheckBoxWidget(PMLChoiceBase, Widget):
    template = "pml/widgets/choice.xml"
    
    def render(self, name, value, attrs=None):
        self.attrs.update({"type": "checkbox"})
        return super(PMLCheckBoxWidget, self).render(name, value, attrs)


class PMLRadioWidget(PMLChoiceBase, Widget):
    template = "pml/widgets/choice.xml"
    
    def render(self, name, value, attrs=None):
        self.attrs.update({"type": "radio"})
        return super(PMLRadioWidget, self).render(name, value, attrs)


class PMLSelectWidget(PMLChoiceBase, Widget):
    template = "pml/widgets/select.xml"
    

class PMLTextWidget(Widget):
    def render(self, name, value, attrs=None):
        context = {}
        context['attrs'] = self.attrs
        context['name'] = name
        context['value'] = value
        context['widget'] = self
        return render_to_string("pml/widgets/text.xml", context)


class PMLHiddenWidget(Widget):
    def render(self, name, value, attrs=None):
        self.attrs.update({"type": "hidden"})
        context = {}
        context['attrs'] = self.attrs
        context['name'] = name
        context['value'] = value
        context['widget'] = self
        return render_to_string("pml/widgets/hidden.xml", context)
