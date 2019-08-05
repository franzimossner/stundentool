'''Hier wird das Modell gespeichert

Aus den anderen Teilen werden die Modelle und Parameter importiert und zu einem Modell zusammen gefügt.
Im Main-Skript wird diese Datei dann an die Solver gechickt, der dann das X_res file produziert, das dann verarbeitet wird
'''


''' Content of a pyomo model
Set: data set to define model instance
Param: parameter data
Var: descision variables
objective: minimizing or maximizing function
constraint: constraints

Here we will probably use abstract models since we have parameters and cosntraints depending on the size od some sets
'''


'''Import von allen nötigen Modellklassen und vom pyomo
'''
from __future__ import division
from pyomo.environ import *

#import von Django Model Klassen
from datainput.models import Raum, Lehrer, Schulklasse, Schulfach, Lehrfaecher, Unterrricht, Tag, Stunde, Zeitslot, Partner, LehrerBelegt, RaumBelegt


'''Initialisierung des Problems
'''
# wir deklarieren ein abstraktes Modell, weil wir sich ändernde Daten haben
model = AbstractModel()

'''Deklaration von Mengen
'''

# Lehrer
# get Lehrerzahl aus Django
zahlLehrer = Lehrer.objects.all().count()
# initialisiere Menge
model.Lehrer = Set(dimen=zahlLehrer)

# Klassen
# get Klassenzahl aus Django
zahlKlassen = Schulklasse.objects.all().count()
# initialisiere Menge
model.Klassen = Set(dimen=zahlKlassen)

# Räume
# get raumzahl aus Django
zahlraum = Raum.objects.all().count()
# initialisiere Menge
model.Raeume = Set(dimen=zahlraums)

# Zeitslots
# get zahlslots aus Django
zahlslots = Zeitslot.objects.all().count()
# initialisiere Menge
model.Zeitslots = Set(dimen=zahlslots)

# Fächer
model.Faecher = Set()


'''Deklaration von Parametern
'''

# Deklariere optimierungsparameter aus den modellen, der Parameter solver wird erst im main-skript abgefragt und verwendet
model.lehrerinKlasseGewicht = Param()
model.tandeminKlasseGewicht = Param()
model.partnerinKlasseGewicht = Param()
model.lehrerwechselGewicht = Param()
model.sportunterrichtGewicht = Param()
model.lehrerminimumGewicht = Param()


'''Variablendeklaration
    Ziel: Kreiere nur Variablen, bei denen es möglich ist, dass sie den Wert 1 annehmen
'''
# deklariere die variable, boolean setzt es als 0/1 variable
model.var = Var(model.Klassen, model.Lehrer, model.Zeitslots, model.Faecher, domain=Boolean)

'''Objective Function
    Sie besteht aus allen softconstraints mit den Gewichten (Parametern)
'''
