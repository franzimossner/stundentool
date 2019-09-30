'''Hier wird das Modell gespeichert

Aus den anderen Teilen werden die Modelle und Parameter importiert und zu einem Modell zusammen gefügt.
Im Main-Skript wird diese Datei dann an die Solver gechickt, der dann das X_res file produziert, das dann verarbeitet wird
'''


'''Import von allen nötigen Modellklassen und von pyomo
'''
#from __future__ import division
from pyomo.environ import *
import cProfile
import time
import datetime

#import von Django Model Klassen
from datainput.models import Raum, Lehrer, Schulklasse, Schulfach, Lehrfaecher, Unterrricht, Tag, Stunde, Slot, Partner, LehrerBelegt, RaumBelegt, VorgabeEinheit, Uebergreifung, LehrerBelegt, StundenzahlproTag
from optimierung.models import Parameters

def createModel():

    '''Initialisierung des Problems
    '''
    # wir deklarieren ein abstraktes Modell, weil wir sich ändernde Daten haben
    model = ConcreteModel()

    '''Deklaration von Funktionen
    '''

    # Setze eine Klasse auf, die alle Datenbankzugriffe macht und auf die man dann später zugreifen kann.

    class Datenbankzugriff():
        '''Diese Klasse speichert alle Datenbankzugriffe auf Django, damit sie nicht bereits beim migrate ausgeführt werden, sondern erst beim import
        Nur die model.??? sollen hier gespeichert werden
        '''
        __instance = None
        @staticmethod
        def getInstance():
            if Datenbankzugriff.__instance == None:
                Datenbankzugriff()
            return Datenbankzugriff.__instance
        def __init__(self):
            #--borg-code--
            if Datenbankzugriff.__instance != None:
                raise Exception("Datenbankzugriff wurde bereits erstellt")
            else:
                self.Lehrermenge = Lehrer.objects.order_by('Kurzname')
                self.zahlLehrer = Lehrer.objects.all().count()
                self.Klassenmenge = Schulklasse.objects.order_by('Name')
                self.zahlKlassen = Schulklasse.objects.all().count()
                self.zahlRaum = Raum.objects.all().count()
                self.Raummenge = Raum.objects.order_by('Name')
                self.zahlslots = Slot.objects.all().count()
                self.Schulfachmenge = Schulfach.objects.order_by('Name')
                self.Vorgaben = VorgabeEinheit.objects.order_by('Schulklasse')
                self.parameterset = Parameters.objects.order_by('lehrerinKlasse').first()
                self.LehrerBelegtMenge = LehrerBelegt.objects.order_by('lehrer')
                self.Tage = Tag.objects.order_by('Index')

                Datenbankzugriff.__instance = self

    # erstelle das Objekt für die zukünftige NUtzung
    Datenbank = Datenbankzugriff.getInstance()


    def Klassleitung(klasse):
        # gibt die Klassleitung einer Klasse zurück
        klasse = Schulklasse.objects.get(Name=klasse)
        klassleitung = [klasse.Klassenlehrer.Kurzname]
        return klassleitung

    def Haupttandem(klasse):
        # gibt den Haupttandem einer Klasse zurück
        klasse = Schulklasse.objects.get(Name=klasse)
        haupttandem = [klasse.HauptTandem.Kurzname]
        return haupttandem

    def Partnerlehrer(klasse):
        # gibt eine Liste an Partnerlehrern der Klasse zurück
        Klasse = Schulklasse.objects.get(Name=klasse)
        partnerlehrer = Klasse.partner_set.all()
        lehrerliste = []
        for partner in partnerlehrer:
            lehrerliste.append(partner.lehrer.Kurzname)
        return lehrerliste


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
        Klasse =  Schulklasse.objects.get(Name=klasse)
        Fach = Schulfach.objects.get(Name=fach)
        if Lehrfaecher.objects.filter(schulklasse=Klasse, schulfach=Fach).exists():
            schulfach = Lehrfaecher.objects.get(schulklasse=Klasse, schulfach=Fach)
            fachdauer = schulfach.blockstunden
            return fachdauer
        else:
            return 0

    def Uebergreifend(fach, klasse):
        # gibt alle fächer zurück die zu diesem Fach in der Klasse übergeifend sind, und sich slebst
        # außerdem getUebergreifend = len( Uebergeifernd)
        schulfach = Schulfach.objects.get(Name=fach)
        schulklasse = Schulklasse.objects.get(Name=klasse)

        uebergreifend = Uebergreifung.objects.filter(fach=schulfach, schulklasse=schulklasse)
        liste = []
        for group in uebergreifend:
            liste.append(klasse.Name for klasse in group.schulklasse.all())
        if liste == []:
            liste.append(schulklasse.Name)
        return liste

    def Arbeitszeit(lehrer):
        # gibt die Arbeitszeit in Stunden für den Lehrer zurück
        lehrperson = Lehrer.objects.get(Kurzname=lehrer)
        stundenzahl = lehrperson.Stundenzahl
        return stundenzahl

    def GleichzeitigFach(fach):
        # gibt zurück, ob das Fach parallel Fächer hat udn wenn ja, eine Liste dieser
        fach = Schulfach.objects.get(Name=fach)
        faecher = Schulfach.objects.all()
        #parallelfaecher=[fach.Name]
        parallelfaecher=[]
        for parfach in faecher:
            if parfach.Parallel == fach:
                parallelfaecher.append(parfach.Name)
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
        # gibt zurück, ob der Raum zu dem Zeitpunkt verfügbar Ist
        # hole alle Räume mit diesem Fach und prüfe dann wie viele frei sind, da es keine Überschneidungen gibt
        raum = Raum.objects.get(Name=raum)
        # alle Räume mit der gleichen Fächerkombination
        raumliste = Raum.objects.filter(faecher__id__in=raum.faecher.all())
        slotliste = convert_to_slot(zeitslot)
        Zeitslot = Slot.objects.get(Tag__Tag=slotliste[0], Stunde__Index=slotliste[1])

        raumverfuegbar = 0
        for ort in raumliste:
            if not RaumBelegt.objects.filter(raum=ort, slot=Zeitslot).exists():
                raumverfuegbar += 1
        return raumverfuegbar

    def RaumFaecher(raum):
        # gibt die Fächer eines Raumes zurück als Liste
        raumobj = Raum.objects.get(Name=raum)
        faecherliste = [fach.Name for fach in raumobj.faecher.all()]
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
        if Lehrfaecher.objects.get(schulklasse=schulklasse, schulfach=schulfach).exists():
            stundenzahl = Lehrfaecher.objects.get(schulklasse=schulklasse, schulfach=schulfach).wochenstunden
        else:
            stundenzahl = 0
        return stundenzahl

    def Klassenfaecher(klasse):
        # gibt zurück, welche Fächer dir Klasse hat
        schulklasse = Schulklasse.objects.get(Name=klasse)
        faecherliste = []
        for fach in schulklasse.lehrfaecher_set.all():
            faecherliste.append(fach.schulfach.Name)
        return faecherliste

    def TagAnfang(tag):
        # gibt für index von tag den index der ersten Stunde des tages zurück
        number = int(tag)

        if number == 1:
            anfang = 1
        if number == 2:
            anfang = 10
        if number == 3:
            anfang = 19
        if number == 4:
            anfang = 28
        if number == 5:
            anfang = 37

        return anfang

    def Klassenzeiten(klasse):
        # gibt alle Zeitslots zurück, an denen die klasse Unterricht hat
        # Liste mit klassenzeiten für return
        zeitenlist = []
        # Hole Klassenobjekt
        Klasse = Schulklasse.objects.get(Name=klasse)
        for tagobj in Datenbank.Tage:
            # für jeden Tag, berechne den TagAnfang
            taganfang = TagAnfang(tagobj.Index)
            # hole die Stundenzahl an diesem Taf aus Djang, das scheint korrekt zu funktionieren
            zahl = StundenzahlproTag.objects.get(tag=tagobj, schulklasse=Klasse).Stundenzahl
            # für jede stunde, baue den Slot und hänge an
            for index in range(taganfang, taganfang+zahl):
                zeitenlist.append(index)
        return zeitenlist

    def KlassenTagEnde(klasse):
        # gibt alle stundennummern zurück bei denen für diese Klasse ein Tag endet
        tagendelist =[]
        for tagobj in Datenbank.Tage:
            taganfang = TagAnfang(tagobj.Index)
            Klasse = Schulklasse.objects.get(Name=klasse)
            zahl = StundenzahlproTag.objects.get(tag=tagobj, schulklasse=Klasse).Stundenzahl
            tagende = taganfang + zahl -1
            tagendelist.append(tagende)
        return tagendelist


    '''Deklaration von Mengen

    Die Mengen im Modell enthalen keine Django Objekte, sondern nur deren Namen oder einen anderen Refernzwert. Mit objects.get() kann dann das echt Objekt geholt werden, um Werte abzufragen
    '''

    # Lehrer
    # get Lehrerzahl aus Django
    zahlLehrer = Datenbank.zahlLehrer
    #zahlLehrer = Lehrer.objects.all().count()
    # initialisiere Menge
    Lehrermenge = []
    for lehrer in Datenbank.Lehrermenge:
        Lehrermenge.append(lehrer.Kurzname)
    model.Lehrer = Set(initialize=Lehrermenge)

    # Klassen
    # get Klassenzahl aus Django
    zahlKlassen = Datenbank.zahlKlassen
    #zahlKlassen = Schulklasse.objects.all().count()
    # initialisiere Menge
    Klassenmenge = []
    for klasse in Datenbank.Klassenmenge:
        Klassenmenge.append(klasse.Name)
    model.Klassen = Set(initialize=Klassenmenge)

    # Räume
    # get raumzahl aus Django
    zahlraum = Datenbank.zahlRaum
    #zahlraum = Raum.objects.all().count()
    # initialisiere Menge
    Raummenge =[]
    for raum in Datenbank.Raummenge:
        Raummenge.append(raum.Name)
    model.Raeume = Set(initialize=Raummenge)

    # Zeitslots
    # get zahlslots aus Django
    zahlslots = Datenbank.zahlslots
    #zahlslots = Slot.objects.all().count()
    # initialisiere Menge
    model.Zeitslots = RangeSet(1, zahlslots)

    # Fächer
    Schulfachmenge = []
    for fach in Datenbank.Schulfachmenge:
        Schulfachmenge.append(fach.Name)
    model.Faecher = Set(initialize=Schulfachmenge)

    # Vorgaben
    Vorgabenmenge = []
    for vorgabe in Datenbank.Vorgaben:
        stundenindex = vorgabe.Zeitslot.Stunde.Index
        tagindex = vorgabe.Zeitslot.Tag.Index
        zeitnummer = slot_to_number(tagindex, stundenindex)
        if vorgabe.Lehrperson == None:
            Vorgabenmenge.append((vorgabe.Schulklasse.Name, vorgabe.Fach.Name, 0 , zeitnummer,))
        else:
            Vorgabenmenge.append((vorgabe.Schulklasse.Name, vorgabe.Fach.Name, vorgabe.Lehrperson.Kurzname, zeitnummer))
    model.Vorgaben = Set(dimen=4,initialize=Vorgabenmenge)


    '''Deklaration von Parametern
    '''

    # Deklariere optimierungsparameter aus den modellen, der Parameter solver wird erst im main-skript abgefragt und verwendet
    parameterset = Datenbank.parameterset
    #parameterset = Parameters.objects.order_by('lehrerinKlasse').first()
    model.lehrerinKlasseGewicht = Param(initialize=parameterset.lehrerinKlasse)
    model.tandeminKlasseGewicht = Param(initialize=parameterset.tandeminKlasse)
    model.partnerinKlasseGewicht = Param(initialize=parameterset.partnerinKlasse)
    model.lehrerwechselGewicht = Param(initialize=parameterset.lehrerwechsel)
    model.sportunterrichtGewicht = Param(initialize=parameterset.sportunterricht)
    model.lehrerminimumGewicht = Param(initialize=parameterset.lehrerminimum)

    # schreibe alle lehrer nicht da Paare in eine Menge:
    BelegtMenge = Datenbank.LehrerBelegtMenge
    LehrerBelegtListe = []
    for belegung in BelegtMenge:
        LehrerBelegtListe.append((belegung.lehrer.Kurzname, slot_to_number(belegung.slot.Tag.Index, belegung.slot.Stunde.Index)))

    model.LehrerNichtDa = Set(initialize=LehrerBelegtListe)

    # die zahl der parallelen Fächer in der größten Gruppe
    # aktuell nicht benutzt
    # faecher = Schulfach.objects.all()
    # lengths = []
    # for fach in faecher:
    #     parallelfaecher=[fach]
    #     for parfach in faecher:
    #         if parfach.Parallel == fach:
    #             parallelfaecher.append(parfach)
    #     lengths.append(len(parallelfaecher))
    # model.maxUebergreifungRange = max(lengths)


    '''Variablendeklaration
        Ziel: Kreiere nur Variablen, bei denen es möglich ist, dass sie den Wert 1 annehmen
    '''
    # deklariere die variable, boolean setzt es als 0/1 variable
    # die 4 Mengen sind die Indexmengen in dieser Reihenfolge
    # x ist die Hauptvariable, die später auch ausgewertet wird
    model.x = Var(model.Klassen, model.Lehrer, model.Faecher, model.Zeitslots, domain=Boolean)

    # Hilfsvariable für Lehrerzahl
    model.y = Var(model.Klassen, model.Lehrer, domain=Boolean)
    # Hilfsvariable für wechselzähler
    model.w = Var(model.Klassen, model.Lehrer, model.Zeitslots, domain=Boolean)
    # Hilfsvariable für sportunterricht
    model.p = Var(model.Klassen, model.Zeitslots, domain=Boolean)
    # Hilfsvariable für parallele und geteilte Fächer
    model.pds = Var(model.Klassen, model.Zeitslots, model.Faecher, domain=Boolean)

    # kreiere Variablenmenge von Variablen, die überhaupt den Wert 1 annehmen könnten

    # Fehlersuche:
    # Klassenmenge, Lehrermenge, zahlslots sind korrekt importiert
    # 135468 Variablen geprüft
    # 75691 aufgenommen
    # 11 Minuten gesamtlaufzeit mit Optimierung

    # Vermutung: Zu wenige Variablen werden aufgenommen in die Variablenmenge

    # Geschwindigkeit liegt an den Datenbankzugriffen
    def Variablenmenge(model):
        start = time.time()
        #pr = cProfile.Profile()
        #pr.enable()
        counter = 0
        Variablenmenge = []
        for k in Klassenmenge:
            print(counter)
            Unterrichtszeit = Klassenzeiten(k)
            Unterrichtsfaecher = Klassenfaecher(k)
            TagEndeListe = KlassenTagEnde(k)
            for l in Lehrermenge:
                Lehrerfaecher = Unterricht(l)
                for z in range(1,zahlslots+1):
                    #print("Klasse {0}, Unterrichtszeit {1}".format(k,Unterrichtszeit))
                    if z in Unterrichtszeit:
                        for f in Lehrerfaecher:
                            testbestanden = 1
                            Fachlaenge = Fachdauer(f,k)
                            counter += 1
                            # wenn die Klasse das Fach gar nicht hat, ignoriere
                            if not f in Unterrichtsfaecher:
                                continue
                            # wenn das Fach länger als 1 Stunde ist müssen auch die Folgestunden zulässig sein
                            if Fachlaenge > 1:
                                for t in range(z+1, min(zahlslots + 1, z+Fachlaenge)):
                                    if not t in Unterrichtszeit or t-1 in TagEndeListe:
                                        testbestanden = 0
                                        break
                            # Kein Unterricht nach dem Ende der Woche
                            if z+ Fachlaenge -1 > zahlslots:
                                continue
                            # Wenn der Lehrer nicht da ist, dann kein Unterricht
                            if (l,z) in model.LehrerNichtDa:
                                continue
                            # Doppelstunden nicht über die Pause
                            if Fachlaenge > 1:
                                for tag in range(1,6):
                                    TagBeginn = TagAnfang(tag)
                                    for i in range(1,4):
                                        if z== TagBeginn + 2*i-1:
                                            testbestanden = 0
                                            break
                            if testbestanden == 1:
                                Variablenmenge.append((k,l,f,z))
        print(len(Variablenmenge))
        ende = time.time()
        wert = str(datetime.timedelta(seconds=ende - start))
        print(wert)
        #pr.disable()
        #pr.dump_stats("profiling2.txt")
        return Variablenmenge


    # initialize Variablenmenge
    model.Variablenmenge = Set(initialize=Variablenmenge(model))

    '''Objective Function
        Sie besteht aus allen softconstraints mit den Gewichten (Parametern)
    '''

    def ObjRule(model):
        # Gewicht * Summe über alle klassen, deren Klassleitungen, deren Unterrichtsfächer und alle Zeitslot mit dem wert der Variable und der Fachdauer
        # Belohne jedes Ereignis, in dem der Klassleiter in seiner Klasse ist
        lehrerKlasse = model.lehrerinKlasseGewicht * sum(model.x[k,l,f,z] * Fachdauer(f,k) for k in model.Klassen for l in Klassleitung(k)[0] for f in Unterricht(Klassleitung(k)[0]) for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge)
        print("Lehrer in Klasse berechnet")
        #Gewicht * Summer über alle Klassen, deren HauptTandem, deren Fächer und allen Zeitslots mit dem Wert der Variable und der Fachdauer
        #Belohne jedes Ereignis, in dem der HauptTandemin der Klasse ist
        tandemKlasse = model.tandeminKlasseGewicht * sum(model.x[k,l,f,z] * Fachdauer(f,k) for k in model.Klassen for l in Haupttandem(k)[0] for f in Unterricht(Haupttandem(k)[0]) for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge)
        print("Tandem in Klasse berechnet")
        #Belohne jedes Ereignis, bei dem ein Partnerlehrer in der Klasse ist
        partnerKlasse = 0
        for k in model.Klassen:
            for pl in Partnerlehrer(k):
                partnerKlasse += model.partnerinKlasseGewicht * sum(model.x[k,pl,f,z] * Fachdauer(f,k) for k in model.Klassen for f in Unterricht(pl) for z in model.Zeitslots if (k,pl,f,z) in model.Variablenmenge)
        print("Partner in Klasse berechnet")
        #Belohne, wenn es weniger Lehrerwechsel im Tagesablauf gibt
        wechsel = model.lehrerwechselGewicht * sum(model.w[k,l,z] * 0.5 for k in model.Klassen for l in model.Lehrer for z in model.Zeitslots)
        print("Wechsel berechnet")
        #Belohne, wenn Mädchen und Jungen der Klasse gleichzeitig Sport haben
        sport = model.sportunterrichtGewicht * sum(model.p[k,z] for k in model.Klassen for z in model.Zeitslots)
        print("Sport berechnet")
        #Belohne, wenn wenige Lehrer insgesamt die Klasse unterrichten
        lehrermin = model.lehrerminimumGewicht * sum(model.y[k,l] for k in model.Klassen for l in model.Lehrer)
        print("Lehrermin berechnet")
        #Setze alles zu einer Zielfunktion zusammen
        objective = lehrerKlasse + tandemKlasse + partnerKlasse - wechsel + sport - lehrermin
        #objective = lehrerKlasse
        print("Objective eingelesen")
        return objective

    # Set objective
    model.Obj = pyomo.environ.Objective(rule=ObjRule, sense=maximize)


    ''' Deklaration von Constraints
    '''
    # Lehrer müsssen in ihrer Arbeitszeit bleiben
    '''Stimmt mit Model überein'''
    '''Ohne Fehlermeldung einlesbar'''
    def ArbeitszeitRule(model,l):
        maxArbeit = sum(model.x[k,l,f,z] * Fachdauer(f,k)/len(Uebergreifend(f,k)) for k in model.Klassen for f in model.Faecher for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge)
        constraint =  maxArbeit <= Arbeitszeit(l)
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    # erstelle indexierte Constraint
    model.maxArbeitszeit = Constraint(model.Lehrer, rule=ArbeitszeitRule)
    print("ArbeitszeitRule gelesen")

    # Vorgaben, sowohl mit als auch ohne Lehrer angegeben (If Clause)
    '''Stimmt mit Model überein'''
    '''Ohne Fehlermeldung einlesbar'''
    def VorgabeRule(model, klasse, fach, lehrer, zeitslot):
        if lehrer != 0:
            constraint = sum(model.x[klasse, lehrer, fach, z] for z in range(max(1,zeitslot+1-Fachdauer(fach,klasse)), zeitslot+1) if (klasse,lehrer,fach,z) in model.Variablenmenge) >= 1
        else:
            constraint = sum(model.x[klasse, l, fach, z] for l in model.Lehrer for z in range(max(1,zeitslot+1-Fachdauer(fach,klasse)), zeitslot+1)) >= 1
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    model.vorgabencheck = Constraint(model.Vorgaben, rule=VorgabeRule)
    print("VorgabenRule gelesen")

    # Räume müssen verfügbar sein
    '''Stimmt mit Model überein'''
    '''Leere Constraint für Küche, stunde 11/17 , vermutlich ist dort ein Raum verfügbar, aber die Varaiblen sind alle nicht in der Variablenmenge?'''
    def RaumRule(model,r,z):
        if RaumVerfuegbar(r,z) > 0:
            RaumNoetig = sum(model.x[k,l,f,t]/len(Uebergreifend(f,k)) for f in RaumFaecher(r) for l in model.Lehrer for k in model.Klassen for t in range(max(1,z+1-Fachdauer(f,k)), z+1) if (k,l,f,t) in model.Variablenmenge)
            constraint = RaumNoetig <= RaumVerfuegbar(r,z)
            if isinstance(constraint, Constraint):
                return constraint
            else:
                return Constraint.Feasible
        return Constraint.Feasible
    # erstelle Constraints
    model.Raumverfuegbarkeit = Constraint(model.Raeume, model.Zeitslots, rule=RaumRule)
    print("RaumRule gelesen")

    # Es darf nur ein Unterricht pro stunde pro klasse stattfinden, außer für geteilte Fächer
    # auch mit andersrum überprüfen pyomo.core.base.constraint.indexedConstraint oder ähnlich
    # oder auch nach Constraint (ohne alles)
    '''Stimmt mit Model überein'''
    def NureinUnterrichtRule(model,k,z):
        # erstelle die SumExpression
        maxUnterricht = sum(model.x[k,l,f,t]/GeteilteFaecher(f,k) for f in model.Faecher if f != "Tandem" for l in model.Lehrer for t in range(max(1,z+1-Fachdauer(f,k)), z+1) if (k,l,f,t) in model.Variablenmenge)
        #stelle constraint auf
        constraint = maxUnterricht <= 1
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    # erstelle Constraint
    model.NureinUnterricht = Constraint(model.Klassen, model.Zeitslots, rule=NureinUnterrichtRule)
    print("NureinUnterrichtRule Klassen gelesen")

    # parallele und geteilte fächer müssen zusammen stattfinden
    # '''Stimmt mit Model überein, aber die Funktion ParallelGeteilt ist noch unklar'''
    # def ParallelundgeteiltRule(model,f,k,z):
    #     # ParellelGeteilt(f,k) muss also alle fächer zurückgeben, die parallel zu dem Fach sind und geteilt sind?
    #     if f in ParallelGeteilt(f,k):
    #         wert = sum(model.x[k,l,f,z]/GeteilteFaecher(f,k) for l in model.Lehrer if (k,l,f,z) in model.Variablenmenge)
    #         return wert == model.pds[k,z,f]
    #     else:
    #         return Constraint.Feasible
    # model.Parallelundgeteilt = Constraint(model.Faecher, model.Klassen, model.Zeitslots, rule=ParallelundgeteiltRule)
    # print("ParallelundgeteiltRule eingelesen")

    # Ein lehrer darf nur einen Unterricht geben, außer bei übergreifenden fächern
    '''stimmt mit Model überein'''
    def lehrernureinUnterrichtRule(model,l,z):
        ohneCCS = sum(model.x[k,l,f,t] for k in model.Klassen for f in Unterricht(l) for t in range(max(1,z+1-Fachdauer(f,k)), z+1) if len(Uebergreifend(f,k)) == 1 if (k,l,f,t) in model.Variablenmenge)
        mitCCS = sum(sum(model.x[c,l,f,t] for c in Uebergreifend(f,k))/len(Uebergreifend(f,k)) for k in model.Klassen for f in Unterricht(l) for t in range(max(1,z+1-Fachdauer(f,k)), z+1) if len(Uebergreifend(f,k)) > 1 if (c,l,f,z) in model.Variablenmenge)
        constraint = ohneCCS + mitCCS <= 1
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    model.LehrerUnterricht = Constraint(model.Lehrer, model.Zeitslots, rule=lehrernureinUnterrichtRule)
    print("lehrernureinUnterrichtRule gelesen")

    # Übergreifende Fächer müssen gleichzeitig stattfinden
    '''Nicht komplett gleich, weil die Summe mehrer Restriktionen ersetzt wie bei parallenzusammen'''
    def UebergreifendRule(model,f,k,z):
        if len(Uebergreifend(f,k)) > 1:
            uebergreifendsumme = 0
            for klasse in Uebergreifend(f,k) and klasse != k:
                uebergreifendsumme += sum(model.x[k,l,f,z] for l in model.Lehrer and (k,l,f,z) in model.Variablenmenge) - sum(model.x[klasse,l,f,z] for l in model.Lehrer if (klasse,l,f,z) in model.Variablenmenge)
            return uebergreifendsumme == 0
        else:
            return Constraint.Feasible
    model.Uebergreifend = Constraint(model.Faecher, model.Klassen, model.Zeitslots, rule=UebergreifendRule)

    # Übergreifende Fächer brauchen auch den gleichen Lehrer
    '''Auch hier eine extra Summe, eventuell mit Index arbeiten '''
    def UebergreifendgleicherLehrerRule(model,f,l,z,k):
        if len(Uebergreifend(f,k)) > 1:
            lehrersumme = 0
            for klasse in Uebergreifend(f,k) and klasse != k and (klasse,l,f,z) in model.Variablenmenge:
                lehrersumme += model.x[k,l,f,z] - model.x[klasse,l,f,z]
            return lehrersumme == 0
        else:
            return Constraint.Feasible
    model.UebergreifendgleicherLehrer = Constraint(model.Faecher, model.Lehrer, model.Zeitslots, model.Klassen, rule=UebergreifendgleicherLehrerRule)
    print("UebergreifendgleicherLehrertRule gelesen")

    # Parallele Fächer müsssen gleichzeitig stattfinden
    '''Nicht komplett wie im Modell, da hier mit zusätzlicher summe, also nochmal prüfen'''
    def ParallelzusammenRule(model,f,k,z):
        if GleichzeitigFach(f) != []:
            parallelsumme = 0
            for parfach in GleichzeitigFach(f):
                parallelsumme += sum(model.x[k,l,f,z] for l in model.Lehrer if (k,l,f,z) in model.Variablenmenge) - sum(model.x[k,l,parfach,z] for l in model.Lehrer if (k,l,parfach,z) in model.Variablenmenge)
            constraint = parallelsumme == 0
        else:
            constraint = Constraint.Feasible
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    model.Parallelzusammen = Constraint(model.Faecher, model.Klassen, model.Zeitslots, rule=ParallelzusammenRule)
    print("ParallelzusammenRule gelesen")

    # Jede Klasse muss ihren Lehrplan erfüllen
    '''Stimmt mit Model überein'''
    def LehrplanRule(model,f,k):
        mindestUnterricht = sum(model.x[k,l,f,z] * Fachdauer(f,k)/GeteilteFaecher(f,k) for l in model.Lehrer for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge)
        constraint = mindestUnterricht >= Lehrplanstunden(f,k)
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    model.Lehrplanerfuellt = Constraint(model.Faecher, model.Klassen, rule=LehrplanRule)
    print("LehrplanRule gelesen")

    # Tandemlehrer muss anwesend sein wenn gefordert
    '''Stimmt mit Model überein'''
    def TandemRule(model,k,z):
        Tandem1 = sum(model.x[k,l,"Tandem",z] for l  in model.Lehrer if (k,l,"Tandem",z) in model.Variablenmenge)
        Tandem2 = sum(Tandemnummer(f,k) * model.x[k,l,f,t] for f in model.Faecher for l in model.Lehrer for t in range(max(1,z+1-Fachdauer(f,k)), z+1) if (k,l,f,t) in model.Variablenmenge)
        constraint = Tandem1 == Tandem2
        if isinstance(constraint, Constraint):
            return constraint
        else:
            return Constraint.Feasible
    # erstelle Constraint
    model.Tandembenoetigt = Constraint(model.Klassen, model.Zeitslots, rule=TandemRule)
    print("TandemRule gelesen")


    '''Constraints für auxiliary variables
    '''

    # Restriktion für Variable y:
    '''Wie im Model'''
    ''' ToDo: Funktion für intelligente Arbeitszeit schreiben'''
    def auxiliaryYRule(model,k,l):
        return sum(model.x[k,l,f,z] * Fachdauer(f,k)/GeteilteFaecher(f,k) for f in Unterricht(l) for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge) <= model.y[k,l] * Arbeitszeit(l)

    model.auxilaryY = Constraint(model.Klassen, model.Lehrer, rule=auxiliaryYRule)
    print("auxiliaryYRule eingelesen")

    # Restriktion für Variable w
    '''Stimmt mit Model überein'''
    def auxiliaryWRule(model,k,l,z):
        return sum(model.x[k,l,f,t] for f in Klassenfaecher(k) for t in range(max(1,z+1-Fachdauer(f,k)), z+1) if (k,l,f,t) in model.Variablenmenge) - sum(model.x[k,l,g,t+1] for g in Klassenfaecher(k) for t in range(max(1,z+1-Fachdauer(f,k))) if (k,l,g,t+1) in model.Variablenmenge) <= model.w[k,l,z]

    model.auxiliaryW = Constraint(model.Klassen, model.Lehrer, model.Zeitslots, rule=auxiliaryWRule)
    print("auxiliaryWRule eingelesen")

    # Restriktion für Variable p
    '''Stimmt mit Model überein '''
    def auxiliaryPRule1(model,k,z):
        return sum(model.x[k,l,"SportM",z] for l in model.Lehrer and (k,l,"SportM",z) in model.Variablenmenge) - sum(model.x[k,l,"SportW",z] for l in model.Lehrer if(k,l,"SportW",z) in model.Variablenmenge) <= model.p[k,z]

    model.auxiliaryP1 = Constraint(model.Klassen, model.Zeitslots, rule=auxiliaryPRule1)
    print("auxiliaryPRule1 eingelesen")

    '''Stimmt mit Model überein '''
    def auxiliaryPRule2(model,k,z):
        return sum(model.x[k,l,"SportW",z] for l in model.Lehrer and (k,l,"SportW",z) in model.Variablenmenge) - sum(model.x[k,l,"SportM",z] for l in model.Lehrer if (k,l,"SportM",z) in model.Variablenmenge) <= model.p[k,z]

    model.auxiliaryP2 = Constraint(model.Klassen, model.Zeitslots, rule=auxiliaryPRule2)
    print("auxiliaryPRule2 eingelesen")

    return model
