from dataoutput.write_timetables import writingTimetables

import xpress as xp

'''
Hier wird das Optimierungsmodell an den jeweils ausgewählten Solver weitergegeben.
'''
def doeverything():
    '''Aktuell wird nur künstlich ein Run kreiert und eine bereits vorbereitete Resultdatei ausgewertet.
    Später muss das Ergebnis CSV Dateiblatt im Optimierung ordner gespeichert werden. Dann kann get getTimetableUnits seine Arbeit richtig machen
    '''
    writingTimetables.getTimetableUnits()
