from django.shortcuts import render, get_object_or_404
from datainput.models import Schulklasse, Raum, Tag, Stunde, Lehrer, Schulfach, Uebergreifung, VorgabeEinheit, Lehreinheit, OptimierungsErgebnis
import xlwt
import openpyxl
from django.http import HttpResponse
#from reportlab.pdfgen import canvas

# Create your views here.
def output_main(request):
    return render(request, 'dataoutput/output_main.html',)


def output_teacher(request):
    run = OptimierungsErgebnis.objects.order_by('-Index').first()
    lehrers = Lehrer.objects.order_by('Name')
    return render(request, 'dataoutput/output_teacher.html', {'lehrers': lehrers, 'run': run})


def output_classes(request):
    # aktuell nur die neueste Version zum download für alle Klassen, muss noch in eine Tabelle umgewandelt werden
    run = OptimierungsErgebnis.objects.order_by('-Index').first()
    klassen = Schulklasse.objects.order_by('Name')
    return render(request, 'dataoutput/output_classes.html', {'klassen': klassen, 'run': run})


def class_detail(request, klasse):
    klasse = get_object_or_404(Schulklasse, Name=klasse)
    runs = OptimierungsErgebnis.objects.all()
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    runToStundenplan = []
    for run in runs:
        stundenplan = []
        for stunde in stunden:
            tagesplan = []
            for tag in tage:
                tagesplan.append(klasse.lehreinheit_set.filter(Zeitslot__Stunde=stunde, Zeitslot__Tag=tag, run=run).first())
            stundenplan.append((stunde, tagesplan))
        runToStundenplan.append((klasse, stundenplan, run))
    return render(request, 'dataoutput/class_detail.html', {'runToStundenplan': runToStundenplan ,
    'tage': tage ,
    'stunden': stunden,
    'klasse': klasse,
    'runs': runs
    })


def teacher_detail(request, lehrer):
    lehrer = get_object_or_404(Lehrer, Kurzname=lehrer)
    runs = OptimierungsErgebnis.objects.all()
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    runToStundenplan = []
    for run in runs:
        stundenplan = []
        for stunde in stunden:
            tagesplan = []
            for tag in tage:
                tagesplan.append(lehrer.lehreinheit_set.filter(Zeitslot__Stunde=stunde, Zeitslot__Tag=tag, run=run).first())
            stundenplan.append((stunde, tagesplan))
        runToStundenplan.append((lehrer, stundenplan, run))
    return render(request, 'dataoutput/teacher_detail.html', {'runToStundenplan': runToStundenplan,
    'lehrer':lehrer,
    'tage': tage,
    'stunden': stunden,
    'runs' : runs
    })



''' Ab hier Code zum Download von Klassenstundenplänen in Excel
'''


def download_excel_data_Alleklassen(request, run):
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="alleKlassen_{0}_.xls"'.format(run)
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    #adding sheet for each class
    klassen = Schulklasse.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    Run = OptimierungsErgebnis.objects.get(Index=run)

    for klasse in klassen:
        ws = wb.add_sheet("Klasse {0} ".format(klasse))
        row_num = 0
        font_style = xlwt.XFStyle()
        # headers are bold
        font_style.font.bold = True
        #column header names
        columns = ['Stunden']
        for tag in tage:
               columns.append(tag.Tag)
        #write column headers in sheet
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        for stunde_num, stunde in enumerate(stunden):
            ws.write(stunde_num + 1, 0, stunde.Stunde, font_style)
            colwidth = max(len(str(stunde.Stunde)) for stunde in stunden)
            ws.col(0).width = colwidth * 367

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        #get data to filter the database
        Klasse= Schulklasse.objects.get(Name=klasse)

        #get your data, from database
        data = Lehreinheit.objects.filter(Klasse=Klasse, run=Run)
        for lehreinheit in data:
            row_num = lehreinheit.Zeitslot.Stunde.Index
            tag = lehreinheit.Zeitslot.Tag.Index
            TagName = lehreinheit.Zeitslot.Tag.Tag
            lehrer = lehreinheit.Lehrer.Kurzname
            fach = lehreinheit.Schulfach.Name

            cellobject=[fach, " ({0})".format(lehrer)]

            colwidth = max(len(str(fach)) + len(str(lehrer)), len(str(TagName)))
            # Warum 367??
            # Default value of width is 2962 units and excel points it to as 8.11 units. Hence i am multiplying 367 to length of data.
            ws.col(tag).width = colwidth * 367
            # ws.write(row_num, col_num, content, font_style)
            ws.write(row_num, tag , cellobject, font_style)
    wb.save(response)
    return response


def download_excel_1klasse_1run(request, klasse, run):
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="klassenplan_{0}_{1}.xls"'.format(klasse, run)
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    #adding sheet for the class
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')

    ws = wb.add_sheet("Klasse " + klasse)
    # Row to choose for the header of the data
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    #column header names
    columns = ['Stunden']
    for tag in tage:
           columns.append(tag.Tag)
    #write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    for stunde_num, stunde in enumerate(stunden):
        ws.write(stunde_num + 1, 0, stunde.Stunde, font_style)
        colwidth = max(len(str(stunde.Stunde)) for stunde in stunden)
        ws.col(0).width = colwidth * 367

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    #get data to filter the database
    klasse= Schulklasse.objects.get(Name=klasse)
    run = OptimierungsErgebnis.objects.get(Index=run)

    #get your data, from database or from a text file...
    data = Lehreinheit.objects.filter(Klasse=klasse, run=run)
    for lehreinheit in data:
        row_num = lehreinheit.Zeitslot.Stunde.Index
        tag = lehreinheit.Zeitslot.Tag.Index
        TagName = lehreinheit.Zeitslot.Tag.Tag
        lehrer = lehreinheit.Lehrer.Kurzname
        fach = lehreinheit.Schulfach.Name

        cellobject=[fach, " ({0})".format(lehrer)]

        colwidth = max(len(str(fach)) + len(str(lehrer)), len(str(TagName)))
        # Warum 367??
        # Default value of width is 2962 units and excel points it to as 8.11 units. Hence i am multiplying 367 to length of data.
        ws.col(tag).width = colwidth * 367
        # ws.write(row_num, col_num, content, font_style)
        ws.write(row_num, tag , cellobject, font_style)

    wb.save(response)
    return response



