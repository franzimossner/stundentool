'''Hier wird das Modell gespeichert

Aus den anderen Teilen werden die Modelle und Parameter importiert und zu einem Modell zusammen gefügt.
Im Main-Skript wird diese Datei dann an die Solver gechickt, der dann das X_res file produziert, das dann verarbeitet wird
'''
import xpress as xp
import math



'''Import von allen nötigen Modellklassen
'''
from datainput.models import Schulklasse, Lehrer, Raum, Schulfach, Lehrfaecher, Lehreinheit, VorgabeEinheit, Partner, Uebergreifung, RaumBelegt, LehrerBelegt, Unterricht, Nutzbar, Slot, Tag, Stunde, StundenzahlproTag
from optimierung import parameters

Klassen = Schulklasse.objects.order_by('Name')
Lehrer = Lehrer.objects.order_by('Name')
Raeume = Raum.objects.order_by('Name')
Schulfaecher = Schulfach.objects.order_by('Name')

Tage = Tag.objects.order_by('Index')
Stunden = Stunde.objects.order_by('Index')
Slots = Slot.objects.all()

Zeitslots = []
for slot in Slots:
    if slot.Tag.Index == 1:
        slotnumber = slot.Stunde.Index
    elif slot.Tag.Index == 2:
        slotnumber = 9 + slot.Stunde.Index
    elif slot.Tag.Index == 3:
        slotnumber = 18 + slot.Stunde.Index
    elif slot.Tag.Index == 4:
        slotnumber = 27 + slot.Stunde.Index
    elif slot.Tag.Index == 5:
        slotnumber = 36 slot.Stunde.Index
    Zeitslots.append(slotnumber)

Vorgaben = VorgabeEinheit.objects.all()
Lehrfaecher = Lehrfaecher.objects.all()
Partners = Partner.objects.all()
Uebergreifungen = Uebergreifung.objects.all()


'''Initialisierung des Problems
'''
# eröffne leeres Optimierungsproblem und gib ihm einen Namen
myproblem = xp.problem(name = "Stundenplanoptimierung")


'''Variablendeklaration
    Ziel: Kreiere nur Variablen, bei denen es möglich ist, dass sie den Wert 1 annehmen
'''
for k in Klassen, l in Lehrer, z in Zeitslots:
    # betrachte nur  fächer, die der Lehrer auch unterichten kann:
    for f in l.unterricht_set.all():
        # betrachte nur fächer, die die Klasse auch hat
        if not f in k.lehrfaecher_set.all():
            next
        else:
            var = xp.var(x(f,k,l,z), vartype=xpress.binary)
            m.addVariable(var)


'''Objective Function
    Sie besteht aus allen softconstraints mit ihren Gewichten
'''
# funktion, die prüft, ob Mädchen und Jungs zusmamen Sport haben
def sportpruefer(klasse, zeitslot):
    sport = sum(l in Lehrer for x("SportM",k,l,z).exists()) x("SportM",k,l,z) + sum(l in Lehrer for x("SportW",k,l,z).exists()) x("SportW",k,l,z)
    if sport % 2 > 0:
        return 0
    else:
        return 1

# funktion, die ausrechnen kann, wie viele Wechsel eine Klasse hat
def wechselpruefer(klasse, lehrer, zeitslot):
    wl = sum(f in Schulfaecher) sum(t in range(max(1,z+1 - klasse.lehrfaecher_set.filter(schulfach=f), len(Zeitslots) + 1))) x(f,klasse,lehrer,t)
        + sum(g in Schulfaecher) x(g,klasse,lehrer,zeitslot + 1)
    if wl % 2 > 0:
        return 1
    else:
        return 0

# Klassenlehrer nur in seiner Klasse
objectiveValue = 0
# Welche Art der Summation ist die richtige? Warum ist die Farbgebung anders als bei dem anderen Python code?
objectiveValue = xp.Sum(k in Klassen, f in k.Klassenlehrer.unterricht_set.all(), z in Zeitslots) x(f,k,k.Klassenlehrer,z)*k,lehrfaecher_set.filter(schulfach=f).blockstunden
for k in Klassen, f in k.Klassenlehrer.unterricht_set.all(), z in Zeitslots:
    objectiveValue += x(f,k,k.Klassenlehrer,z)* k.lehrfaecher_set.filter(schulfach=f).blockstunden
objective1 = lehrerinklasse * objectiveValue

# tandemlehrer nur in seiner Klasse
objectiveValue = 0
objectiveValue = xp.Sum(k in Klassen, f in k.HauptTandem.unterricht_set.all(), z in Zeitslots) x(f,k,k.HauptTandem,z) * k.lehrfaecher_set.filter(schulfach=f).blockstunden
for k in Klassen, f in k.HauptTandem.unterricht_set.all(), z in Zeitslots:
    objectiveValue += x(f,k,k.HauptTandem, z) * k.lehrfaecher_set.filter(schulfach=f).blockstunden
objective2 = tandeminklasse * objectiveValue

# Partnerlerher am leibsten in ihrer Klasse
objectiveValue = 0
for k in Klassen, pl in k.partner_set.all():
    for f in pl.unterricht_set.all(), z in Zeitslots:
        objectiveValue += x(f,k,pl,z) * k.lehrfaecher_set.filter(schulfach=f).blockstunden
objective3 = partnerinklasse * objectiveValue

# Minimiere die Zahl der Wechsel in der Klasse
objective4 = lehrerwechsel * sum(k in Klassen, l in Lehrer, z in Zeitslots) wechselpruefer(k,l,z)*0,5

# Belohne, wenn Sport bei Mädchen und Jungen zusammen stattfindet
objective5 = sportunterricht * sum(k in Klassen, z in Zeitslots) sportpruefer(k,z)

# Minimiere Zahl der lehrer pro Klasse
# Dazu: Kreiere variable, die anzeigt, ob der lehrer in der gegebenen Klasse unterrichtet
for k in Klassen, l in Lehrer:
    var = xp.var(y(k,l),vartype=xpress.binary)
    m.addVariable(var)

objective6 = lehrerminimum * sum(k in Klassen, l in Lehrer) y(k,l)

# Setze die Objective Funktion in dem Model
objective = objective1 + objective2 + objective3 - objective4 + objective5 -objective6
setObjective(objective , sense=xp.maximize)
