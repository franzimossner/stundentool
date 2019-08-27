'''Hier wird das Modell gespeichert

Aus den anderen Teilen werden die Modelle und Parameter importiert und zu einem Modell zusammen gefügt.
Im Main-Skript wird diese Datei dann an die Solver gechickt, der dann das X_res file produziert, das dann verarbeitet wird

Content of a pyomo model
Set: data set to define model instance
Param: parameter data
Var: descision variables
objective: minimizing or maximizing function
constraint: constraints

Here we will probably use abstract models since we have parameters and cosntraints depending on the size od some sets
'''


'''Import von allen nötigen Modellklassen und von pyomo
'''
#from __future__ import division
from pyomo.environ import *

#import von Django Model Klassen
from datainput.models import Raum, Lehrer, Schulklasse, Schulfach, Lehrfaecher, Unterrricht, Tag, Stunde, Slot, Partner, LehrerBelegt, RaumBelegt, VorgabeEinheit
from optimierung.models import Parameters

'''Initialisierung des Problems
'''
# wir deklarieren ein abstraktes Modell, weil wir sich ändernde Daten haben
model = AbstractModel()

'''Deklaration von Funktionen
'''

def Klassleitung(klasse):
    # gibt die Klassleitung einer Klasse zurück
    klasse = Schulklasse.objects.get(Name=klasse)
    klassleitung = [klasse.Klassenlehrer.Kurzname]
    return klassleitung

def Haupttandem(klasse):
    # gibt den Haupttandem einer Klasse zurück
    klasse = Schulklasse.objects.get(Name=klasse)
    haupttandem = klasse.HauptTandem.Kurzname
    return haupttandem

def Partnerlehrer(klasse):
    # gibt eine Liste an Partnerlehrern der Klasse zurück
    klasse = Schulklasse.objects.get(Name=klasse)
    partnerlehrer = klasse.partner__set.all()
    return partnerlehrer


def Unterricht(lehrer):
    # gibt alle Fächer zurück, die der Lehrer unterrichtet
    lehrperson = Lehrer.objects.get(Kurzname=lehrer)
    faecher = lehrperson.Faecher.all()
    liste = []
    for fach in faecher:
        liste.append(fach.Name)
    return liste

def Fachdauer(fach, klasse):
    # gibt zurück, wie lange das Fach in der Klasse dauert
    print(fach)
    print(klasse)
    Klasse =  Schulklasse.objects.get(Name=klasse)
    Fach = Schulfach.objects.get(Name=fach)
    if Lehrfaecher.objects.filter(schulklasse=Klasse, schulfach=Fach).exists():
        schulfach = Lehrfaecher.objects.get(schulklasse=Klasse, schulfach=Fach)
        fachdauer = schulfach.blockstunden
        return fachdauer
    else:
        return 0

def wechselLehrer(klasse, lehrer, zeitslot):
    # stellt fest, ob zu dieser stunde ein Lehrerwechsel stattgefunden hat
    wl = sum(sum(model.x[k,l,f,t] for t in max(1, Range(z+1-Fachdauer(f,k), z+1))) for f in model.Faecher) + sum(model.x[k,l,g,t+1] for g in model.Faecher)
    if wl % 2 > 0:
        return 1
    else:
        return 0
    return 0

def sportGleichzeitig(klasse, zeitslot):
    # stellt fest, ob Mädchen und Jungen der Klasse gleichzeitig Sport haben
    sport = sum(model.x[k,l,"SportM",z] for l in model.Lehrer) + sum(model.x[k,l,"SportW",z] for l in model.Lehrer)
    if sport % 2 > 0 :
        return 0
    else:
        return 1

def LehrerinKlasse(klasse, lehrer):
    # stellt fest, ob der lehrer in der Klasse stunden unterrichtet
    lehrerval = sum(model.x[klasse,lehrer,f,z] for f in model.Faecher and z in model.Zeitslots)
    if lehrerval >= 1:
        return True
    else:
        return False

def getUebergreifend(fach, klasse):
    '''!!!'''
    # gibt zurück, wie viele Fächer zu dem Fach überggreifend sind in dieser Klasse (Gesamtzahl, also mindestens 1)
    schulfach = Schulfach.objects.get(Name=fach)
    schulklasse = Schulklasse.objects.get(Name=klasse)

    uebergreifend = Uebergreifung.objects.filter(schulfach=schulfach, schulklasse=schulklasse)
    menge = []
    for Klasse in uebergreifend:
        menge.append(Klasse.Name)
    return len(menge)

