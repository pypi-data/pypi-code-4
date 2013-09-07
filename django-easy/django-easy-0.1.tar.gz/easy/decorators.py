from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
import json

def context_template_response(func):
  def wrapper(*args):
    response = func(*args)
    if isinstance(response, tuple):
      template = response[0] 
      variables = {}
      if len(response) > 1:
        variables = response[1]
    elif isinstance(response, str):
      template = response
      variables = {}
    else:
      raise TypeError("expected either tuple or string")

    if not isinstance(template, str):
      raise TypeError("expected string")

    if not isinstance(variables, dict):
      raise TypeError("expected dictionary")

    return render_to_response(
      template,
      variables,
      context_instance=RequestContext(args[0])
    )

  return wrapper

def json_response(func):
  def wrapper(*args):
    response = func(*args)

    if not isinstance(response, (dict, list)):
      raise TypeError("expected either dictionary or list")

    return HttpResponse(
      json.dumps(response, indent=2),
      content_type='application/json',
    )
  
  return wrapper

def string_response(func):
  def wrapper(*args):
    response = func(*args)
    return HttpResponse(str(response))

  return wrapper
