from django import forms
from datainput.models import Lehrer, Schulklasse, Schulfach

class ParameterForm(forms.Form):
    lehrerinKlasse = forms.IntegerField(label='Gewichtung für den Klassenleiter')
    tandeminKlasse = forms.IntegerField(label='Gewichtung für den TandemLehrer')
    partnerinklasse = forms.IntegerField(label='Gewichtung für die Partnerlehrer')
    lehrerwechsel = forms.IntegerField(label='Gewichtung für den Lehrerwechsel')
    sportunterricht = forms.IntegerField(label='Gewichtung für den Sportunterricht')
    lehrerminimum = forms.IntegerField(label='Gewichtung für die Lehrerzahl pro Klasse')

    solver = forms.ChoiceField(label='Benutzter Solver')