def Arbeitszeit(lehrer):
    # gibt die Arbeitszeit in Stunden für den Lehrer zurück
    lehrperson = Lehrer.objects.get(Kurzname=lehrer)
    stundenzahl = lehrperson.Stundenzahl
    return stundenzahl

def GleichzeitigFach(fach):
    # gibt zurück, ob das Fach parallel Fächer hat udn wenn ja, eine Liste dieser
    fach = Schulfach.objects.get(Name=fach)
    faecher = Schulfach.objects.all()
    parallelfaecher=[fach]
    for parfach in faecher:
        if parfach.Parallel == fach:
            parallelfaecher.append(parfach)
    return parallelfaecher

def convert_to_slot(number):
    #converting given number from 1 to 40 to a slot in out model
    number = int(number)
    tag = ""
    stundenindex = 0

    if number in range(1,10):
        tag = "Montag"
        stundenindex = range(1,10).index(number) + 1
    if number in range(10,19):
        tag = "Dienstag"
        stundenindex = range(10,19).index(number) + 1
    if number in range(19,28):
        tag = "Mittwoch"
        stundenindex = range(19,28).index(number) + 1
    if number in range(28,37):
        tag = "Donnerstag"
        stundenindex = range(28,37).index(number) + 1
    if number in range(37,41):
        tag = "Freitag"
        stundenindex = range(37,41).index(number) + 1

    return [tag, stundenindex]

def slot_to_number(tagindex, stundenindex):
    # wandelt einen Zeitslot mit indices in eine Nummer um, von 1 bis Ende der Woche
    # hier soll später mal die Länge der Studnen rauskommen
    number = (tagindex -1)* 9
    #max(index for index in Stunde.objects.filter(Index=index))
    number2 = number + stundenindex
    return number2

def RaumVerfuegbar(raum, zeitslot):
    '''!!!'''
    # gibt zurück, ob der Raum zu dem Zeitpunkt verfügbar Ist
    # soll die zahl der Räume dieses Raumtyps zum Zeitpunkt angeben
    # hole alle Räume mit diesem Fach und prüfe dann wie viele frei sind, da es keine Überschneidungen gibt
    raum = Raum.objects.get(Name=raum)
    # alle Räume mit der gleichen Fächerkombination
    raumliste = Raum.objects.filter(nutzbar__set=raum.nutzbar__set)
    slotliste = convert_to_slot(zeitslot)
    zeitslot = Slot.objects.get(Tag_Tag=slotliste[0], Stunde_Index=slotliste[1])

    raumverfuegbar = 0
    for ort in raumliste:
        if not RaumBelegt.objects.filter(raum=ort, slot=zeitslot).exists():
            raumverfuegbar += 1
    return raumverfuegbar

def RaumFaecher(raum):
    # gibt die Fächer eines Raumes zurück
    raumobj = Raum.objects.get(Name=raum)
    faecherliste = [fach.Name for fach in raumobj.nutzbar__set.all()]
    return faecherliste

def GeteilteFaecher(fach, klasse):
    # gibt zrück, in wie viele Gruppen die Klasse zu teilen ist
    schulfach = Schulfach.objects.get(Name=fach)
    schulklasse = Schulklasse.objects.get(Name=klasse)
    gruppenzahl = Lehrfaecher.objects.get(schulklasse=schulklasse, schulfach=schulfach).klassengruppen
    return gruppenzahl

def Lehrplanstunden(fach, klasse):
    # gibt zurück, wie viele studnen die klasse in dem Fach machen muss
    schulklasse = Schulklasse.objects.get(Name=klasse)
    schulfach = Schulfach.objects.get(Name=fach)
    stundenzahl = Lehrfaecher.objects.get(schulklasse=schulklasse, schulfach=schulfach).wochenstunden
    return stundenzahl

def Klassenfaecher(klasse):
    # gibt zurück, welche Fächer dir Klasse hat
    schulklasse = Schulklasse.objects,get(Name=klasse)
    faecherliste = []
    for fach in schulklasse.lehrfaecher__set:
        faecherliste.append(fach.Name)
    return faecherliste


'''Deklaration von Mengen

Die Mengen im Modell enthalen keine Django Objekte, sondern nur deren Namen oder einen anderen Refernzwert. Mit objects.get() kann dann das echt Objekt geholt werden, um Werte abzufragen
'''

