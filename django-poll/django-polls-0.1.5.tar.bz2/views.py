from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import ListView, DetailView, FormView
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django import forms
from django.conf import settings
from django.contrib import messages

from polls.models import Choice, Poll, UserChoice, AnonymousUserChoice
from polls.forms import PollForm, PollVoteForm
from polls.methods import get_poll_form, get_poll_vote_form


class PollListView(ListView):
    template_name = 'polls/index.html'

    def get_queryset(self):
        if self.request.user.is_authenticated():
            return Poll.objects.filter(user=self.request.user)
        else:
            return []


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
        poll = Poll.objects.get(pk=self.pk)

        self.form = get_poll_vote_form(poll)

        return super(PollVoteView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ANONYMOUS_VOTING = getattr(
            settings,
            'POLL_ANONYMOUS_VOTING_ENABLED',
            False)
        
        ANONYMOUS_SESSION_AGE = getattr(
            settings,
            'POLL_ANONYMOUS_SESSION_AGE',
            0)
        
        message = None
        
        self.pk = kwargs.get('pk')
        self.form = PollVoteForm(request.POST)
        user = request.user
        poll = Poll.objects.get(pk=self.pk)
        session_key = 'has_voted_on_poll_%s' % poll.pk
        
        if not user.is_authenticated() and not ANONYMOUS_VOTING:
            return (
                HttpResponseRedirect(
                    '%s?%s' %
                    (settings.LOGIN_URL, request.path))
            )

        if (user.is_authenticated() and poll.has_voted(user)) or (not user.is_authenticated() and ANONYMOUS_VOTING and request.session.get(session_key, False)):
            message = getattr(
                settings,
                'POLL_MESSAGE_VOTE_ERROR_ALREADY_VOTED',
                'You have already voted in this poll!')
                
            messages.add_message(
                request,
                messages.WARNING,
                message)
                
            return HttpResponseRedirect(request.path)

        if len(request.POST.getlist('choice')) > 0:
            flag_for_session_save = False
            
            for choice in request.POST.getlist('choice'):
                choice = Choice.objects.get(pk=choice)

                if user.is_authenticated():
                    UserChoice(
                        poll=poll,
                        choice=choice,
                        user=self.request.user).save()
                else:
                    AnonymousUserChoice(
                        poll=poll,
                        choice=choice).save()
                    
                    flag_for_session_save = True
                    
                choice.votes += 1
                choice.save()
            
            if flag_for_session_save:
                request.session[session_key] = True
                request.session.set_expiry(ANONYMOUS_SESSION_AGE)
            
            message = getattr(
                settings,
                'POLL_MESSAGE_VOTE',
                'Voted!')
                
            messages.add_message(request, messages.SUCCESS, message)
    
            return (
                HttpResponseRedirect(
                    reverse('poll_results',
                            kwargs={'pk': self.pk}))
            )
        else:
            message = getattr(
                settings,
                'POLL_MESSAGE_VOTE_ERROR_CHOICE_SELECTION',
                'Select a choice!')
                
            messages.add_message(request, messages.WARNING, message)
            return HttpResponseRedirect(request.path)

    def get_context_data(self, *args, **kwargs):
        context = super(PollVoteView, self).get_context_data(*args, **kwargs)

        pk = self.pk

        instance = Poll.objects.get(pk=pk)

        context['pk'] = pk
        context['form'] = self.form
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
                return (
                    HttpResponseRedirect(
                        '%s?%s' %
                        (settings.LOGIN_URL, request.path))
                )
        else:
            instance = None

        form, formset = get_poll_form(instance, request)

        context = dict(form=form, formset=formset)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        
        message = None
            
        if pk:
            instance = Poll.objects.get(pk=pk)
            if request.user != instance.user:
                return (
                    HttpResponseRedirect(
                        '%s?%s' %
                        (settings.LOGIN_URL, request.path))
                )
                
            message = getattr(
                settings,
                'POLL_MESSAGE_UPDATE',
                'Poll was updated!')
        else:
            instance = None
            message = getattr(
                settings,
                'POLL_MESSAGE_ADD',
                'Poll was added!')

        data = request.POST

        form, formset = get_poll_form(instance, request)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            
            messages.add_message(request, messages.SUCCESS, message)
            
            return (
                HttpResponseRedirect(
                    reverse('poll_vote', kwargs={'pk': form.instance.pk}))
            )
        else:
            context = dict(form=form, formset=formset)

        return render(request, self.template_name, context)
