from django import forms
from optimierung.models import Parameters

class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameters
        fields = ['lehrerinKlasse', 'tandeminKlasse', 'partnerinKlasse', 'lehrerwechsel', 'sportunterricht', 'lehrerminimum']