# Lehrer
# get Lehrerzahl aus Django
zahlLehrer = Lehrer.objects.all().count()
# initialisiere Menge
Lehrermenge = []
for lehrer in Lehrer.objects.order_by('Kurzname'):
    Lehrermenge.append(lehrer.Kurzname)
model.Lehrer = Set(initialize=Lehrermenge)
#model.Lehrer = Set(dimen=zahlLehrer, initialize=Lehrermenge)

# Klassen
# get Klassenzahl aus Django
zahlKlassen = Schulklasse.objects.all().count()
# initialisiere Menge
Klassenmenge = []
for klasse in Schulklasse.objects.order_by('Name'):
    Klassenmenge.append(klasse.Name)
model.Klassen = Set(initialize=Klassenmenge)
#model.Klassen = Set(dimen=zahlKlassen, initialize=Klassenmenge)

# Räume
# get raumzahl aus Django
zahlraum = Raum.objects.all().count()
# initialisiere Menge
Raummenge =[]
for raum in Raum.objects.order_by('Name'):
    Raummenge.append(raum.Name)
model.Raeume = Set(initialize=Raummenge)
#model.Raeume = Set(dimen=zahlraum, initialize=Raummenge)

# Zeitslots
# get zahlslots aus Django
zahlslots = Slot.objects.all().count()
# initialisiere Menge
model.Zeitslots = RangeSet(1, zahlslots)

# Fächer
Schulfachmenge = []
for fach in Schulfach.objects.order_by('Name'):
    Schulfachmenge.append(fach.Name)
model.Faecher = Set(initialize=Schulfachmenge)

# Vorgaben
Vorgabenmenge = []
for vorgabe in VorgabeEinheit.objects.order_by('Schulklasse'):
    stundenindex = vorgabe.Zeitslot.Stunde.Index
    tagindex = vorgabe.Zeitslot.Tag.Index
    zeitnummer = slot_to_number(tagindex, stundenindex)
    Vorgabenmenge.append(frozenset([vorgabe.Schulklasse.Name, vorgabe.Fach.Name, zeitnummer, vorgabe.Lehrperson]))
model.Vorgaben = Set(initialize=Vorgabenmenge)


'''Deklaration von Parametern
'''

# Deklariere optimierungsparameter aus den modellen, der Parameter solver wird erst im main-skript abgefragt und verwendet
model.lehrerinKlasseGewicht = Param(initialize=Parameters.lehrerinKlasse)
model.tandeminKlasseGewicht = Param(initialize=Parameters.tandeminKlasse)
model.partnerinKlasseGewicht = Param(initialize=Parameters.partnerinKlasse)
model.lehrerwechselGewicht = Param(initialize=Parameters.lehrerwechsel)
model.sportunterrichtGewicht = Param(initialize=Parameters.sportunterricht)
model.lehrerminimumGewicht = Param(initialize=Parameters.lehrerminimum)

# die zahl der parallelen Fächer in der größten Gruppe
faecher = Schulfach.objects.all()
lengths = []
for fach in faecher:
    parallelfaecher=[fach]
    for parfach in faecher:
        if parfach.Parallel == fach:
            parallelfaecher.append(parfach)
    lengths.append(len(parallelfaecher))
model.maxUebergreifungRange = max(lengths)


'''Variablendeklaration
    Ziel: Kreiere nur Variablen, bei denen es möglich ist, dass sie den Wert 1 annehmen
'''
# deklariere die variable, boolean setzt es als 0/1 variable
# die 4 Mengen sind die Indexmengen in dieser Reihenfolge
model.x = Var(model.Klassen, model.Lehrer, model.Faecher, model.Zeitslots, domain=Boolean)

'''Objective Function
    Sie besteht aus allen softconstraints mit den Gewichten (Parametern)
'''

