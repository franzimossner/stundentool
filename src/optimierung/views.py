from django.shortcuts import render
from .datencheck import datenpruefer
#from ..Skripte import datencheck

# Create your views here.
def optimierung_main(request):
    return render(request, 'optimierung/optimierung_main.html',)

def datencheck(request):
    messages = datenpruefer.machdencheck(datenpruefer)
    if messages == []:    
        messages = ["Ihre Daten haben den Datencheck bestanden. Gehen sie nun weiter zum nächsten Schritt"]

    return render(request, 'optimierung/datencheck.html', {'messages': messages})

def parameters(request):
    return render(request, 'optimierung/parameters.html',)

def optimierung(request):
    return render(request, 'optimierung/optimierung.html',)
