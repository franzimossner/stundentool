from django import forms
from .models import Lehrer, Schulklasse, Schulfach

class LehrerForm(forms.Form):
    class Meta:
        name = Lehrer
