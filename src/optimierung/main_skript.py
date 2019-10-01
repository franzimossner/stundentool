from dataoutput.write_timetables import writingTimetables
from .schulmodell import createModel
#from .schulmodell import Datenbankzugriff
import pyomo.environ as pyo
from pyomo.environ import *
import os

# Aus schulmodell.py
from pyomo.environ import *
import cProfile
import time
import datetime

#import von Django Model Klassen
from datainput.models import Raum, Lehrer, Schulklasse, Schulfach, Lehrfaecher, Unterrricht, Tag, Stunde, Slot, Partner, LehrerBelegt, RaumBelegt, VorgabeEinheit, Uebergreifung, LehrerBelegt, StundenzahlproTag
from optimierung.models import Parameters



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
    model = createModel()
    #model.pprint('model-debug.txt')
    opt = pyo.SolverFactory('glpk')
    #instance = model.create_instance()
    results = opt.solve(model, tee=True)
    results.write(num=1)
    # brauche ich das für irgendwas?
    #solutions.load_from(results
    model.display('results.txt')

    print('optimierung done')

    with open('./X_res.csv','w') as file:
        file.write('Klasse, Lehrer, Fach, Slot, Var\n')
        for v_data in model.component_data_objects(Var, descend_into=True):
            #print ("Variable",v)
            #varobject = getattr(model, str(v))
            #for index in varobject:
                #if varobject[index].value == 1:
                    #indexlist = []
                    #for element in index:

            file.write('{0},'.format(v_data.name))
            file.write('{0}\n'.format(value(v_data)))




    '''Benutze kreiertes Erbegnis, um Lehreinheiten zu erstellen
    '''
    writingTimetables.getTimetableUnits()