def ObjRule(model):
    # Gewicht * Summe über alle klassen, deren Klassleitungen, deren Unterrichtsfächer und alle Zeitslot mit dem wert der Variable und der Fachdauer
    # Belohne jedes Ereignis, in dem der Klassleiter in seiner Klasse ist
    lehrerKlasse = model.lehrerinKlasseGewicht * sum(model.x[k,l,f,z] * Fachdauer(f,k) for k in model.Klassen for f in Unterricht(Klassleitung(k)[0]) for z in model.Zeitslots for l in Klassleitung(k))
    # Gewicht * Summer über alle Klassen, deren HauptTandem, deren Fächer und allen Zeitslots mit dem Wert der Variable und der Fachdauer
    # Belohne jedes Ereignis, in dem der HauptTandemin der Klasse ist
    tandemKlasse = model.tandeminKlasseGewicht * sum(model.x[k,l,f,z] * Fachdauer(f,k) for k in model.Klassen and f in Unterricht(Haupttandem(k)) and z in model.Zeitslots and l==Haupttandem(k))

    # Belohne jedes Ereignis, bei dem ein Partnerlehrer in der Klasse ist
    partnerKlasse = 0
    for k in model.Klassen and pl in Partnerlehrer(k):
        partnerKlasse += model.partnerinKlasseGewicht * sum(model.x[k,l,f,z] * Fachdauer(f,k) for k in model.Klassen and f in Unterricht(pl) and z in model.Zeitslots and l==pl)

    # Belohne, wenn es weniger Lehrerwechsel im Tagesablauf gibt
    wechsel = model.lehrerwechselGewicht * sum(wechselLehrer(k,l,z) * 0.5 for k in model.Klassen and l in model.Lehrer and z in range(1, zahlslots))

    # Belohne, wenn Mädchen und Jungen der Klasse gleichzeitig Sport haben
    sport = model.sportunterrichtGewicht * sum(sportGleichzeitig(k,z) for k in model.Klassen and z in model.Zeitslots)

    # Belohne, wenn wenige Lehrer insgesamt die Klasse unterrichten
    lehrermin = model.lehrerminimumGewicht * sum(LehrerinKlasse(k,l) for k in model.Klassen and l in model.Lehrer)

    # Setze alles zu einer Zielfunktion zusammen
    objective = lehrerinKlasse + tandeminKlasse + partnerinKlasse - wechsel + sport - lehrermin
    return objective

# Set objective
model.Obj = pyomo.environ.Objective(rule=ObjRule, sense=maximize)


''' Deklaration von Constraints
'''
# Vorgaben, sowohl mit als auch ohne Lehrer angegeben (If Clause)
def VorgabeRule(model,vorgabe):
    for klasse, fach, zeitslot, lehrer in vorgabe:
        if lehrer != None:
            return sum(model.x[klasse, lehrer, fach, z] for z in max(1, Range(zetislot+1-Fachdauer(fach,klasse), zeitslot+1)))>= 1
        else:
            sum(model.x[klasse, fach, l, z] for l in model.Lehrer and z in max(1, Range(zetislot+1-Fachdauer(fach,klasse), zeitslot+1))) >= 1
vorgabencheck = Constraint(model.Vorgaben, rule=VorgabeRule)


# Lehrer müsssen in ihrer Arbeitszeit bleiben
def ArbeitszeitRule(model,l):
    maxArbeit = sum(model.x[k,l,f,z] * Fachdauer(f,k)/getUebergreifend(f,k) for k in model.Klassen and f in model.Faecher and z in model.Zeitslots)
    return maxArbeit <= Arbeitszeit(l)
# erstelle indexierte Constraint
maxArbeitszeit = Constraint(model.Lehrer, rule=ArbeitszeitRule)

# Räume müssen verfügbar sein
def RaumRule(model,r,z):
    if RaumVerfuegbar(r,z) > 0:
        RaumDa= sum(model.x[k,l,f,z]/getUebergreifend(f,k) for f in RaumFaecher(r) and k in model.Klassen and t in max(1, Range(z+1-Fachdauer(f,k), z+1)))
        return RaumDa <= RaumVerfuegbar(r,z)
# erstelle Constraints
Raumverfuegbarkeit = Constraint(model.Raeume, model.Zeitslots, rule=RaumRule)

# Parallele Fächer müssen gleichzeitig stattfinden
'''!!! Synatx Error: cant assign to function call bei zweitem k in model.x'''
def GleichzeitigRule(model,f,k,z):
    if len(GleichzeitigFach(f)) > 0 :
        gleich = sum(model.x[k,l,f,z] for l in model.Lehrer) - sum(model.x[k,l,fach,z] for l in model.Lehrer and fach in GleichzeitigFach(f))
        return gleich == 0
# erstelle Constraint
paralleleFaecher = Constraint(model.Faecher, model.Klassen, model.Zeitslots, rule=GleichzeitigRule)

