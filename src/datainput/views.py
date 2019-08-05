from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Schulklasse, Raum, Tag, Stunde, Lehrer, Schulfach, Uebergreifung, VorgabeEinheit
from django.forms import modelformset_factory


from django.http import HttpResponseRedirect
from .forms import LehrerForm, SchulfachForm, UebergreifungForm, BlockenForm, TagesForm, VorgabenForm, KlassenForm, PartnerForm, LehrfaecherForm, RaumForm, UnterrrichtForm, RaumBelegtForm, NutzbarForm

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
        if 'submitRaum' in request.POST:
            formRaum = RaumForm(request.POST)
            if formRaum.is_valid():
                formRaum.save()
        else:
            formRaum = RaumForm()
        if 'submitBelegung' in request.POST:
            formBelgegt = RaumBelegtForm(request.POST)
            if formBelegt.is_valid():
                formBelegt.save()
        else:
            formBelegt = RaumBelegtForm()
        if 'submitNutzbar' in request.POST:
            formNutzbar = NutzbarForm(request.POST)
            if formNutzbar.is_valid():
                formNutzbar.save()
        else:
            formNutzbar = NutzbarForm()
    else:
        formRaum = RaumForm()
        formBelegt = RaumBelegtForm()
        formNutzbar = NutzbarForm()

    return render(request, 'datainput/room_page.html', {
        'rooms': rooms,
        'tage': tage,
        'stunden': stunden,
        'roomToSlot': roomToSlot,
        'formRaum':formRaum,
        'formBelegt': formBelegt,
        'formNutzbar': formNutzbar,
    })

@login_required
@user_passes_test(rechte_check)
def teacher_page(request):

    lehrers = Lehrer.objects.order_by('Name')
    if request.method == "POST":
        if 'submitLehrer' in request.POST:
            formLehrer = LehrerForm(request.POST)
            if formLehrer.is_valid():
                formLehrer.save()
        else:
            formLehrer = LehrerForm()
        if 'submitFaecher' in request.POST:
            formFaecher = UnterrrichtForm(request.POST)
            if formFaecher.is_valid():
                formFaecher.save()
        else:
            formFaecher = UnterrrichtForm()
    else:
        formLehrer = LehrerForm()
        formFaecher = UnterrrichtForm()
    return render(request,'datainput/teacher_page.html', {'lehrers':lehrers, 'formLehrer': formLehrer, 'formFaecher': formFaecher})


@login_required
@user_passes_test(rechte_check)
def curriculum_page(request):
    klassen = Schulklasse.objects.order_by('Name')

    if request.method == "POST":
        if 'submitKlasse' in request.POST:
            formKlasse = KlassenForm(request.POST)
            if formKlasse.is_valid():
                formKlasse.save()
        else:
            formKlasse = KlassenForm()
        if 'submitFaecher' in request.POST:
            formFaecher = LehrfaecherForm(request.POST)
            if formFaecher.is_valid():
                formFaecher.save()
        else:
            formFaecher = LehrfaecherForm()
    else:
        formKlasse = KlassenForm()
        formFaecher = LehrfaecherForm()
    return render(request,'datainput/curriculum_page.html', {'klassen': klassen, 'formKlasse':formKlasse, 'formFaecher': formFaecher})


@login_required
@user_passes_test(rechte_check)
def mainteacher_page(request):
    klassen = Schulklasse.objects.order_by('Name')

    if request.method == "POST":
        if 'submitKlasse' in request.POST:
            formKlasse = KlassenForm(request.POST)
            if formKlasse.is_valid():
                formKlasse.save()
        else:
            formKlasse = KlassenForm()
        if 'submitPartner' in request.POST:
            formPartner = PartnerForm(request.POST)
            if formPartner.is_valid():
                formPartner.save()
        else:
            formPartner = PartnerForm()
    else:
        formKlasse = KlassenForm()
        formPartner = PartnerForm()

    return render(request, 'datainput/mainteacher_page.html', {'klassen':klassen, 'formKlasse':formKlasse, 'formPartner': formPartner})


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
