from django.shortcuts import render
#from .models import
from django.utils import timezone
#from .tables import TeacherTable, CurrTable, MainTeacherTable, RoomTable, ParallelTable, KlassenTable
from .models import Schulklasse, Raum, Tag, Stunde, Lehrer, Schulfach, Uebergreifung, VorgabeEinheit


# Create your views here.
def input_main(request):
     return render(request, 'datainput/input_main.html',)
#
def room_page(request):
    rooms = Raum.objects.order_by('Name')
    tage = Tag.objects.order_by('Tag')
    stunden = Stunde.objects.order_by('Stunde')
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

def teacher_page(request):
    lehrers = Lehrer.objects.order_by('Name')
    return render(request,'datainput/teacher_page.html', {'lehrers':lehrers})


def curriculum_page(request):
    klassen = Schulklasse.objects.order_by('Name')
    return render(request,'datainput/curriculum_page.html', {'klassen': klassen})

def mainteacher_page(request):
    klassen = Schulklasse.objects.order_by('Name')
    return render(request, 'datainput/mainteacher_page.html', {'klassen':klassen})

def parallel_page(request):
    faecher = Schulfach.objects.order_by('Name')
    parallels =[]
    for fach in faecher:
        if fach.Parallel != None:
            parallels.append(fach)

    return render(request,'datainput/parallel_page.html', {'parallels': parallels})

def uebergreifend_page(request):
    uebergreifend = Uebergreifung.objects.order_by('fach')
    return render(request,'datainput/uebergreifend_page.html', {'uebergreifend':uebergreifend})
#
# def unavailable_page(request):
#     unavailables = Teacherunavailable.objects.order_by('title')
#     return render(request, 'datainput/unavailable_page.html', {'unavailables':unavailables})
#
def hoursperday_page(request):
    klassen =  Schulklasse.objects.order_by('Name')
    tage = Tag.objects.order_by('Tag')
    return render(request, 'datainput/hoursperday_page.html', {'klassen':klassen, 'tage':tage})

def guidelines_page(request):
    # klassen =  Schulklasse.objects.order_by('Name')
    # return render(request, 'datainput/guidelines_page.html', {'klassen':klassen})

    klassen = Schulklasse.objects.order_by('Name')
    tage = Tag.objects.order_by('Tag')
    stunden = Stunde.objects.order_by('Stunde')
    klasseToVorgabe = []
    for klasse in klassen:
        vorgabenListe = []
        for stunde in stunden:
            tagVorgabenListe = []
            for tag in tage:
                tagVorgabenListe.append(VorgabeEinheit.Zeitslot.filter(Stunde=stunde, Tag=tag).exists())
            vorgabenListe.append((klasse, tagVorgabenListe))
        klasseToVorgabe.append((klasse, vorgabenListe))
        # [("Klasse 1", [("Stunde 1", [??????])])]
        # [("raum 1", [("stunde 1", [True, False, True])])]
    return render(request, 'datainput/room_page.html', {
        'klassen': klassen,
        'tage': tage,
        'stunden': stunden,
        'klasseToVorgabe': klasseToVorgabe,
    })
