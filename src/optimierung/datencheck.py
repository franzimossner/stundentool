from datainput.models import Schulklasse, Raum, RaumBelegt, Lehrer, LehrerBelegt, VorgabeEinheit, StundenzahlproTag, Tag, Stunde, Slot, Lehrfaecher, Schulfach

class datenpruefer(object):
    ''' In dieser Klasse wird der Datencheck gespeichert, der sicherstellt, dass keine widersprüchlichen Daten eingegeben werden

    Was hier überprüft wird:
    - Die Summe der eingegeben Wochenstunden im Lehrplan muss der Summe der stundenprotag minus der Mittagspause ergeben (check_lehrplan)
    - Die Summe der eingegeben wochenstunden für alle Klassen, die einen bestimmten Raum benötigen, darf nicht die gesamtKapazität des Raums übersteigen (check_raum)
    - Der eingegebene Lehrer darf nicht zu gleichen Zeit bei /lehrerblocken geblockt sein (check_vorgaben)
    - Der eingegebene Lehrer muss das eingegebene Fach auch unterrichten können (check_vorgaben)
    - Das eingegebene Fach muss auch Teil des Lehrplans der Klasse sein (check_vorgaben)
    '''
    # Erstelle Liste um eventuelle Fehler zu speichern
    message = []

    def machdencheck(self):
        print("machdencheck")

        # for each part of the input data initialize the check
        self.check_lehrplan(self)
        self.check_raum(self)
        self.check_vorgaben(self)

        return self.message

    def check_lehrplan(self):
        """ Hier wird geprüft
            - Die Summe der eingegeben wochenstunden im Lehrplan muss der Summe der stundenprotag minus der Mittagspause ergeben
        """
        klassen = Schulklasse.objects.order_by('Name')
        tage = Tag.objects.order_by('Index')

        for klasse in klassen:
            stundenzahlen = 0
            for tag in tage:
                # Hier möchte ich als zahl die stunden der Klasse an diesem Tag
                stundenzahl = klasse.getStundenzahlen().filter(tag=tag).first()
                if stundenzahl:
                    stundenzahlen += stundenzahl.Stundenzahl
            lehrplanzahlen = 0
            for fach in klasse.lehrfaecher_set.all():
                # Hier möchte ich als zahl die wochenstunden des fachs für diese Klasse
                lehrplanzahlen += fach.wochenstunden
            if stundenzahlen != lehrplanzahlen:
                self.message.append("Die Klasse {} hat nicht die richtige Zahl an Stunden. Im Lehrplan stehen {} Stunden, die Klasse hat aber {} Stunden zur Vefügung".format(klasse.Name, lehrplanzahlen, stundenzahlen))

    def check_raum(self):
        """ Hier wird geprüft
            - Die Summe der eingegeben wochenstunden für alle Klassen, die einen bestimmten Raum benötigen, darf nicht die gesamtKapazität des Raums übersteigen
        """
        klassen = Schulklasse.objects.order_by('Name')
        raeume = Raum.objects.order_by('Name')

        for raum in raeume:
            Faecher = raum.faecher
            stundenzahl = 0
            for klasse in klassen:
                for fach in klasse.lehrfaecher_set.all():
                    # Hier möchte ich als zahl die wochenstunden des fachs für diese Klasse
                    stundenzahl += fach.wochenstunden
            # multipliziere zahl der tage mit der zahl der stunden insgesamt. An maximal so vielen slots kann der raum frei sein
            raumfreizahl = Tag.objects.all().count() * Stunde.objects.all().count()
            for belegt in RaumBelegt.objects.filter(raum=raum):
                raumfreizahl -= 1
            if raumfreizahl < stundenzahl:
                self.message.append("Raum" + raum + "hat nicht genug freie Slots, um alle Fächer unterzubringen, die benötigt werden")

        ''' Finde alle Fächer für einen Raum
            Finde diese Fächer in den Lehrplänen und addiere ihre Wochenstunden
            Finde die Summe aller freien Slots eines Raumes
            Wenn die benötigten mehr als die freien sind, dann Fehler
        '''


    def check_vorgaben(self):
        """ Hier wird geprüft
            - Der eingegebene Lehrer darf nicht zu gleichen Zeit bei /lehrerblocken geblockt sein
            - Der eingegebene Lehrer muss das eingegebene Fach auch unterrichten können
            - Das eingegebene Fach muss auch Teil des Lehrplans der Klasse sein
        """

        vorgaben = VorgabeEinheit.objects.all()

        for vorgabe in vorgaben:
            # greife auf Attribut Fach in der VorgabeEinheitzu
            fach = vorgabe.Fach#
            if fach not in vorgabe.Schulklasse.Faecher.all():
                self.message.append("Das Fach " + fach.Name + " ist nicht im Lehrplan der Klasse" + vorgabe.Schulklasse.Name + " und kann deshalb nicht vorgegeben werden")
            if vorgabe.Lehrperson != None:
                lehrer = vorgabe.Lehrperson
                if fach not in lehrer.Faecher.all():
                    self.message.append("Das Fach " + fach.Name + " kann nicht von" + lehrer.Name + " unterrichtet werden und kann deshalb nicht vorgegeben werden")
                if vorgabe.Zeitslot in lehrer.NichtDa.all():
                    self.message.append("Das Lehrer " + Lehrer.Name + " ist zum Slot" + vorgabe.Zeitslot + " nicht da und kann deshalb nicht vorgegeben werden")

        ''' Finde alle vorgaben
            Für jeder Vorgabe, finde das fach und ggf den Lehrer dazu
            Prüfe ob das Fach im Lehrplan der Klasse aus der Vorgabe ist, wenn nein, message
            Prüfe, ob der Lehrer das Fach unterrichten Kann, wenn nicht, message
            Prüfe, ob der Lehrer zum Zeitslot nicht da ist, wenn ja, message
        '''
