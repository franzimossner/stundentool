from dataoutput.write_timetables import writingTimetables
from .schulmodell import model


'''
Hier wird das Optimierungsmodell an den jeweils ausgewählten Solver weitergegeben.
'''
'''Aktuell wird nur künstlich ein Run kreiert und eine bereits vorbereitete Resultdatei ausgewertet.
Später muss das Ergebnis CSV Dateiblatt im Optimierung ordner gespeichert werden. Dann kann get getTimetableUnits seine Arbeit richtig machen
'''
def doeverything():
    TODO

    ''' Senden an den solver und festlegen des Ouputorts
    Supported Solvers: CBC, Gurobi, Cplex
    all solvers with pyomo help --solvers
    '''
    #write in command line -> noch rausfinden wie
    # instance = model.create_instance()
    # opt = pyo.SolverFactory('solvername')
    # opt.solve(instance)
    # pyomo solve Schulmodell.py --solver=xpress

    opt = pyo.SolverFactory('xpress')
    results = opt.solve(model, tree=True)

    with open('X_res.csv') as file:
        file.write('Fach, Klasse, Lehrer, Slot, Var\n')
        for (n1,n2,n3,n4) in index_set:
            if  model.x[n2, n3, n1, n4].value == 1:
                f.write('$s, %s, %s, %s, %s\n') % (n1, n2, n3, n4, model.x[n2, n3, n1, n4].value)

    # geht das auch ohne .dat file sondern mit direktimport?

    '''Benutze kreiertes Erbegnis, um Lehreinheiten zu erstellen
    '''
    writingTimetables.getTimetableUnits()
