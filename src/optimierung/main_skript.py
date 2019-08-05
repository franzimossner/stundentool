from dataoutput.write_timetables import writingTimetables


'''
Hier wird das Optimierungsmodell an den jeweils ausgewählten Solver weitergegeben.
'''
'''Aktuell wird nur künstlich ein Run kreiert und eine bereits vorbereitete Resultdatei ausgewertet.
Später muss das Ergebnis CSV Dateiblatt im Optimierung ordner gespeichert werden. Dann kann get getTimetableUnits seine Arbeit richtig machen
'''
def doeverything():
    ''' Import von allen Parametern und dem Schulmodell für den solver
    '''
    TODO

    ''' Senden an den solver und festlegen des Ouputorts
    Supported Solvers: CBC, Gurobi, Cplex
    all solvers with pyomo help --solvers
    '''
    #write in command line -> noch rausfinden wie
    # instance = model.create_instance()
    # opt = pyo.SolverFactory('solvername')
    # opt.solve(instance)
    # pyomo solve Schulmodell.py data.dat --solver=cplex

    # geht das auch ohne .dat file sondern mit direktimport?

    '''Benutze kreiertes Erbegnis, um Lehreinheiten zu erstellen
    '''
    writingTimetables.getTimetableUnits()
