from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, redirect, render, get_object_or_404
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.mail import send_mail
from .models import Contact



def contactForm(request):
	if request.method == 'POST':
		c = {}
		c.update(csrf(request))
		form = Contact(request.POST)
		if form.is_valid():
			message = form.cleaned_data['message']
			fromEmail = form.cleaned_data['email']
			send_mail('Email from Truck Form', message, fromEmail,
			    ['bryanlrobinson@gmail.com'], fail_silently=False)
			return HttpResponseRedirect('/thanks/')
			
	else:
		c = {}
		c.update(csrf(request))
		form = Contact()
	return render (request, 'contact.html', {
		'form': form,
		'c': c,
	})
