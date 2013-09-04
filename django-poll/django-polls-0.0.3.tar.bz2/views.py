from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, FormView
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django import forms
from django.conf import settings
from django.contrib import messages

from polls.models import Choice, Poll, UserChoice
from polls.forms import PollForm, PollVoteForm

class PollListView(ListView):
    template_name = 'polls/index.html'

    def get_queryset(self):
        return Poll.objects.filter(user=self.request.user).order_by('-created')
        
class ResultsView(DetailView):
    model = Poll
    template_name = 'polls/results.html'
    
class PollVoteView(FormView):
    form_class = PollVoteForm
    template_name = 'polls/vote.html'
    success_url = '/'
    pk = None
    form = None
    
    def get(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk')
        self.form = PollVoteForm()
        user = request.user
        poll = Poll.objects.get(pk=self.pk)
        
        return super(PollVoteView, self).get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.pk = kwargs.get('pk')
        self.form = PollVoteForm(request.POST)
        user = request.user
        poll = Poll.objects.get(pk=self.pk)
        
        if user.is_authenticated():
            if not poll.has_voted(user):
                if len(request.POST.getlist('choice')) > 0:
                    for choice in request.POST.getlist('choice'):
                        choice = Choice.objects.get(pk=choice)
                        UserChoice(poll=poll, choice=choice, user=self.request.user).save()
                        choice.votes += 1
                        choice.save()
                    return HttpResponseRedirect(reverse('poll_results', kwargs={'pk': self.pk}))
                else:
                    messages.add_message(request, messages.WARNING, 'Select a choice.')
                    return HttpResponseRedirect(request.path)
            else:
                messages.add_message(request, messages.WARNING, 'You have already voted in the poll.')
                return HttpResponseRedirect(request.path)
        else:
            return HttpResponseRedirect('%s?%s' % (settings.LOGIN_URL, request.path))

    def get_context_data(self, *args, **kwargs):
        context = super(PollVoteView, self).get_context_data(*args, **kwargs)

        pk = self.pk
        
        instance = Poll.objects.get(pk=pk)
            
        form = self.form
        
        form.construct(instance)
        
        context['pk'] = pk
        context['form'] = form
        context['instance'] = instance
        
        return context
        
class PollView(FormView):
    form_class = PollForm
    template_name = 'polls/poll/poll.html'
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        
        if pk:
            instance = Poll.objects.get(pk=pk)
            if request.user != instance.user:
                return HttpResponseRedirect('%s?%s' % (settings.LOGIN_URL, request.path))
        else:
            instance = None
        
        form = PollForm(instance=instance)
        
        ChoiceFormSet = inlineformset_factory(Poll, Choice)
        
        formset = ChoiceFormSet(instance=instance)
        
        context = dict(form=form, formset=formset)
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        
        if pk:
            instance = Poll.objects.get(pk=pk)
            if request.user != instance.user:
                return HttpResponseRedirect('%s?%s' % (settings.LOGIN_URL, request.path))
        else:
            instance = None
            
        ChoiceFormSet = inlineformset_factory(Poll, Choice)
        
        data = request.POST
        
        form = PollForm(data, instance=instance) if instance else PollForm(data)
        form.instance.user = request.user
        formset = ChoiceFormSet(data, instance=form.instance)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return HttpResponseRedirect(reverse('poll_vote', kwargs={'pk': form.instance.pk}))  
        else:
            context = dict(form=form, formset=formset)
            
        return render(request, self.template_name, context)