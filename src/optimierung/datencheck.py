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
                stundenzahlen += klasse.Stundenzahlen.filter(Tag=tag)
            lehrplanzahlen = 0
            for fach in klasse.Faecher:
                # Hier möchte ich als zahl die wochenstunden des fachs für diese Klasse
                lehrplanzahlen += fach.wochenstunden
            if stunzahlen != lehrplanzahlen:
                self.message.append("Die Klasse" + klasse.Name + "hat nicht die richtige Zahl an Stunden. Im Lehrplan stehen " + lehrplanzahlen + " Stunden, die Klasse hat aber " + stundenzahlen + " Stunden zur Vefügung")

    def check_raum(self):
        """ Hier wird geprüft
            - Die Summe der eingegeben wochenstunden für alle Klassen, die einen bestimmten Raum benötigen, darf nicht die gesamtKapazität des Raums übersteigen
        """
        klassen = Schulklasse.objects.order_by('Name')
        raeume = Raum.objects.order_by('Name')

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
