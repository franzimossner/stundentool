from django.conf import settings
from django.db import models
from django.utils import timezone

class Schulklasse(models.Model):
    """ Eine normale Schulklasse
    Attribute: Name
    Relationen: hat einen Haupttandemlehrer (many-to-one)
                hat genau einen Klassenlehrer (one-to-one)
                hat mehrere Lehrfächer mit deren Attributen (many-to-many)
                hat (potentiell) mehrere Partnerlehrer (many-to-many)
                hat pro Tag eine gewissen Zahl an Stunden zu absolvieren (many-to-many)
    Der angezeigte Name im Tool ist der Name der Klasse
    """
    Name = models.CharField(max_length=20)
    HauptTandem = models.ForeignKey('Lehrer', on_delete=models.CASCADE, related_name='TandemKlassen')
    Klassenlehrer = models.OneToOneField('Lehrer', on_delete=models.CASCADE, related_name='HauptKlasse')
    Faecher = models.ManyToManyField('Schulfach', through = 'Lehrfaecher', through_fields = ('schulklasse','schulfach'))
    PartnerLehrer = models.ManyToManyField('Lehrer', through = 'Partner', through_fields=('schulklasse', 'lehrer'))
    Stundenzahlen = models.ManyToManyField('Tag', through = 'StundenzahlproTag', through_fields=('schulklasse', 'tag'))

    def __str__(self):
        return self.Name

    def getStundenzahlen(self):
        return self.stundenzahlprotag_set.order_by('tag__Index')

class Partner(models.Model):
    """ Eine Model Klasse, um die Beziehungen zwischen einer Schulklasse und ihren Partnerlehrern zu simulieren
        Der angezeigte Name im Modell ist der Name des Partnerlehrers
    """
    schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)
    lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)

    def __str__(self):
        return self.lehrer

class Uebergreifung(models.Model):
    """ Eine Model Klasse, um zu simulieren, dass bestimmte Fächer übergreifend statt finden müssen
        Im Tool wird angezeigt, um welche Klasse und um welches Fach es sich handelt
    """
    schulklasse = models.ManyToManyField('Schulklasse')
    fach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} übergreifend für {1}".format(self.fach, self.schulklasse.order_by('Name'))

class Lehrer(models.Model):
    """ Ein Lehrer der Schule
    Attribute: Name, Kurzname, Stundenzahl, Faecher
               TODO: Tandemfähig? Sportbefähigung?
    Relationen: hat Fächer, die er unterrichten kann (many-to-many)
                hat Slots, zu denen er auf nicht verfügbar geschaltet werden kann (many-to-many)
    Im Tool wird ein Lehrer mit seinem vollen Namen angezeigt
    """
    Name = models.CharField(max_length=50)
    Kurzname = models.CharField(max_length=10)
    Stundenzahl = models.IntegerField(default=0)
    #Sport = models.CharField(choices= [(1, 'Ja'), (0, 'Nein')], default=1, max_length=10)
    Tandem = models.CharField(choices= [("1", "Ja"), ("0", "Nein")], default="1", max_length=10)
    Faecher = models.ManyToManyField('Schulfach', through ='Unterrricht', through_fields=('lehrer', 'fach'))
    NichtDa = models.ManyToManyField('Slot', through = 'LehrerBelegt', through_fields= ('lehrer', 'slot'))

    def __str__(self):
        return self.Name

class RaumBelegt(models.Model):
    """ Eine Model Klasse, um zu simulieren, wann ein Raum belegt, also nicht verfügbar ist
        Im Tool wird angezeigt, welcher Raum und welche Zeit geblockt sind
    """
    raum = models.ForeignKey('Raum', on_delete=models.CASCADE)
    slot = models.ForeignKey('Slot', on_delete =models.CASCADE)

    def __str__(self):
        return "{0} nicht frei in {1}".format(self.raum, self.slot)

class LehrerBelegt(models.Model):
    """ Eine Model Klasse, um zu simulieren, wann ein Raum oder ein Lehrer belegt, also nicht verfügbar ist
        Im Tool wird angezeigt, welcher Lehrer zu welcher Zeit nicht da ist
    """
    lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)
    slot = models.ForeignKey('Slot', on_delete =models.CASCADE)

    def __str__(self):
        return "{0} kann nicht in {1}".format(self.lehrer, self.slot)

class Unterrricht(models.Model):
    """ Eine Model Klasse, um zu simulieren, welche Fächer ein Lehrer unterrrichten kann
    """
    lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)
    fach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} unterrichtet {1}".format(self.lehrer, self.fach)

class Raum(models.Model):
    """ Ein normaler Raum
    Attribute: Name, Beschreibung
    Relationen: hat mehrere Fächer, die hier unterrrichtet werden können (many-to-many)
                hat mehrere Slots, in denen er belegt und somit nicht verfügbar ist (many-to-many)
    """
    Name = models.CharField(max_length=50)
    Beschreibung = models.TextField(blank=True)
    faecher = models.ManyToManyField('Schulfach', through = 'Nutzbar', through_fields =('raum', 'schulfach'))
    Nichtfrei = models.ManyToManyField('Slot', through = 'RaumBelegt', through_fields = ('raum', 'slot'))

    def __str__(self):
        return self.Name

