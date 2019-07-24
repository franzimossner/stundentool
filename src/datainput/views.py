from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Schulklasse, Raum, Tag, Stunde, Lehrer, Schulfach, Uebergreifung, VorgabeEinheit
from django.forms import modelformset_factory


from django.http import HttpResponseRedirect
from .forms import LehrerForm, SchulfachForm, UebergreifungForm, BlockenForm, TagesForm, VorgabenForm, KlassenForm, PartnerForm, LehrfaecherForm, RaumForm

def rechte_check(user):
    return user.username in ['Direktor','franzi']

# Create your views here.
@login_required
@user_passes_test(rechte_check)
def input_main(request):
     return render(request, 'datainput/input_main.html',)

@login_required
@user_passes_test(rechte_check)
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

    if request.method == "POST":
        form = RaumForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = RaumForm()

    return render(request, 'datainput/room_page.html', {
        'rooms': rooms,
        'tage': tage,
        'stunden': stunden,
        'roomToSlot': roomToSlot,
        'form':form
    })

@login_required
@user_passes_test(rechte_check)
def teacher_page(request):
    lehrers = Lehrer.objects.order_by('Name')
    if request.method == "POST":
        form = LehrerForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = LehrerForm()
    return render(request,'datainput/teacher_page.html', {'lehrers':lehrers, 'form': form})


@login_required
@user_passes_test(rechte_check)
def curriculum_page(request):
    klassen = Schulklasse.objects.order_by('Name')

    if request.method == "POST":
        form = LehrfaecherForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = LehrfaecherForm()
    return render(request,'datainput/curriculum_page.html', {'klassen': klassen, 'form':form})


@login_required
@user_passes_test(rechte_check)
def mainteacher_page(request):
    klassen = Schulklasse.objects.order_by('Name')

    if request.method == "POST":
        form = KlassenForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = KlassenForm()

    # if request.method == "POST":
    #     form = PartnerForm(request.POST)
    #     if form.is_valid():
    #         form.save()
    # else:
    #     form = PartnerForm()

    return render(request, 'datainput/mainteacher_page.html', {'klassen':klassen, 'form':form})


@login_required
@user_passes_test(rechte_check)
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

    if request.method == "POST":
        form = SchulfachForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = SchulfachForm()

    return render(request,'datainput/parallel_page.html', {'parallels': parallels, 'form': form})


@login_required
@user_passes_test(rechte_check)
def uebergreifend_page(request):
    uebergreifend = Uebergreifung.objects.order_by('fach')

    if request.method == "POST":
        form = UebergreifungForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = UebergreifungForm()

    return render(request,'datainput/uebergreifend_page.html', {'uebergreifend':uebergreifend, 'form':form})


@login_required
@user_passes_test(rechte_check)
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

    if request.method == "POST":
        form = BlockenForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = BlockenForm()

    return render(request, 'datainput/unavailable_page.html', {
        'lehrers': lehrers,
        'tage': tage,
        'stunden': stunden,
        'stundenListe': stundenListe,
        'form': form
    })


@login_required
@user_passes_test(rechte_check)
def hoursperday_page(request):
    klassen =  Schulklasse.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')

    if request.method == "POST":
        form = TagesForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = TagesForm()

    return render(request, 'datainput/hoursperday_page.html', {'klassen':klassen, 'tage':tage, 'form': form})


@login_required
@user_passes_test(rechte_check)
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

    if request.method == "POST":
        form = VorgabenForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = VorgabenForm()

    return render(request, 'datainput/guidelines_page.html', {
        'klassen': klassen,
        'tage': tage,
        'stunden': stunden,
        'klasseToVorgabe': klasseToVorgabe,
        'form':form
    })