''' Ab hier Code zum Download von Lehrerstundenplänen in Excel
'''


def download_excel_1lehrer_1run(request, lehrer, run):
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="lehrerplan_{0}_{1}.xls"'.format(lehrer, run)
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    #adding sheet for the class
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')

    ws = wb.add_sheet("{0} ".format(lehrer))
    # Row to choose for the header of the data
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    #column header names
    columns = ['Stunden']
    for tag in tage:
           columns.append(tag.Tag)
    #write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    for stunde_num, stunde in enumerate(stunden):
        ws.write(stunde_num + 1, 0, stunde.Stunde, font_style)
        colwidth = max(len(str(stunde.Stunde)) for stunde in stunden)
        ws.col(0).width = colwidth * 367

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    #get data to filter the database
    lehrperson = Lehrer.objects.get(Kurzname=lehrer)
    run = OptimierungsErgebnis.objects.get(Index=run)

    #get your data, from database or from a text file...
    data = Lehreinheit.objects.filter(Lehrer=lehrperson, run=run)
    for lehreinheit in data:
        row_num = lehreinheit.Zeitslot.Stunde.Index
        tag = lehreinheit.Zeitslot.Tag.Index
        TagName = lehreinheit.Zeitslot.Tag.Tag
        klasse = lehreinheit.Klasse.Name
        fach = lehreinheit.Schulfach.Name

        cellobject=[fach, " ({0})".format(klasse)]

        colwidth = max(len(str(fach)) + len(str(klasse)), len(str(TagName)))
        # Warum 367??
        # Default value of width is 2962 units and excel points it to as 8.11 units. Hence i am multiplying 367 to length of data.
        ws.col(tag).width = colwidth * 367
        # ws.write(row_num, col_num, content, font_style)
        ws.write(row_num, tag , cellobject, font_style)

    wb.save(response)
    return response



def download_excel_data_Allelehrer(request, run):
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')
    #decide file name
    response['Content-Disposition'] = 'attachment; filename="alleLehrer_{0}_.xls"'.format(run)
    #creating workbook
    wb = xlwt.Workbook(encoding='utf-8')

    #adding sheet for each class
    lehrers = Lehrer.objects.order_by('Name')
    tage = Tag.objects.order_by('Index')
    stunden = Stunde.objects.order_by('Index')
    Run = OptimierungsErgebnis.objects.get(Index=run)

    for lehrer in lehrers:
        ws = wb.add_sheet("{0} ".format(lehrer))
        row_num = 0
        font_style = xlwt.XFStyle()
        # headers are bold
        font_style.font.bold = True
        #column header names
        columns = ['Stunden']
        for tag in tage:
               columns.append(tag.Tag)
        #write column headers in sheet
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        for stunde_num, stunde in enumerate(stunden):
            ws.write(stunde_num + 1, 0, stunde.Stunde, font_style)
            colwidth = max(len(str(stunde.Stunde)) for stunde in stunden)
            ws.col(0).width = colwidth * 367

        # Sheet body, remaining rows
        font_style = xlwt.XFStyle()
        #get data to filter the database
        lehrperson = Lehrer.objects.get(Name=lehrer)

        #get your data, from database
        data = Lehreinheit.objects.filter(Lehrer=lehrperson, run=Run)
        for lehreinheit in data:
            row_num = lehreinheit.Zeitslot.Stunde.Index
            tag = lehreinheit.Zeitslot.Tag.Index
            TagName = lehreinheit.Zeitslot.Tag.Tag
            klasse = lehreinheit.Klasse.Name
            fach = lehreinheit.Schulfach.Name

            cellobject=[fach, " ({0})".format(klasse)]

            colwidth = max(len(str(fach)) + len(str(lehrer)), len(str(TagName)))
            # Warum 367??
            # Default value of width is 2962 units and excel points it to as 8.11 units. Hence i am multiplying 367 to length of data.
            ws.col(tag).width = colwidth * 367
            # ws.write(row_num, col_num, content, font_style)
            ws.write(row_num, tag , cellobject, font_style)
    wb.save(response)
    return response


''' Ab hier Experimente zum Download von Klassenstundenplänen als PDF
'''
#
# def write_pdf_alleKlassen(request):
#     # Create a file-like buffer to receive PDF data.
#     buffer = io.BytesIO()
#
#     # Create the PDF object, using the buffer as its "file."
#     p = canvas.Canvas(buffer)
#
#     # Draw things on the PDF. Here's where the PDF generation happens.
#     # See the ReportLab documentation for the full list of functionality.
#
#     ''' ???? '''
#     p.drawString(100, 100, "Hello world.")
#
#     # Close the PDF object cleanly, and we're done.
#     p.showPage()
#     p.save()
#
#     # FileResponse sets the Content-Disposition header so that browsers
#     # present the option to save the file.
#     return FileResponse(buffer, as_attachment=True, filename='hello.pdf')
