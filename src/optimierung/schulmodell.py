"""Hier wird das Modell gespeichert

Aus den anderen Teilen werden die Modelle und Parameter importiert und zu einem Modell zusammen gefügt.
Im Main-Skript wird diese Datei dann an die Solver gechickt, der dann das X_res file produziert, das dann verarbeitet wird
"""


"""Import von allen nötigen Modellklassen und von pyomo
"""
# from __future__ import division
from pyomo.environ import *
import cProfile
import time
import datetime

# import von Django Model Klassen
from datainput.models import (
    Raum,
    Lehrer,
    Schulklasse,
    Schulfach,
    Lehrfaecher,
    Unterrricht,
    Tag,
    Stunde,
    Slot,
    Partner,
    LehrerBelegt,
    RaumBelegt,
    VorgabeEinheit,
    Uebergreifung,
    LehrerBelegt,
    StundenzahlproTag,
)
from optimierung.models import Parameters


def createModel():

    def constraint_or_feasible(ctr):
        if isinstance(ctr, pyomo.core.expr.logical_expr.InequalityExpression) or isinstance(ctr, pyomo.core.expr.logical_expr.EqualityExpression):
            return ctr
        else:
            return Constraint.Feasible

    """Initialisierung des Problems
    """
    # wir deklarieren ein abstraktes Modell, weil wir sich ändernde Daten haben
    model = ConcreteModel()

    """Deklaration von Funktionen
    """

    # Setze eine Klasse auf, die alle Datenbankzugriffe macht und auf die man dann später zugreifen kann.

    class Datenbankzugriff:
        """Diese Klasse speichert alle Datenbankzugriffe auf Django, damit sie nicht bereits beim migrate ausgeführt werden, sondern erst beim import
        Nur die model.??? sollen hier gespeichert werden
        """

        __instance = None

        @staticmethod
        def getInstance():
            if Datenbankzugriff.__instance == None:
                Datenbankzugriff()
            return Datenbankzugriff.__instance

        def __init__(self):
            # --borg-code--
            if Datenbankzugriff.__instance != None:
                raise Exception("Datenbankzugriff wurde bereits erstellt")
            else:
                self.Lehrermenge = Lehrer.objects.order_by("Kurzname")
                self.zahlLehrer = Lehrer.objects.all().count()
                self.Klassenmenge = Schulklasse.objects.order_by("Name")
                self.zahlKlassen = Schulklasse.objects.all().count()
                self.zahlRaum = Raum.objects.all().count()
                self.Raummenge = Raum.objects.order_by("Name")
                self.zahlslots = Slot.objects.all().count()
                self.Schulfachmenge = Schulfach.objects.order_by("Name")
                self.Vorgaben = VorgabeEinheit.objects.order_by("Schulklasse")
                self.parameterset = Parameters.objects.order_by(
                    "lehrerinKlasse"
                ).first()
                self.LehrerBelegtMenge = LehrerBelegt.objects.order_by("lehrer")
                self.Tage = Tag.objects.order_by("Index")

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
        lehrerliste = [partner.lehrer.Kurzname for partner in Klasse.partner_set.all()]
        return lehrerliste

    def Unterricht(lehrer):
        # gibt alle Fächer zurück, die der Lehrer unterrichtet
        lehrperson = Lehrer.objects.get(Kurzname=lehrer)
        faecherliste = [fach.Name for fach in lehrperson.Faecher.all()]
        return faecherliste

    def Fachdauerkombinationen():
        FachdauerFuerFachUndKlasse = {}
        for klasse in Datenbank.Klassenmenge:
            # fidne für jedes Fach die Fachdauer und bau es ein
            FachdauerFuerFachUndKlasse[klasse.Name] = {}
            for fach in Datenbank.Schulfachmenge:
                try:
                    FachdauerFuerFachUndKlasse[klasse.Name][
                        fach.Name
                    ] = Lehrfaecher.objects.get(
                        schulklasse=klasse, schulfach=fach
                    ).blockstunden
                except Lehrfaecher.DoesNotExist:
                    FachdauerFuerFachUndKlasse[klasse.Name][fach.Name] = 0
        return FachdauerFuerFachUndKlasse

    Fachdauerliste = Fachdauerkombinationen()

    def Fachdauer(fach, klasse):
        # gibt die Fachdauer für das Fach in dieser Klasse aus. Falls die Klasse das Fach nicht hat, gibt es 0 zurück
        fachdauer = Fachdauerliste[klasse][fach]
        return fachdauer
        # gibt zurück, wie lange das Fach in der Klasse dauert
        # try:
        #     fachdauer = Lehrfaecher.objects.get(schulklasse__Name=klasse, schulfach__Name=fach).blockstunden
        # except Lehrfaecher.DoesNotExist:
        #     fachdauer = 0
        # return fachdauer

    def Tandemnummer(fach, klasse):
        ''' Sollte eigentlich die Zahl der Tandemlehrer pro Stunde zurück geben'''
        # gibt für die Klasse die Zahl der benötigten Tandemlehrer aus pro Woche
        try:
            tandemnummer = Lehrfaecher.objects.get(
                schulklasse__Name=klasse, schulfach__Name=fach
            ).tandemstunden
        except Lehrfaecher.DoesNotExist:
            tandemnummer = 0
        return tandemnummer

    def uebergreifendeKombinationen():
        uebergreifendFuerFachUndKlasse = {}
        for uebergreifung in Uebergreifung.objects.all():
            if uebergreifung.fach.Name not in uebergreifendFuerFachUndKlasse:
                uebergreifendFuerFachUndKlasse[uebergreifung.fach.Name] = {}
            klassen = [k.Name for k in uebergreifung.schulklasse.all()]
            for klasse in klassen:
                uebergreifendFuerFachUndKlasse[uebergreifung.fach.Name][
                    klasse
                ] = klassen
        return uebergreifendFuerFachUndKlasse

    uebergreifendListe = uebergreifendeKombinationen()

    def Uebergreifend(f, k):
        if f in uebergreifendListe and k in uebergreifendListe[f]:
            return uebergreifendListe[f][k]
        else:
            return [k]

    def Arbeitszeit(lehrer):
        # gibt die Arbeitszeit in Stunden für den Lehrer zurück
        stundenzahl = Lehrer.objects.get(Kurzname=lehrer).Stundenzahl
        return stundenzahl

    def GleichzeitigFach(fach):
        # gibt zurück, ob das Fach parallel Fächer hat udn wenn ja, eine Liste dieser
        fach = Schulfach.objects.get(Name=fach)
        faecher = Schulfach.objects.all()
        # parallelfaecher=[fach.Name]
        parallelfaecher = []
        for parfach in faecher:
            if parfach.Parallel == fach:
                parallelfaecher.append(parfach.Name)
        return parallelfaecher

    def convert_to_slot(number):
        # converting given number from 1 to 40 to a slot in out model
        number = int(number)
        tag = ""
        stundenindex = 0

        if number in range(1, 10):
            tag = "Montag"
            stundenindex = range(1, 10).index(number) + 1
        if number in range(10, 19):
            tag = "Dienstag"
            stundenindex = range(10, 19).index(number) + 1
        if number in range(19, 28):
            tag = "Mittwoch"
            stundenindex = range(19, 28).index(number) + 1
        if number in range(28, 37):
            tag = "Donnerstag"
            stundenindex = range(28, 37).index(number) + 1
        if number in range(37, 41):
            tag = "Freitag"
            stundenindex = range(37, 41).index(number) + 1

        return [tag, stundenindex]

    def slot_to_number(tagindex, stundenindex):
        # wandelt einen Zeitslot mit indices in eine Nummer um, von 1 bis Ende der Woche
        number = (tagindex - 1) * 9
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

        raumverfuegbar = (
            len(raumliste)
            - RaumBelegt.objects.filter(raum__in=raumliste, slot=Zeitslot).count()
        )
        return raumverfuegbar

    def RaumFaecher(raum):
        # gibt die Fächer eines Raumes zurück als Liste
        raumobj = Raum.objects.get(Name=raum)
        faecherliste = [fach.Name for fach in raumobj.faecher.all()]
        return faecherliste

    def GeteilteFaecher(fach, klasse):
        # gibt zrück, in wie viele Gruppen die Klasse zu teilen ist
        gruppenzahl = Lehrfaecher.objects.get(
            schulklasse__Name=klasse, schulfach__Name=fach
        ).klassengruppen
        return gruppenzahl

    def Lehrplanstunden(fach, klasse):
        # gibt zurück, wie viele studnen die klasse in dem Fach machen muss
        try:
            stundenzahl = Lehrfaecher.objects.get(
                schulklasse__Name=klasse, schulfach__Name=fach
            ).wochenstunden
        except Lehrfaecher.DoesNotExist:
            stundenzahl = 0
        return stundenzahl

    def Klassenfaecher(klasse):
        # gibt zurück, welche Fächer dir Klasse hat
        schulklasse = Schulklasse.objects.get(Name=klasse)
        faecherliste = [
            fach.schulfach.Name for fach in schulklasse.lehrfaecher_set.all()
        ]
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
        zeitenlist = []
        for tagobj in Datenbank.Tage:
            # für jeden Tag, berechne den TagAnfang
            taganfang = TagAnfang(tagobj.Index)
            # hole die Stundenzahl an diesem Taf aus Djang, das scheint korrekt zu funktionieren
            zahl = StundenzahlproTag.objects.get(
                tag=tagobj, schulklasse__Name=klasse
            ).Stundenzahl
            # für jede stunde, baue den Slot und hänge an
            for index in range(taganfang, taganfang + zahl):
                zeitenlist.append(index)
        return zeitenlist

    def KlassenTagEnde(klasse):
        # gibt alle stundennummern zurück bei denen für diese Klasse ein Tag endet
        tagendelist = []
        for tagobj in Datenbank.Tage:
            taganfang = TagAnfang(tagobj.Index)
            Klasse = Schulklasse.objects.get(Name=klasse)
            zahl = StundenzahlproTag.objects.get(
                tag=tagobj, schulklasse=Klasse
            ).Stundenzahl
            tagende = taganfang + zahl - 1
            tagendelist.append(tagende)
        return tagendelist

    """Deklaration von Mengen

    Die Mengen im Modell enthalen keine Django Objekte, sondern nur deren Namen oder einen anderen Refernzwert. Mit objects.get() kann dann das echt Objekt geholt werden, um Werte abzufragen
    """

    # Lehrer
    # get Lehrerzahl aus Django
    zahlLehrer = Datenbank.zahlLehrer
    # initialisiere Menge
    Lehrermenge = []
    for lehrer in Datenbank.Lehrermenge:
        Lehrermenge.append(lehrer.Kurzname)
    model.Lehrer = Set(initialize=Lehrermenge)

    # Klassen
    # get Klassenzahl aus Django
    zahlKlassen = Datenbank.zahlKlassen
    # initialisiere Menge
    Klassenmenge = []
    for klasse in Datenbank.Klassenmenge:
        Klassenmenge.append(klasse.Name)
    model.Klassen = Set(initialize=Klassenmenge)

    # Räume
    # get raumzahl aus Django
    zahlraum = Datenbank.zahlRaum
    # initialisiere Menge
    Raummenge = []
    for raum in Datenbank.Raummenge:
        Raummenge.append(raum.Name)
    model.Raeume = Set(initialize=Raummenge)

    # Zeitslots
    # get zahlslots aus Django
    zahlslots = Datenbank.zahlslots
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
            Vorgabenmenge.append(
                (vorgabe.Schulklasse.Name, vorgabe.Fach.Name, 0, zeitnummer)
            )
        else:
            Vorgabenmenge.append(
                (
                    vorgabe.Schulklasse.Name,
                    vorgabe.Fach.Name,
                    vorgabe.Lehrperson.Kurzname,
                    zeitnummer,
                )
            )
    model.Vorgaben = Set(dimen=4, initialize=Vorgabenmenge)

    """Deklaration von Parametern
    """

    # Deklariere optimierungsparameter aus den modellen, der Parameter solver wird erst im main-skript abgefragt und verwendet
    parameterset = Datenbank.parameterset
    # parameterset = Parameters.objects.order_by('lehrerinKlasse').first()
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
        LehrerBelegtListe.append(
            (
                belegung.lehrer.Kurzname,
                slot_to_number(belegung.slot.Tag.Index, belegung.slot.Stunde.Index),
            )
        )

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

    """Variablendeklaration
        Ziel: Kreiere nur Variablen, bei denen es möglich ist, dass sie den Wert 1 annehmen
    """
    # deklariere die variable, boolean setzt es als 0/1 variable
    # die 4 Mengen sind die Indexmengen in dieser Reihenfolge
    # x ist die Hauptvariable, die später auch ausgewertet wird
    model.x = Var(
        model.Klassen, model.Lehrer, model.Faecher, model.Zeitslots, domain=Boolean
    )

    # Hilfsvariable für Lehrerzahl
    model.y = Var(model.Klassen, model.Lehrer, domain=Boolean)
    # Hilfsvariable für wechselzähler
    model.w = Var(model.Klassen, model.Lehrer, model.Zeitslots, domain=Boolean)
    # Hilfsvariable für sportunterricht
    model.p = Var(model.Klassen, model.Zeitslots, domain=Boolean)
    # Hilfsvariable für parallele und geteilte Fächer
    model.pds = Var(model.Klassen, model.Zeitslots, model.Faecher, domain=Boolean)

    # kreiere Variablenmenge von Variablen, die überhaupt den Wert 1 annehmen könnten
    # Geschwindigkeit liegt an den Datenbankzugriffen
    def Variablenmenge(model):
        # start = time.time()
        # pr = cProfile.Profile()
        # pr.enable()
        counter = 0
        Variablenmenge = []
        for k in model.Klassen:
            print(counter)
            Unterrichtszeit = Klassenzeiten(k)
            Unterrichtsfaecher = Klassenfaecher(k)
            TagEndeListe = KlassenTagEnde(k)
            for l in model.Lehrer:
                Lehrerfaecher = Unterricht(l)
                for z in model.Zeitslots:
                    # print("Klasse {0}, Unterrichtszeit {1}".format(k,Unterrichtszeit))
                    if z in Unterrichtszeit:
                        for f in Lehrerfaecher:
                            testbestanden = 1
                            Fachlaenge = Fachdauer(f, k)
                            counter += 1
                            # wenn die Klasse das Fach gar nicht hat, ignoriere
                            if not f in Unterrichtsfaecher:
                                continue
                            # wenn das Fach länger als 1 Stunde ist müssen auch die Folgestunden zulässig sein
                            if Fachlaenge > 1:
                                for t in range(
                                    z + 1, min(zahlslots + 1, z + Fachlaenge)
                                ):
                                    if (
                                        not t in Unterrichtszeit
                                        or t - 1 in TagEndeListe
                                    ):
                                        testbestanden = 0
                                        break
                            # Kein Unterricht nach dem Ende der Woche
                            if z + Fachlaenge - 1 > zahlslots:
                                continue
                            # Wenn der Lehrer nicht da ist, dann kein Unterricht
                            if (l, z) in model.LehrerNichtDa:
                                continue
                            # Doppelstunden nicht über die Pause
                            if Fachlaenge > 1:
                                for tag in range(1, 6):
                                    TagBeginn = TagAnfang(tag)
                                    for i in range(1, 4):
                                        if z == TagBeginn + 2 * i - 1:
                                            testbestanden = 0
                                            break
                            if testbestanden == 1:
                                Variablenmenge.append((k, l, f, z))
        # print(len(Variablenmenge))
        # ende = time.time()
        # wert = str(datetime.timedelta(seconds=ende - start))
        # print(wert)
        # pr.disable()
        # pr.dump_stats("profiling2.txt")
        return Variablenmenge

    # initialize Variablenmenge
    model.Variablenmenge = Set(initialize=Variablenmenge, dimen=4)

    """Objective Function
        Sie besteht aus allen softconstraints mit den Gewichten (Parametern)
    """

    def ObjRule(model):
        # Gewicht * Summe über alle klassen, deren Klassleitungen, deren Unterrichtsfächer und alle Zeitslot mit dem wert der Variable und der Fachdauer
        # Belohne jedes Ereignis, in dem der Klassleiter in seiner Klasse ist
        lehrerKlasse = model.lehrerinKlasseGewicht * sum(
            model.x[k, l, f, z] * Fachdauer(f, k)
            for k in model.Klassen
            for l in Klassleitung(k)[0]
            for f in Unterricht(Klassleitung(k)[0])
            for z in model.Zeitslots
            if (k, l, f, z) in model.Variablenmenge
        )
        print("Lehrer in Klasse berechnet")
        # Gewicht * Summer über alle Klassen, deren HauptTandem, deren Fächer und allen Zeitslots mit dem Wert der Variable und der Fachdauer
        # Belohne jedes Ereignis, in dem der HauptTandemin der Klasse ist
        tandemKlasse = model.tandeminKlasseGewicht * sum(
            model.x[k, l, f, z] * Fachdauer(f, k)
            for k in model.Klassen
            for l in Haupttandem(k)[0]
            for f in Unterricht(Haupttandem(k)[0])
            for z in model.Zeitslots
            if (k, l, f, z) in model.Variablenmenge
        )
        print("Tandem in Klasse berechnet")
        # Belohne jedes Ereignis, bei dem ein Partnerlehrer in der Klasse ist
        partnerKlasse = 0
        for k in model.Klassen:
            for pl in Partnerlehrer(k):
                partnerKlasse += model.partnerinKlasseGewicht * sum(
                    model.x[k, pl, f, z] * Fachdauer(f, k)
                    for k in model.Klassen
                    for f in Unterricht(pl)
                    for z in model.Zeitslots
                    if (k, pl, f, z) in model.Variablenmenge
                )
        print("Partner in Klasse berechnet")
        # Belohne, wenn es weniger Lehrerwechsel im Tagesablauf gibt
        wechsel = model.lehrerwechselGewicht * sum(
            model.w[k, l, z] * 0.5
            for k in model.Klassen
            for l in model.Lehrer
            for z in model.Zeitslots
        )
        print("Wechsel berechnet")
        # Belohne, wenn Mädchen und Jungen der Klasse gleichzeitig Sport haben
        sport = model.sportunterrichtGewicht * sum(
            model.p[k, z] for k in model.Klassen for z in model.Zeitslots
        )
        print("Sport berechnet")
        # Belohne, wenn wenige Lehrer insgesamt die Klasse unterrichten
        lehrermin = model.lehrerminimumGewicht * sum(
            model.y[k, l] for k in model.Klassen for l in model.Lehrer
        )
        print("Lehrermin berechnet")
        # Setze alles zu einer Zielfunktion zusammen
        objective = (
            lehrerKlasse + tandemKlasse + partnerKlasse - wechsel + sport - lehrermin
        )
        # objective = lehrerKlasse
        return objective

    # Set objective
    model.Obj = pyomo.environ.Objective(rule=ObjRule, sense=maximize)
    print("Objective eingelesen")

    """ Deklaration von Constraints
    """
    # Lehrer müsssen in ihrer Arbeitszeit bleiben
    """Stimmt mit Model überein"""
    """Ohne Fehlermeldung einlesbar"""

    def ArbeitszeitRule(model, l):
        maxArbeit = sum(
            model.x[k, l, f, z] * Fachdauer(f, k) / len(Uebergreifend(f, k))
            for k in model.Klassen
            for f in model.Faecher
            for z in model.Zeitslots
            if (k, l, f, z) in model.Variablenmenge
        )
        constraint = maxArbeit <= Arbeitszeit(l)
        return constraint_or_feasible(constraint)

    # erstelle indexierte Constraint
    model.maxArbeitszeit = Constraint(model.Lehrer, rule=ArbeitszeitRule)
    print("ArbeitszeitRule gelesen")

    # Vorgaben, sowohl mit als auch ohne Lehrer angegeben (If Clause)
    """Stimmt mit Model überein"""

    def VorgabeRule(model, klasse, fach, lehrer, zeitslot):
        if lehrer != 0:
            constraint = (
                sum(
                    model.x[klasse, lehrer, fach, z]
                    for z in range(
                        max(1, zeitslot + 1 - Fachdauer(fach, klasse)), zeitslot + 1
                    )
                    if (klasse, lehrer, fach, z) in model.Variablenmenge
                )
                >= 1
            )
        else:
            constraint = (
                sum(
                    model.x[klasse, l, fach, z]
                    for l in model.Lehrer
                    for z in range(
                        max(1, zeitslot + 1 - Fachdauer(fach, klasse)), zeitslot + 1
                    )
                    if (klasse, l, fach, z) in model.Variablenmenge
                )
                >= 1
            )
        return constraint_or_feasible(constraint)

    model.vorgabencheck = Constraint(model.Vorgaben, rule=VorgabeRule)
    print("VorgabenRule gelesen")

    # Räume müssen verfügbar sein
    """Stimmt mit Model überein"""

    def RaumRule(model, r, z):
        RaumNoetig = sum(
            model.x[k, l, f, t] / len(Uebergreifend(f, k))
            for f in RaumFaecher(r)
            for l in model.Lehrer
            for k in model.Klassen
            for t in range(max(1, z + 1 - Fachdauer(f, k)), z + 1)
            # Experiment, um Doppelstundenverfügbarkeit zu testen
            if RaumVerfuegbar(r,t) > 0
            if (k, l, f, t) in model.Variablenmenge
        )
        constraint = RaumNoetig <= RaumVerfuegbar(r, z)
        return constraint_or_feasible(constraint)

    # erstelle Constraints
    model.Raumverfuegbarkeit = Constraint(model.Raeume, model.Zeitslots, rule=RaumRule)
    print("RaumRule gelesen")

    faecherFuerKlasse = {}
    for klasse in Klassenmenge:
        faecherFuerKlasse[klasse] = list(
            Lehrfaecher.objects.filter(schulklasse__Name=klasse)
        )

    # [(f, f.klassengruppen, f.blockstunden) for f in Lehrfaecher.objects.filter(schulklasse__Name=klasse) if f.Name != "Tandem"]

    # Es darf nur ein Unterricht pro stunde pro klasse stattfinden, außer für geteilte Fächer
    # auch mit andersrum überprüfen pyomo.core.base.constraint.indexedConstraint oder ähnlich
    # oder auch nach Constraint (ohne alles)
    """Stimmt mit Model überein"""
    ''' Wird im Ergebnis nicht eingehalten '''

    def NureinUnterrichtRule(model, k, z):
        # faecher = Lehrfaecher.objects.filter(...)
        # erstelle die SumExpression
        maxUnterricht = sum(
            model.x[k, l, f.schulfach.Name, t] / f.klassengruppen
            for f in faecherFuerKlasse[k]
            if f.schulfach.Name != 'Tandem'
            for l in model.Lehrer
            for t in range(max(1, z + 1 - f.blockstunden), z + 1)
            if (k, l, f.schulfach.Name, t) in model.Variablenmenge
        )
        # stelle constraint auf
        constraint = maxUnterricht <= 1
        return constraint_or_feasible(constraint)

    # erstelle Constraint
    model.NureinUnterricht = Constraint(
        model.Klassen, model.Zeitslots, rule=NureinUnterrichtRule
    )
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
    """stimmt mit Model überein"""
    """dauert mit Abstand am längsten"""

    def lehrernureinUnterrichtRule(model, l, z):
        ohneCCS = sum(
            model.x[k, l, f, t]
            for k in model.Klassen
            for f in Unterricht(l)
            for t in range(max(1, z + 1 - Fachdauer(f, k)), z + 1)
            if len(Uebergreifend(f, k)) == 1
            if (k, l, f, t) in model.Variablenmenge
        )
        mitCCS = sum(
            sum(
                model.x[c, l, f, t]
                for c in Uebergreifend(f, k)
                if (c, l, f, z) in model.Variablenmenge
            )
            / (2 * len(Uebergreifend(f, k)))
            for k in model.Klassen
            for f in Unterricht(l)
            for t in range(max(1, z + 1 - Fachdauer(f, k)), z + 1)
            if len(Uebergreifend(f, k)) > 1
        )
        constraint = ohneCCS + mitCCS <= 1
        return constraint_or_feasible(constraint)

    model.LehrerUnterricht = Constraint(
        model.Lehrer, model.Zeitslots, rule=lehrernureinUnterrichtRule
    )
    print("lehrernureinUnterrichtRule gelesen")

    # Übergreifende Fächer müssen gleichzeitig stattfinden
    """Nicht komplett gleich, weil die Summe mehrer Restriktionen ersetzt wie bei parallenzusammen"""

    def UebergreifendRule(model, f, k, z):
        if len(Uebergreifend(f, k)) > 1:
            uebergreifendsumme = 0
            for klasse in Uebergreifend(f, k):
                if klasse != k:
                    uebergreifendsumme += sum(
                        model.x[k, l, f, z]
                        for l in model.Lehrer
                        if (k, l, f, z) in model.Variablenmenge
                    ) - sum(
                        model.x[klasse, l, f, z]
                        for l in model.Lehrer
                        if (klasse, l, f, z) in model.Variablenmenge
                    )
            constraint = uebergreifendsumme == 0
            return constraint_or_feasible(constraint)
        else:
            return Constraint.Feasible

    model.Uebergreifend = Constraint(
        model.Faecher, model.Klassen, model.Zeitslots, rule=UebergreifendRule
    )
    print("UebergreifendRule gelesen")

    # Übergreifende Fächer brauchen auch den gleichen Lehrer
    """Auch hier eine extra Summe, eventuell mit Index arbeiten """

    def UebergreifendgleicherLehrerRule(model, f, l, z, k):
        if len(Uebergreifend(f, k)) > 1:
            lehrersumme = 0
            for klasse in Uebergreifend(f, k):
                if klasse != k and (klasse, l, f, z) in model.Variablenmenge:
                    lehrersumme += model.x[k, l, f, z] - model.x[klasse, l, f, z]
            constraint = lehrersumme == 0
            return constraint_or_feasible(constraint)
        else:
            return Constraint.Feasible

    model.UebergreifendgleicherLehrer = Constraint(
        model.Faecher,
        model.Lehrer,
        model.Zeitslots,
        model.Klassen,
        rule=UebergreifendgleicherLehrerRule,
    )
    print("UebergreifendgleicherLehrertRule gelesen")

    # Parallele Fächer müsssen gleichzeitig stattfinden
    """Nicht komplett wie im Modell, da hier mit zusätzlicher summe, also nochmal prüfen"""

    def ParallelzusammenRule(model, f, k, z):
        gleichzeitigMenge = GleichzeitigFach(f)
        if gleichzeitigMenge != []:
            parallelsumme = 0
            for parfach in gleichzeitigMenge:
                parallelsumme += sum(
                    model.x[k, l, f, z]
                    for l in model.Lehrer
                    if (k, l, f, z) in model.Variablenmenge
                ) - sum(
                    model.x[k, l, parfach, z]
                    for l in model.Lehrer
                    if (k, l, parfach, z) in model.Variablenmenge
                )
            constraint = parallelsumme == 0
        else:
            constraint = Constraint.Feasible
        return constraint_or_feasible(constraint)

    model.Parallelzusammen = Constraint(
        model.Faecher, model.Klassen, model.Zeitslots, rule=ParallelzusammenRule
    )
    print("ParallelzusammenRule gelesen")

    # Jede Klasse muss ihren Lehrplan erfüllen
    """Stimmt mit Model überein"""

    def LehrplanRule(model, f, k):
        mindestUnterricht = sum(
            model.x[k, l, f, z] * Fachdauer(f, k) / GeteilteFaecher(f, k)
            for l in model.Lehrer
            for z in model.Zeitslots
            if (k, l, f, z) in model.Variablenmenge
        )
        constraint = mindestUnterricht >= Lehrplanstunden(f, k)
        return constraint_or_feasible(constraint)

    model.Lehrplanerfuellt = Constraint(model.Faecher, model.Klassen, rule=LehrplanRule)
    print("LehrplanRule gelesen")

    # Tandemlehrer muss anwesend sein wenn gefordert
    """Stimmt mit Model überein"""
    ''' Für eine Klasse und ein Fach, finde die wochenstunden
    Dann summiere Tandemvariablen über diese Wochenstunden, das muss dann Tandemnummer sein
    '''
    def TandemRule(model, k, f):
        # Tandem0: summiert alle Wochenstunden für das Fach in der Klasse - die tandemstunden darin
        Tandem0 = sum(sum(model.x[k,l,f,z] for l in model.Lehrer if (k,l,f,z) in model.Variablenmenge) - sum(model.x[k,j,'Tandem',z] for j in model.Lehrer if (k,j,'Tandem',z) in model.Variablenmenge) for z in model.Zeitslots)
        #Tandem0 = sum(model.x[k,l,f,z] - model.x[k,j,'Tandem', z] for l in model.Lehrer for j in model.Lehrer for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge if (k,l,'Tandem',z) in model.Variablenmenge )
        # Diese differenz müsste Lehrplanstunden - Tandemstunden sein
        Tandem1 = Lehrplanstunden(f,k) - Tandemnummer(f,k)
        constraint = Tandem0 == Tandem1

        #TandemA = sum(model.x[k,l,'Tandem', z] for l in model.Lehrer for z in model.Zeitslots if (k,l,'Tandem',z) in model.Variablenmenge)
        # TandemB schaut für die klasse und das Fach nach wie viele Tandems benötigt werden und summiert
        # reicht hier auch einfach nur die Tandemnummer hinzuschreiben? Denn so viele wie es sein sollen, sind es dann??
        #TandemB = Tandemnummer(f,k)
        #TandemB = sum(Tandemnummer(f,k) * model.x[k,l,f,z] for l in model.Lehrer for z in model.Zeitslots if (k,l,f,z) in model.Variablenmenge)
        #constraint = TandemA == TandemB
        #print(constraint)
        return constraint_or_feasible(constraint)

    # erstelle Constraint
    model.Tandembenoetigt = Constraint(model.Klassen, model.Faecher, rule=TandemRule)
    print("TandemRule gelesen")

    """Constraints für auxiliary variables
    """

    # Restriktion für Variable y:
    """Wie im Model"""
    """ ToDo: Funktion für intelligente Arbeitszeit schreiben"""

    def auxiliaryYRule(model, k, l):
        Lehrerfaecher = Unterricht(l)
        return sum(
            model.x[k, l, f, z] * Fachdauer(f, k) / GeteilteFaecher(f, k)
            for f in Lehrerfaecher
            for z in model.Zeitslots
            if (k, l, f, z) in model.Variablenmenge
        ) <= model.y[k, l] * Arbeitszeit(l)

    model.auxilaryY = Constraint(model.Klassen, model.Lehrer, rule=auxiliaryYRule)
    print("auxiliaryYRule eingelesen")

    # Restriktion für Variable w
    """Stimmt mit Model überein"""

    def auxiliaryWRule(model, k, l, z):
        Faecher = Klassenfaecher(k)
        return (
            sum(
                model.x[k, l, f, t]
                for f in Faecher
                for t in range(max(1, z + 1 - Fachdauer(f, k)), z + 1)
                if (k, l, f, t) in model.Variablenmenge
            )
            - sum(
                model.x[k, l, g, t + 1]
                for g in Faecher
                for t in range(max(1, z + 1 - Fachdauer(g, k)))
                if (k, l, g, t + 1) in model.Variablenmenge
            )
            <= model.w[k, l, z]
        )

    model.auxiliaryW = Constraint(
        model.Klassen, model.Lehrer, model.Zeitslots, rule=auxiliaryWRule
    )
    print("auxiliaryWRule eingelesen")

    # Restriktion für Variable p
    """Stimmt mit Model überein """

    def auxiliaryPRule1(model, k, z):
        return (
            sum(
                model.x[k, l, "SportM", z]
                for l in model.Lehrer
                if (k, l, "SportM", z) in model.Variablenmenge
            )
            - sum(
                model.x[k, l, "SportW", z]
                for l in model.Lehrer
                if (k, l, "SportW", z) in model.Variablenmenge
            )
            <= model.p[k, z]
        )

    model.auxiliaryP1 = Constraint(model.Klassen, model.Zeitslots, rule=auxiliaryPRule1)
    print("auxiliaryPRule1 eingelesen")

    """Stimmt mit Model überein """

    def auxiliaryPRule2(model, k, z):
        return (
            sum(
                model.x[k, l, "SportW", z]
                for l in model.Lehrer
                if (k, l, "SportW", z) in model.Variablenmenge
            )
            - sum(
                model.x[k, l, "SportM", z]
                for l in model.Lehrer
                if (k, l, "SportM", z) in model.Variablenmenge
            )
            <= model.p[k, z]
        )

    model.auxiliaryP2 = Constraint(model.Klassen, model.Zeitslots, rule=auxiliaryPRule2)
    print("auxiliaryPRule2 eingelesen")

    return model
