from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import Schulklasse, Raum, Tag, Stunde, Lehrer, Schulfach, Uebergreifung, VorgabeEinheit
from django.forms import modelformset_factory


from django.http import HttpResponseRedirect
from .forms import LehrerForm


# Create your views here.
@login_required
def input_main(request):
     return render(request, 'datainput/input_main.html',)

@login_required
def room_page(request):
    rooms = Raum.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    roomToSlot = []
    for raum in rooms:
        stundenListe = []
        for stunde in stunden:
            tagBelegungsListe = []
            for tag in tage:
                tagBelegungsListe.append(raum.Nichtfrei.filter(Stunde=stunde, Tag=tag).exists())
            stundenListe.append((stunde, tagBelegungsListe))
        roomToSlot.append((raum, stundenListe))
        # [("raum 1", [("stunde 1", [True, False, True])])]
    return render(request, 'datainput/room_page.html', {
        'rooms': rooms,
        'tage': tage,
        'stunden': stunden,
        'roomToSlot': roomToSlot,
    })

@login_required
def teacher_page(request):
    lehrers = Lehrer.objects.order_by('Name')
    TeacherFormSet = modelformset_factory(Lehrer, fields = ("__all__"))
    if request.method == "POST":
        formset = TeacherFormSet(
            request.POST, request.FILES,
            queryset = Lehrer.objects.all()
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = TeacherFormSet(queryset = Lehrer.objects.all())
    return render(request,'datainput/teacher_page.html', {'lehrers':lehrers, 'formset': formset})


@login_required
def curriculum_page(request):
    klassen = Schulklasse.objects.order_by('Name')
    print([k.lehrfaecher_set.all() for k in klassen])
    return render(request,'datainput/curriculum_page.html', {'klassen': klassen})


@login_required
def mainteacher_page(request):
    klassen = Schulklasse.objects.order_by('Name')
    return render(request, 'datainput/mainteacher_page.html', {'klassen':klassen})


@login_required
def parallel_page(request):
    faecher = Schulfach.objects.order_by('Name')
    parallels = []

    for fach in faecher:
        parallelfaecher=[fach]
        for parfach in faecher:
            if parfach.Parallel == fach:
                parallelfaecher.append(parfach)
        if len(parallelfaecher) > 1:
            parallels.append(parallelfaecher)

    return render(request,'datainput/parallel_page.html', {'parallels': parallels})


@login_required
def uebergreifend_page(request):
    uebergreifend = Uebergreifung.objects.order_by('fach')
    return render(request,'datainput/uebergreifend_page.html', {'uebergreifend':uebergreifend})


@login_required
def unavailable_page(request):
    # lehrers = Lehrer.objects.order_by('Name')
    # return render(request, 'datainput/unavailable_page.html', {'lehrers':lehrers})

    lehrers = Lehrer.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    stundenListe = []
    for stunde in stunden:
        tagBelegungsListe = []
        for tag in tage:
            tagNichtda = lehrers.filter(NichtDa__Stunde = stunde, NichtDa__Tag = tag)
            tagBelegungsListe.append(tagNichtda)
        stundenListe.append((stunde, tagBelegungsListe))
    return render(request, 'datainput/unavailable_page.html', {
        'lehrers': lehrers,
        'tage': tage,
        'stunden': stunden,
        'stundenListe': stundenListe,
    })


@login_required
def hoursperday_page(request):
    klassen =  Schulklasse.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')
    return render(request, 'datainput/hoursperday_page.html', {'klassen':klassen, 'tage':tage})


@login_required
def guidelines_page(request):
    # klassen =  Schulklasse.objects.order_by('Name')
    # return render(request, 'datainput/guidelines_page.html', {'klassen':klassen})

    klassen = Schulklasse.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    vorgaben = VorgabeEinheit.objects.order_by('Schulklasse')
    klasseToVorgabe = []
    for klasse in klassen:
        vorgabenListe = []
        for stunde in stunden:
            tagVorgabenListe = []
            for tag in tage:
                # Hier in der Zeile ist ein Fehler
                tagVorgabenListe.append(vorgaben.filter(Zeitslot__Stunde=stunde, Zeitslot__Tag=tag, Schulklasse=klasse).first())
            vorgabenListe.append((stunde, tagVorgabenListe))
        klasseToVorgabe.append((klasse, vorgabenListe))
        # [("Klasse 1", [("Stunde 1", [??????])])]
        # [("raum 1", [("stunde 1", [True, False, True])])]
    return render(request, 'datainput/guidelines_page.html', {
        'klassen': klassen,
        'tage': tage,
        'stunden': stunden,
        'klasseToVorgabe': klasseToVorgabe,
    })
