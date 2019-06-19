from django.shortcuts import render
from datainput.tables import DataTable

# Create your views here.

def datainfo(request):
    info = DataTable()
    return render(request, "index.html", {'info': people})
