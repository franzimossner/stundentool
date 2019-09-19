import csv
from django.utils import timezone
from datainput.models import Lehreinheit, Schulfach, Schulklasse, OptimierungsErgebnis, Lehrer, Slot, Lehrfaecher, Tag


'''
In diesem Dokument wird das Skript gespeichert, das die X_res Datei einliest und daraus Klassenstundenpläne und Lehererstundenpläne baut und übergibt
'''

class writingTimetables(object):

    def convert_to_slot(number):
        '''converting given number from 1 to 40 to a slot in out model
        '''
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

    def getTimetableUnits():
        '''
        gehe durch X_res und finde alle Zeilen, die die gegebene Klasse haben
        Für jeden Tag, gehe durch jede Stunde und sammle die dortigen Tupel
        für jedes gefundene Tupel in einer Stunde, baue eine LehrEinheit und speichere sie (wo??)

        Line in textdatei sieht so aus: Fach, Klasse, Lehrer, Zeitslot, 1
        Todo: Wie importiere ich die textdatei, so dass die Funktion sie überhaupt bekommen kann?
        Wie greife ich auf die sachen in der Zeile der Datei korrekt zu?
        '''

        # Füge einen neuen run hinzu, bevor die Lehreinheiten gebaut werden, damit sie dem Run zugeprdnet werden können
        sp = OptimierungsErgebnis.objects.create(Zeit=timezone.now(),Index=OptimierungsErgebnis.objects.count() + 1)
        sp.save()

        with open('./X_res.csv') as csvfile:
            resultfile = csv.reader(csvfile, delimiter=',')
            next(resultfile, None)  # skip the headers

            for row in resultfile:
                fach = row[2]
                lehrer = row[1]
                slot = row[3]
                tag, stundenindex = writingTimetables.convert_to_slot(slot)
                klasse = row[0]

                Fach = Schulfach.objects.get(Name=fach)
                Lehrperson = Lehrer.objects.get(Kurzname=lehrer)
                Klasse = Schulklasse.objects.get(Name=klasse)
                Zeitslot = Slot.objects.get(Tag__Tag=tag, Stunde__Index=stundenindex)

                # für die ganze fachdauer lehreinheiten kreieren
                fachdauer = Lehrfaecher.objects.get(schulklasse=Klasse, schulfach=Fach).blockstunden

                for i in range(1, fachdauer+1):
                    # für jede stunde der fachdauer kreiere eine LehrEinheit
                    tag_nr = Tag.objects.get(Tag=tag).Index
                    if stundenindex -1+i <= 9 and tag_nr <= 5:
                        if tag_nr == 5 and stundenindex -1+i <= 4:
                            Zeitslot = Slot.objects.get(Tag__Index=tag_nr, Stunde__Index=stundenindex -1 +i)
                            le = Lehreinheit.objects.create(Schulfach= Fach, Klasse= Klasse, Lehrer= Lehrperson, Zeitslot= Zeitslot, run=sp)
                            le.save()
                        elif tag_nr != 5:
                            Zeitslot = Slot.objects.get(Tag__Index=tag_nr, Stunde__Index=stundenindex -1 +i)
                            le = Lehreinheit.objects.create(Schulfach= Fach, Klasse= Klasse, Lehrer= Lehrperson, Zeitslot= Zeitslot, run=sp)
                            le.save()
