from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from quiz import models, signals
from django.db import transaction
from django.utils.datastructures import SortedDict

class RadioFieldRenderer(widgets.RadioFieldRenderer):
    def render(self):
        """Outputs a <ol> for this set of radio fields."""
        return mark_safe(u'<ol>\n%s\n</ol>' % u'\n'.join([u'<li>%s</li>'
                % force_unicode(w) for w in self]))

@transaction.commit_on_success
def save_sitting_form(self, student):
    sitting = models.Sitting.objects.create(
        student=student,
        quiz=self.quiz
    )
    for question in self.quiz.question_set.all():
        models.Response.objects.create(
            sitting=sitting,
            question=question,
            choice=self.cleaned_data['q_%d' % question.id]
        )
    signals.quiz_complete.send_robust(sender=sitting)
    return sitting

def make_sitting_form(quiz):
    fields = SortedDict(
        ('q_%d' % question.id, forms.ModelChoiceField(
            label=question,
            queryset=models.Answer.objects.filter(question=question),
            widget=widgets.RadioSelect(renderer=RadioFieldRenderer),
            required=True,
            empty_label=None,
        ))
        for question in  quiz.question_set.all()
    )
    return type('SittingForm', (forms.BaseForm,), {
        'base_fields': fields,
        'quiz': quiz,
        'save': save_sitting_form
    })
