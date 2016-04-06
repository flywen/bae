from django.shortcuts import render
from django.template.context_processors import request
from django.http.response import HttpResponse

# Create your views here.

def test(request):
    return HttpResponse('it is a test for bae')
    