# Es darf nur ein Unterricht pro stunde pro klasse stattfinden, außer für geteilte Fächer
def NureinUnterrichtRule(model,k,z):
    maxUnterricht = sum(model.x[k,l,f,z]/GeteilteFaecher(f,k) for f in model.Faecher and l in model.Lehrer and t in max(1, Range(z+1-Fachdauer(f,k), z+1)))
    return maxUnterricht <= 1
NureinUnterricht = Constraint(model.Klassen, model.Zeitslots, rule=NureinUnterrichtRule)

# parallele und geteilte fächer müssen zusammen stattfinden
# '''??? Ist das eine Restriktion oder nicht?'''
# model.ggf = Var(model.Faecher, model.Klassen, model.Zeitslots, domain=boolean)
# def parallelundgeteiltRule(model,f,k,z):
#     if f in Klassenfaecher(f):
#         model.ggf[f,k,z] = sum(model.x[k,l,f,z]/GeteilteFaecher(f) for l in model.Lehrer and f in Unterricht(l))

# Ein lehrer darf nur einen Unterricht geben, außer bei übergreifenden fächern
def lehrernureinUnterrichtRule(model,l,z):
    lv = 0
    for f in Unterricht(l):
        if Uebergreifend(f,1).exists():
            lv += sum(1/len(Uebergreifend(f,gruppe)) * sum(model.x[k,l,f,z] for k in Uebergreifend(f,gruppe) for gruppe in range(1,maxUebergreifung +1) and Uebergreifend(f,gruppe).exists()))
        else:
            lv += sum(model.x[k,l,f,t] for k in model.Klassen and t in max(1, Range(z+1-Fachdauer(f), z+1)))
    return lv <= 1
LehrerUnterricht = Constraint(model.Lehrer, model.Zeitslots, rule=lehrernureinUnterrichtRule)


# Übergreifende Fächer brauchen auch den gleichen Lehre
'''??? glaube nicht richtig'''
def UebergreifendgleicherLehrerRule(model,f,gruppe,l,z):
    for f in model.Faecher, gruppe in range(1, maxUebergreifung +1), l in model.Lehrer, z in model.Zeitslots and Uebergreifend(f,gruppe).exists():
        klassetemp = Uebergreifend(f,gruppe)
        for i in  range(1,len(klassetemp)):
            uebergreifendLehrer = model.x[klassetemp[i],l,f,z] - model.x[klassetemp[i+1],l,f,z]
            return uebergreifendLehrer ==  0
UebergreifendgleicherLehrer = Constraint(model.Faecher, model.maxUebergreifungRange, model.Lehrer, model.Zeitslots, rule=UebergreifendgleicherLehrerRule)


# Übergreifende Fächer müsssen zusammen stattfinden
'''??? glaube nicht richtig'''
def UebergreifendzusammenRule(model):
    for f in model.Faecher, gruppe in range(1, maxUebergreifung +1), z in model.Zeitslots and Uebergreifend(f,gruppe).exists():
        klassetemp = Uebergreifend(f, gruppe)
        for i in range(1, len(klassetemp)):
            uebergreifendzusammen = sum( model.x[klassetemp[i],l,f,z] for l in model.Lehrer) - sum(model.x[klassetemp[i+1],l,f,z] for l in model.Lehrer)
            return uebergreifendzusammen == 0
Uebergreifendzusammen = Constraint(model.Faecher, model.Zeitslots, model.maxUebergreifungRange, model.Zeitslots, rule=UebergreifendzusammenRule)


# Jede Klasse muss ihren Lehrplan erfüllen
def LehrplanRule(model,f,k):
    mindestUnterricht = sum(model.x[k,l,f,z] * Fachdauer(f,k)/GeteilteFaecher(f,k) for l in model.Lehrer and z in model.Zeitslots)
    return mindestUnterricht >= Lehrplanstunden(f,k)
Lehrplanerfuellt = Constraint(model.Faecher, model.Klassen, rule=LehrplanRule)

# Tandemlehrer muss anwesend sein wenn gefordert
def TandemRule(model,k,z):
    Tandem1 = sum(model.x[k,l,"Tandem",z] for l  in model.Lehrer)
    Tandem2 = sum(Tandemnummer(f,k) * model.x[k,l,f,t] for f in model.Faecher and l in model.Lehrer and t in  max(1, Range(z+1-Fachdauer(f), z+1)))
    return Tandem1 == Tandem2
# erstelle Constraint
Tandembenoetigt = Constraint(model.Klassen, model.Zeitslots, rule=TandemRule)


'''Output für csv Datei in main_skript.py
'''