class Nutzbar(models.Model):
    """ Eine Model Klasse, um zu simulieren, welche fächer im gegeben Raum unterrichtet werden können
    """
    raum = models.ForeignKey('Raum', on_delete=models.CASCADE)
    schulfach = models.ForeignKey('Schulfach', on_delete =models.CASCADE)

    def __str__(self):
        return "{0} nutzbar für {1}".format(self.raum, self.schulfach)

class Slot(models.Model):
    """ Ein Slot im Stundenplan, er beinhaltet potentiell mehrere Lehreinheiten
    Attribute: -
    Relationen: hat einen Tag zugewiesen (many-to-one)
                hat eine Stunde zugewiesen (many-to-one)

    """
    Tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    Stunde = models.ForeignKey('Stunde', on_delete=models.CASCADE)

    def __str__(self):
        return "{0}, {1}".format(self.Tag, self.Stunde)

class Stunde(models.Model):
    Stunde = models.CharField(max_length=20)
    Index = models.IntegerField()

    def __str__(self):
        return self.Stunde


class Schulfach(models.Model):
    """ Ein Schulfach der Schule
    Attribute: Name
    Relationen: hat eventuell mehrere parallel stattfindende Schulfächer
    """
    Name = models.CharField(max_length=50)
    Parallel = models.ForeignKey('Schulfach', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.Name

class Lehrfaecher(models.Model):
    """ Eine Model Klasse, um zu simulieren, welche Attribute die Fächer im Lehrplan haben
    """
    schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)
    schulfach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)

    wochenstunden = models.IntegerField()
    tandemstunden = models.IntegerField(default=0)
    klassengruppen = models.IntegerField(default=1)
    verpflichtend = models.CharField(choices= [("muss", 'Muss getrennt werden'), ("kann", 'Kann getrennt werden')], default="kann", max_length=10)
    blockstunden = models.IntegerField(default=1)

    def __str__(self):
        return "Lehrplan: {0} mit {1}, Attribute {2}, {3}, {4}, {5}, {6}".format(self.schulklasse, self.schulfach, self.wochenstunden, self.tandemstunden, self.blockstunden, self.klassengruppen, self.blockstunden)

class Lehreinheit(models.Model):
    """ Eine Lehreinheit.
    Attribute: -
    Relationen: hat genau ein Fach (many-to-one)
                hat genau einen Lehrerstundenplan und damit genau einen Lehrer (many-to-one)
                hat genau einen Klassenstundenplan und damit genau eine Klasse (many-to-one)
                findet in genau einem Slot statt (many-to-one)
    """
    Schulfach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)
    Lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)
    Zeitslot = models.ForeignKey('Slot', on_delete=models.CASCADE)
    Klasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)
    run = models.ForeignKey('OptimierungsErgebnis', on_delete=models.CASCADE)


    def __str__(self):
        return "LehrEinheit: {0}, {1}, {2}, {3}".format(self.Zeitslot, self.Lehrer, self.Schulfach, self.Klasse)

class Klassenstundenplan(models.Model):
    """ Ein Stundenplan. Hier werden Ergebnisse gespeichert
    Attribute: -
    Relationen: hat eine Schulklasse (many-to-one)
    """
    Schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)

    def __str__(self):
        return self.Schulklasse

class Lehrerstundenplan(models.Model):
    """ Ein Stundenplan. Hier werden Ergebnisse gespeichert
    Attribute: -
    Relationen: hat einen Lehrer (many-to-one)
    """
    Lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)

    def __str__(self):
        return self.Lehrer

class OptimierungsErgebnis(models.Model):
    Zeit = models.DateTimeField()

    def __str__(self):
        return "{0}".format(self.Zeit)

class VorgabeEinheit(models.Model):
    """ Eine Zeiteinheit für die Vorgaben
    Attribute:
    Relationen: hat maximal einen slot (many-to-one)
                hat maximal einen Lehrer (many-to-one)
                hat maximal ein Schulfach (many-to-one)
                hat maximal eine Klasse (many-to-one)
    """
    class Meta:
        unique_together = ['Schulklasse', 'Fach', 'Zeitslot']

    Zeitslot = models.ForeignKey('Slot', on_delete=models.CASCADE)
    Lehrperson = models.ForeignKey('Lehrer', blank=True, null=True, on_delete=models.CASCADE)
    Fach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)
    Schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)

    def __str__(self):
        return "{0}, {1}, {2}".format(self.Lehrperson, self.Fach, self.Schulklasse)

class Tag(models.Model):
    Tag = models.CharField(max_length=20)
    Index = models.IntegerField()

    def __str__(self):
        return self.Tag

class StundenzahlproTag(models.Model):
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)

    Stundenzahl = models.IntegerField()

    def __str__(self):
        return "Klasse {0} hat {1} Stunden am {2}".format(self.schulklasse,self.Stundenzahl, self.tag)
