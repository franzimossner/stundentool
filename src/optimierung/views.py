from django.shortcuts import render
from .datencheck import datenpruefer
from .main_skript import doeverything
#from ..Skripte import datencheck

# Create your views here.
def optimierung_main(request):
    return render(request, 'optimierung/optimierung_main.html',)

def datencheck(request):
    print("datencheck")
    messages = datenpruefer.machdencheck(datenpruefer)
    if messages == []:
        messages = ["Ihre Daten haben den Datencheck bestanden. Gehen sie nun weiter zum nächsten Schritt"]

    return render(request, 'optimierung/datencheck.html', {'messages': messages})

def parameters(request):
    return render(request, 'optimierung/parameters.html',)

def optimierung(request):
    done = doeverything()
    return render(request, 'optimierung/optimierung.html', {'done': done})
