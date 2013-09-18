from django.http import HttpResponse
from django.shortcuts import redirect


def home(request):
    return HttpResponse()

def go_back(request):
    return redirect('/')
