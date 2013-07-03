from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.template.loader import select_template
from django.views.generic.list_detail import object_list
from django.views.generic.simple import direct_to_template
from quiz.settings import SITTING_REDIRECT

from quiz import models, forms

def quiz_list(request):
    # Should filter this by units available to student
    return object_list(request,
        queryset=models.Quiz.objects.all(),
    )

def quiz_sit(request, quiz_id):
    quiz = get_object_or_404(models.Quiz, pk=quiz_id)

    quiz_form = forms.make_sitting_form(quiz)

    if request.method == 'POST':
        form = quiz_form(request.POST)
        if form.is_valid():
            sitting = form.save(request.user)
            if SITTING_REDIRECT:
                if callable(SITTING_REDIRECT):
                    url = SITTING_REDIRECT(sitting)
                else:
                    url = SITTING_REDIRECT
            else: 
                url = sitting.get_absolute_url()
            return HttpResponseRedirect(url)
    else:
        form = quiz_form()

    template = select_template([
        'quiz/quiz_%s.html' % quiz.id,
        'quiz/quiz.html',
    ])
    context = RequestContext(request, {
        'form': form,
        'quiz': quiz,
    })

    return HttpResponse(template.render(context))

def sitting_list(request):
    qset = models.Sitting.all()
    if not request.user.is_staff:
        qset = qset.filter(student=request.user)
    return object_list(request,
        queryset=qset
    )

def sitting_details(request, sitting_id):
    sitting = get_object_or_404(models.Sitting, pk=sitting_id)

    # Only allow admins or sitter view
    if not request.user == sitting and not request.user.is_staff:
        return HttpResponseForbidden()

    return direct_to_template(request, 'quiz/sitting_detail.html',
        extra_context = {
            'sitting': sitting,
        }
    )
