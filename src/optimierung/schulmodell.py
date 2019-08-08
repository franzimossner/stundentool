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
from datainput.models import Raum, Lehrer, Schulklasse, Schulfach, Lehrfaecher, Unterrricht, Tag, Stunde, Zeitslot, Partner, LehrerBelegt, RaumBelegt
from optimierung.models import Parameters

'''Initialisierung des Problems
'''
# wir deklarieren ein abstraktes Modell, weil wir sich ändernde Daten haben
model = AbstractModel()

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
model.Lehrer = Set(dimen=zahlLehrer, initialize=Lehrermenge)

# Klassen
# get Klassenzahl aus Django
zahlKlassen = Schulklasse.objects.all().count()
# initialisiere Menge
Klassenmenge = []
for klasse in Schulklasse.objects.order_by('Name'):
    Klassenmenge.append(klasse.Name)
model.Klassen = Set(dimen=zahlKlassen, initialize=Klassenmenge)

# Räume
# get raumzahl aus Django
zahlraum = Raum.objects.all().count()
# initialisiere Menge
Raummenge =[]
for raum in Raum.objects.order_by('Name'):
    Raummenge.append(raum.Name)
model.Raeume = Set(dimen=zahlraum, initialize=Raummenge)

# Zeitslots
# get zahlslots aus Django
zahlslots = Zeitslot.objects.all().count()
# initialisiere Menge
model.Zeitslots = RangeSet(1, zahlslots)
# noch eine Funktion benötigt, die aus einer Zahl den Slot kreiren kann und anders rum

# Fächer
Schulfachmenge = []
for fach in Schulfach.objects.order_by('Name'):
    Schulfachmenge.append(fach.Name)
model.Faecher = Set(initialize=Schulfachmenge)



'''Deklaration von Funktionen
'''

def Klassleitung(model, klasse):
    # gibt die Klassleitung einer Klasse zurück
    klasse = Schulklasse.objects.get(Name=klasse)
    klassleitung = klasse.Klassenlehrer.Name
    return klassleitung

def Haupttandem(model,klasse):
    # gibt den Haupttandem einer Klasse zurück
    klasse = Schulklasse.objects.get(Name=klasse)
    haupttandem = klasse.HauptTandem.Name
    return haupttandem

def Partnerlehrer(model,klasse):
    # gibt eine Liste an Partnerlehrern der Klasse zurück
    klasse = Schulklasse.objects.get(Name=klasse)
    partnerlehrer = klasse.partner_set.all()
    return partnerlehrer


def Unterricht(model, lehrer):
    # gibt alle Fächer zurück, die der Lehrer unterrichtet
    lehrperson = Lehrer.objects.get(Kurzname=lehrer)
    faecher = lehrperson.Faecher.all()
    return faecher

def Fachdauer(model, fach, klasse):
    # gibt zurück, wie lange das Fach in der Klasse dauert
    Klasse =  Schulklasse.objects.get(Name=klasse)
    fachdauer = Lehrfaecher.objects.get(schulklasse=klasse, schulfach=fach).blockstunden
    return fachdauer

def wechselLehrer(model, klasse, lehrer, zeitslot):
    # stellt fest, ob zu dieser stunde ein Lehrerwechsel stattgefunden hat
    #TODO
    return 0

def sportGleichzeitig(model, klasse, zeitslot):
    # stellt fest, ob Mädchen und Jungen der Klasse gleichzeitig Sport haben
    #TODO
    return 0

def LehrerinKlasse(model, klasse, lehrer):
    # stellt fest, ob der lehrer in der Klasse stunden unterrichtet
    # TODO
    return 0

def getUebergreifend(model, fach, klasse):
    # gibt zurück, in wie viele Grupen die Klasse für das Fach geteilt ist
    return 0

def Arbeitszeit(model, lehrer):
    # gibt die Arbeitszeit in Stunden für den Lehrer zurück
    return 0

def GleichzeitigFach(model, fach):
    # gibt zurück, ob das Fach parallel Fächer hat udn wenn ja, eine Liste dieser
    return 0

def RaumVerfuegbar(model, raum, zeitslot):
    # gibt die Zahl der freien möglichen Räume zu dem Zeitpunkt an
    return 0

'''Deklaration von Parametern
'''

# Deklariere optimierungsparameter aus den modellen, der Parameter solver wird erst im main-skript abgefragt und verwendet
model.lehrerinKlasseGewicht = Param(initialize=Paramters.lehrerinKlasse)
model.tandeminKlasseGewicht = Param(initialize=Parameters.tandeminKlasse)
model.partnerinKlasseGewicht = Param(initialize=Parameters.partnerinKlasse)
model.lehrerwechselGewicht = Param(initialize=Parameters.lehrerwechsel)
model.sportunterrichtGewicht = Param(initialize=Parameters.sportunterricht)
model.lehrerminimumGewicht = Param(initialize=Parameters.lehrerminimum)


