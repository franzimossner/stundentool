from dataoutput.write_timetables import writingTimetables
from .schulmodell import createModel
from loguru import logger as loguru_logger

# from .schulmodell import Datenbankzugriff
import pyomo.environ as pyo

# from pyomo.environ import
import os

# Aus schulmodell.py
from pyomo.environ import *
import cProfile
import time
import datetime

# import von Django Model Klassen
from datainput.models import (
    Raum,
    Lehrer,
    Schulklasse,
    Schulfach,
    Lehrfaecher,
    Unterrricht,
    Tag,
    Stunde,
    Slot,
    Partner,
    LehrerBelegt,
    RaumBelegt,
    VorgabeEinheit,
    Uebergreifung,
    LehrerBelegt,
    StundenzahlproTag,
)
from optimierung.models import Parameters


"""
Hier wird das Optimierungsmodell an den jeweils ausgewählten Solver weitergegeben.
"""
"""Aktuell wird nur künstlich ein Run kreiert und eine bereits vorbereitete Resultdatei ausgewertet.
Später muss das Ergebnis CSV Dateiblatt im Optimierung ordner gespeichert werden. Dann kann get getTimetableUnits seine Arbeit richtig machen
"""


def doeverything():

    """ Senden an den solver und festlegen des Ouputorts
    Supported Solvers: CBC, Gurobi, Cplex
    all solvers with pyomo help --solvers
    """

    # check if file exists, then delete it if so
    if os.path.exists("./X_res.csv"):
        os.remove("./X_res.csv")

    loguru_logger.info("START: create model")
    # import solver and solve model, wirte documentation and load results
    model = createModel()
    loguru_logger.info("END: create model")
    # model.pprint('model-debug.txt')
    # see https://github.com/PyUtilib/pyutilib/issues/31#issuecomment-382479024
    import pyutilib.subprocess.GlobalData

    pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False
    # opt = pyo.SolverFactory('glpk', executable='/usr/local/bin/glpsol')
    loguru_logger.info("initialize solver")
    opt = pyo.SolverFactory("gurobi")
    # instance = model.create_instance()
    loguru_logger.info("START: solve model")
    results = opt.solve(model, tee=True)
    loguru_logger.info("END: solve model")
    results.write()
    loguru_logger.info(f"SOLVER STATUS: {str(results.solver.status)}")

    # brauche ich das für irgendwas?
    # solutions.load_from(results
    #loguru_logger.info("Write model file")
    #model.write("model.lp", io_options={"symbolic_solver_labels": True})

    print("optimierung done")

    if (results.solver.status == SolverStatus.ok) and (
        results.solver.termination_condition == TerminationCondition.optimal
    ):
        loguru_logger.info("write results file")
        model.display("results.txt")
        loguru_logger.info("START: write x values")
        with open("./X_res.csv", "w") as file:
            file.write("Klasse, Lehrer, Fach, Slot, Var\n")
            for (k, l, f, s) in model.Variablenmenge:
                if pyo.value(model.x[k, l, f, s] > 0.1):
                    file.write(f"{k},{l},{f},{s},{pyo.value(model.x[k, l, f, s])}\n")
        loguru_logger.info("END: write x values")
        loguru_logger.info("Transfer solution to timetables")
        """Benutze kreiertes Ergebnis, um Lehreinheiten zu erstellen"""
        writingTimetables.getTimetableUnits()
    elif results.solver.termination_condition == TerminationCondition.infeasible:
        loguru_logger.warning("Solver status is infeasible!")
    else:
        loguru_logger.warning(
            "Solver status is not optimal and not infeasible (possibly unbounded)!"
        )
