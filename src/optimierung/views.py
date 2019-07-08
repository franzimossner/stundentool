from django.shortcuts import render

# Create your views here.
def optimierung_main(request):
    return render(request, 'optimierung/optimierung_main.html',)

def datencheck(request):
    return render(request, 'optimierung/datencheck.html',)

def parameters(request):
    return render(request, 'optimierung/parameters.html',)

def optimierung(request):
    return render(request, 'optimierung/optimierung.html',)
