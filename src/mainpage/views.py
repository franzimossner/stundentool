from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def start_page(request):
    return render(request, 'mainpage/start_page.html',)
