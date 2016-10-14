import random

from django.shortcuts import render, render_to_response, RequestContext


# Create your views here.

def calculate(request):
    num1 = random.randint(0, 5)
    num2 = random.randint(0, 5)
    sum_ok = num1 + num2
    sum_cal = request.POST.get('sum_cal')
    print sum_cal
    return render_to_response('calculate.html', locals(), context_instance=RequestContext(request))
