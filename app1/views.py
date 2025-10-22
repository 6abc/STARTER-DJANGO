from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def app1(request):
    return render(request, 'app1/app.html')