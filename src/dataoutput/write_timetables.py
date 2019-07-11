'''
In diesem Dokument wird das Skript gespeichert, das die X_res Datei einliest und daraus Klassenstundenpläne und Lehererstundenpläne baut und übergibt
'''

class writingTimetables(object):

    def getTimetableUnits(klasse, textdatei):
        '''
        gehe durch X_res und finde alle Zeilen, die die gegebene Klasse haben
        Für jeden Tag, gehe durch jede Stunde und sammle die dortigen Tupel
        für jedes gefundene Tupel in einer Stunde, baue eine LehrEinheit und speichere sie (wo??)

        Line in textdatei sieht so aus: Fach, Klasse, Lehrer, Zeitslot, 1
        Todo: Wie importiere ich die textdatei, so dass die Funktion sie überhaupt bekommen kann?
        Wie greife ich auf die sachen in der Zeile der Datei korrekt zu?
        '''

        for line in textdatei:
            if klasse in line:
                fach = # 1. objekt in der Zeile
                leherer = # 3. Objekt in der Zeile
                slot = # 4. Objekt in der Zeile
                LehrEinheit.objects.add(Schulfach= fach, Klassenstundenplan= klasse, Lehrerstundenplan= lehrer, Zeitslot= slot)
