import csv
from django.utils import timezone
from datainput.models import Lehreinheit, Schulfach, Schulklasse, OptimierungsErgebnis, Lehrer, Slot


'''
In diesem Dokument wird das Skript gespeichert, das die X_res Datei einliest und daraus Klassenstundenpläne und Lehererstundenpläne baut und übergibt
'''

class writingTimetables(object):

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

        with open('optimierung/X_res.csv') as csvfile:
            resultfile = csv.reader(csvfile, delimiter=',')
            next(resultfile, None)  # skip the headers

            for row in resultfile:
                fach = row[0]
                 # 1. objekt in der Zeile
                lehrer = row[2]
                # 3. Objekt in der Zeile
                tag = row[3]
                stundenindex = row[4]
                # 4. Objekt in der Zeile
                klasse = row[1]
                print(klasse)

                Fach = Schulfach.objects.get(Name=fach)
                Lehrperson = Lehrer.objects.get(Kurzname=lehrer)
                Klasse = Schulklasse.objects.get(Name=klasse)
                Zeitslot = Slot.objects.get(Tag__Tag=tag, Stunde__Index=stundenindex)

                le = Lehreinheit.objects.create(Schulfach= Fach, Klasse= Klasse, Lehrer= Lehrperson, Zeitslot= Zeitslot, run=sp)
                # le = LehrEinheit(Schulfach= fach, Klassenstundenplan= klasse, Lehrerstundenplan= lehrer, Zeitslot= slot)
                le.save()
