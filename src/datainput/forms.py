from django import forms
from .models import Lehrer, Schulklasse, Schulfach, Unterrricht, Uebergreifung, LehrerBelegt, StundenzahlproTag, VorgabeEinheit, Partner, Lehrfaecher, Raum, Nutzbar, RaumBelegt

class LehrerForm(forms.ModelForm):
    class Meta:
        model = Lehrer
        exclude = ['NichtDa', 'Faecher']

class UnterrrichtForm(forms.ModelForm):
    class Meta:
        model = Unterrricht
        fields = ['lehrer', 'fach']

class SchulfachForm(forms.ModelForm):
    class Meta:
        model = Schulfach
        fields = ['Name', 'Parallel']

class UebergreifungForm(forms.ModelForm):
    class Meta:
        model = Uebergreifung
        fields = ['schulklasse', 'fach']

class BlockenForm(forms.ModelForm):
    class Meta:
        model = LehrerBelegt
        fields = ['lehrer', 'slot']

class TagesForm(forms.ModelForm):
    class Meta:
        model = StundenzahlproTag
        fields = ['tag', 'schulklasse', 'Stundenzahl']

class VorgabenForm(forms.ModelForm):
    class Meta:
        model = VorgabeEinheit
        fields = ['Zeitslot', 'Fach', 'Lehrperson', 'Schulklasse']

class KlassenForm(forms.ModelForm):
    class Meta:
        model = Schulklasse
        exclude = ['Faecher', 'PartnerLehrer', 'Stundenzahlen']

class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ['schulklasse', 'lehrer']

class LehrfaecherForm(forms.ModelForm):
    class Meta:
        model = Lehrfaecher
        fields = ['schulklasse', 'schulfach', 'wochenstunden', 'tandemstunden', 'klassengruppen', 'verpflichtend', 'blockstunden']

class RaumForm(forms.ModelForm):
    class Meta:
        model = Raum
        exclude = ['faecher', 'Nichtfrei']

class RaumBelegtForm(forms.ModelForm):
    class Meta:
        model = RaumBelegt
        fields = ['raum', 'slot']

class NutzbarForm(forms.ModelForm):
    class Meta:
        model = Nutzbar
        fields = ['raum', 'schulfach']
