from dataoutput.write_timetables import writingTimetables
from .schulmodell import model
from .schulmodell import Datenbankzugriff
import pyomo.environ as pyo
from pyomo.environ import *
import os


'''
Hier wird das Optimierungsmodell an den jeweils ausgewählten Solver weitergegeben.
'''
'''Aktuell wird nur künstlich ein Run kreiert und eine bereits vorbereitete Resultdatei ausgewertet.
Später muss das Ergebnis CSV Dateiblatt im Optimierung ordner gespeichert werden. Dann kann get getTimetableUnits seine Arbeit richtig machen
'''
def doeverything():

    ''' Senden an den solver und festlegen des Ouputorts
    Supported Solvers: CBC, Gurobi, Cplex
    all solvers with pyomo help --solvers
    '''

    # check if file exists, then delete it if so
    if os.path.exists('./X_res.csv'):
        os.remove('./X_res.csv')

    # import solver and solve model, wirte documentation and load results
    opt = pyo.SolverFactory('glpk')
    instance = model.create_instance()
    results = opt.solve(instance, tee=True)
    results.write(num=1)
    # brauche ich das für irgendwas?
    instance.solutions.load_from(results)

    print('optimierung done')

    with open('./X_res.csv','w') as file:
        file.write('Klasse, Lehrer, Fach, Slot, Var\n')
        for v in instance.component_data_objects(Var, active=True):
            #print ("Variable",v)
            varobject = getattr(instance, str(v))
            for index in varobject:
                if varobject[index].value == 1:
                    #indexlist = []
                    for element in index:
                        file.write('{0},'.format(element))
                    file.write('{0}\n'.format(int(varobject[index].value)))




    '''Benutze kreiertes Erbegnis, um Lehreinheiten zu erstellen
    '''
    writingTimetables.getTimetableUnits()
