from django.shortcuts import render
from .datencheck import datenpruefer
from .main_skript import doeverything
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Parameters
from datainput.views import rechte_check

from django.http import HttpResponseRedirect
from .forms import ParameterForm

# Create your views here.
@login_required
@user_passes_test(rechte_check)
def optimierung_main(request):
    return render(request, 'optimierung/optimierung_main.html',)

@login_required
@user_passes_test(rechte_check)
def datencheck(request):
    messages = []
    messages = datenpruefer.machdencheck(datenpruefer)
    if messages == []:
        messages = ["Ihre Daten haben den Datencheck bestanden. Gehen sie nun weiter zum nächsten Schritt"]

    return render(request, 'optimierung/datencheck.html', {'messages': messages})

@login_required
@user_passes_test(rechte_check)
def parameters(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ParameterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            Parameters.lehrerinKlasse = form.cleaned_data['lehrerinKlasse']
            Parameters.tandeminKlasse = form.cleaned_data['tandeminKlasse']
            Parameters.partnerinKlasse = form.cleaned_data['partnerinKlasse']
            Parameters.lehrerwechsel = form.cleaned_data['lehrerwechsel']
            Parameters.sportunterricht = form.cleaned_data['sportunterricht']
            Parameters.lehrerminimum = form.cleaned_data['lehrerminimum']
            Parameters.solver = form.cleaned_data['solver']
            ''' parameter verarbeiten
            '''
            form.save()
    else:
        form = ParameterForm()

    return render(request, 'optimierung/parameters.html', {'form': form})


@login_required
@user_passes_test(rechte_check)
def optimierung(request):
    done = doeverything()
    return render(request, 'optimierung/optimierung.html', {'done': done})