'''Variablendeklaration
    Ziel: Kreiere nur Variablen, bei denen es möglich ist, dass sie den Wert 1 annehmen
'''
# deklariere die variable, boolean setzt es als 0/1 variable
# die 4 Mengen sind die Indexmengen in dieser Reihenfolge
model.x = Var(model.Klassen, model.Lehrer, model.Zeitslots, model.Faecher, domain=Boolean)

'''Objective Function
    Sie besteht aus allen softconstraints mit den Gewichten (Parametern)
'''

def ObjRule(model):
    # Gewicht * Summe über alle klassen, deren Klassleitungen, deren Unterrichtsfächer und alle Zeitslot mit dem wert der Variable und der Fachdauer
    # Belohne jedes Ereignis, in dem der Klassleiter in seiner Klasse ist
    lehrerKlasse = model.lehrerinKlasseGewicht * sum(model.x[k,l,z,f] * Fachdauer(f,k) for k in model.Klassen and f in Unterricht(Klassleitung(k)) and z in model.Zeitslots and l=Klassleitung(k))
    # Gewicht * Summer über alle Klassen, deren HauptTandem, deren Fächer und allen Zeitslots mit dem Wert der Variable und der Fachdauer
    # Belohne jedes Ereignis, in dem der HauptTandemin der Klasse ist
    tandemKlasse = model.tandeminKlasseGewicht * sum(model.x[k,l,z,f] * Fachdauer(f,k) for k in model.Klassen and f in Unterricht(Haupttandem(k)) and z in model.Zeitslots and l=Haupttandem(k))

    # Belohne jedes Ereignis, bei dem ein Partnerlehrer in der Klasse ist
    partnerKlasse = 0
    for k in model.Klassen and pl in Partnerlehrer(k):
        partnerKlasse += model.partnerinKlasseGewicht * sum(model.x[k,l,z,f] * Fachdauer(f,k) for k in model.Klassen and f in Unterricht(pl) and z in model.Zeitslots and l=pl)

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
model.Obj = Objective(rule=ObjRule, sense=maximize)


''' Deklaration von Constraints
'''


# Lehrer müsssen in ihrer Arbeitszeit bleiben
def ArbeitszeitRule(model):
    for l in model.Lehrer:
        maxArbeit(l) = sum(model.x[k,model.Lehrer[l],z,f] * Fachdauer(f,k)/getUebergreifend(f,k) for k in model.Klassen and f in model.Faecher and z in model.Zeitslots)
    return maxArbeit(l) <= Arbeitszeit(l)
# erstelle indexierte Constraint
maxArbeitszeit = Constraint(model.Lehrer, rule=ArbeitszeitRule)

# Räume müssen verfügbar sein
def RaumRule(model):
    for (r in model.Raeume, z in model.Zeitslots) with RaumVerfuegbar(r,z) > 0:
        RaumDa(r,z)= sum(model.x[k,l,z,f]/getUebergreifend(f,k) for f in RaumFaecher(r) and k in model.Lehrer and t in max(1, Range(z+1-Fachdauer(f), z+1)))
    return RaumDa(r,z) <= RaumVerfuegbar(r,z)
# erstelle Constraints
Raumverfuegbarkeit = Constraint(model.Raeume, model.Zeitslots, rule=RaumRule)

# Parallele Fächer müssen gleichzeitig stattfinden
def GleichzeitigRule(model):
    for f in model.Faecher with GleichzeitigFach(f) == True:
        gleichzeitig(f,k,z) = sum(model.x[k,l,f,z] for l in model.Lehrer) - sum(model.x[GleichzeitigFach(f),k,l,z] for l in model.Lehrer)
    return gleichzeitig(f,k,z) == 0
# erstelle Constraint
paralleleFaecher = Constraint(model.Faecher, model.Klassen, model.Zeitslots, rule=GleichzeitigRule)


# Es darf nur ein Unterricht pro stunde pro klasse stattfinden, außer für geteilte Fächer

# parallele und geteilte fächer müssen zusammen stattfinden

# Ein lehrer darf nur einen Unterricht geben, außer bei übergreifenden fächern

# Übergreifende Fächer müsssen zusammen stattfinden

# Übergreifende Fächer brauchen auch den gleichen Lehrer

# Jede Klasse muss ihren Lehrplan erfüllen
def LehrplanRule(model):
    

# Tandemlehrer muss anwesend sein wenn gefordert
def TandemRule(model):
    for k in model.Klassen, z in model.Zeitslots:
        Tandem1(k,z) = sum(model.x[k,l,"Tandem",z] for l  in model.Lehrer)
        Tandem2(k,z) = sum(Tandemnummer(f,k) * model.x[k,l,f,t] for f in model.Faecher, l in model.Lehrer, t in  max(1, Range(z+1-Fachdauer(f), z+1)))
    return Tandem1(k,z) == Tandem2(k,z)
# erstelle Constraint
Tandembenoetigt = Constraint(model.Klassen, model.Zeitslots, rule=TandemRule)
