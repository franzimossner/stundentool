from django.shortcuts import render

# Create your views here.
def output_main(request):
    return render(request, 'dataoutput/output_main.html',)

def output_teacher(request):
    return render(request, 'dataoutput/output_teacher.html',)

def output_classes(request):
    return render(request, 'dataoutput/output_classes.html')
