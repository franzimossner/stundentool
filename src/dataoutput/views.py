from django.shortcuts import render, get_object_or_404
from datainput.models import Schulklasse, Raum, Tag, Stunde, Lehrer, Schulfach, Uebergreifung, VorgabeEinheit, Lehreinheit, OptimierungsErgebnis
import xlwt
#from django.http import HttpResponse, FileResponse
#from reportlab.pdfgen import canvas

# Create your views here.
def output_main(request):
    return render(request, 'dataoutput/output_main.html',)

'''Wo muss ich die Klasse writingTimetables/ funktion getTimetableUnits aufrufen?
'''

def output_teacher(request):
    lehrers = Lehrer.objects.order_by('Name')
    return render(request, 'dataoutput/output_teacher.html', {'lehrers': lehrers})

def output_classes(request):
    klassen = Schulklasse.objects.order_by('Name')
    return render(request, 'dataoutput/output_classes.html', {'klassen': klassen})

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

''' Ab hier Experimente zum Download von Klassenstundenplänen in Excel
'''

# def download_excel_data_Alleklassen(request):
# 	# content-type of response
# 	response = HttpResponse(content_type='application/ms-excel')
# 	#decide file name
# 	response['Content-Disposition'] = 'attachment; filename="klassenplaene.xls"'
# 	#creating workbook
# 	wb = xlwt.Workbook(encoding='utf-8')
#
# 	#adding sheet for each class
#     klassen = Schulklasse.objects.order_by('Name')
#     tage = Tag.objects.order_by('Index')
#     stunden = Stunde.objects.order_by('Index')
#
#     for klasse in klassen:
# 	       ws = wb.add_sheet("Klasse " + klasse)
#
#     	# Row to choose for the header of the data
#     	row_num = 0
#     	font_style = xlwt.XFStyle()
#     	# headers are bold
#     	font_style.font.bold = True
#     	#column header names
#         columns = ['Stunden']
#         for tag in tagen:
#     	       columns.append(tag.Tag)
#     	#write column headers in sheet
#     	for col_num in range(len(columns)):
#     		ws.write(row_num, col_num, columns[col_num], font_style)
#     	# Sheet body, remaining rows
#     	font_style = xlwt.XFStyle()
#
#     	#get your data, from database or from a text file...
#     	data = Klassenstundenplan.objects.filter(Schulklasse=klasse)
#         for lehreinheit in data:
#             row_num = lehreinheit.Zeitslot.Stunde.Index
#             tag = lehreinheit.Zeitslot.Tag.Index
#             lehrer = lehreinheit.Lehrerstundenplan.Lehrer.Kurzname
#             fach = lehreinheit.Schulfach.Name
#
#             # ws.write(row_num, col_num, content, font_style)
#     		ws.write(row_num, tag , (fach, lehrer), font_style)
#     	wb.save(response)
# 	return response

# def download_excel_data_eineklasse(request, klasse):
# 	# content-type of response
# 	response = HttpResponse(content_type='application/ms-excel')
# 	#decide file name
# 	response['Content-Disposition'] = 'attachment; filename="klassenplan_" + klasse + ".xls"'
# 	#creating workbook
# 	wb = xlwt.Workbook(encoding='utf-8')
# 	#adding sheet for the class
#     tage = Tag.objects.order_by('Index')
#     stunden = Stunde.objects.order_by('Index')
#
#     ws = wb.add_sheet("Klasse " + klasse)
# 	# Row to choose for the header of the data
# 	row_num = 0
# 	font_style = xlwt.XFStyle()
# 	# headers are bold
# 	font_style.font.bold = True
# 	#column header names
#     columns = ['Stunden']
#     for tag in tagen:
# 	       columns.append(tag.Tag)
# 	#write column headers in sheet
# 	for col_num in range(len(columns)):
# 		ws.write(row_num, col_num, columns[col_num], font_style)
# 	# Sheet body, remaining rows
# 	font_style = xlwt.XFStyle()
#
# 	#get your data, from database or from a text file...
# 	data = Klassenstundenplan.objects.filter(Schulklasse=klasse)
#     for lehreinheit in data:
#         row_num = lehreinheit.Zeitslot.Stunde.Index
#         tag = lehreinheit.Zeitslot.Tag.Index
#         lehrer = lehreinheit.Lehrerstundenplan.Lehrer.Kurzname
#         fach = lehreinheit.Schulfach.Name
#
#         # ws.write(row_num, col_num, content, font_style)
# 		ws.write(row_num, tag , (fach, lehrer), font_style)
#     wb.save(response)
# 	return response
#
#
# ''' Ab hier Experimente zum Download von Klassenstundenplänen als PDF
# '''
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
