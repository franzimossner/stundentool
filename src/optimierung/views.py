from django.shortcuts import render
#from ..Skripte import datencheck

# Create your views here.
def optimierung_main(request):
    return render(request, 'optimierung/optimierung_main.html',)

def datencheck(request):
    # message = datencheck
    # if message == []:
    #     message = ["Ihre Daten haben den Datenchek bestanden. Gehen sie nun weiter zum nächsten Schritt"]

    messages = ["Ihre Daten haben den Datencheck bestanden. Gehen sie nun weiter zum nächsten Schritt"]
    return render(request, 'optimierung/datencheck.html', {'messages': messages})

def parameters(request):
    return render(request, 'optimierung/parameters.html',)

def optimierung(request):
    return render(request, 'optimierung/optimierung.html',)
