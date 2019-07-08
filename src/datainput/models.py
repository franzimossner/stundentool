from django.conf import settings
from django.db import models
from django.utils import timezone

class Schulklasse(models.Model):
    """ Eine normale Schulklasse
    Attribute: Name
    Relationen: hat genau einen Lehrplan (one-to-one)
                hat mehrere Partnerlehrer (many-to-many)
                hat genau ein HauptTandem (many-to-one)
                hat genau einen Klassenlehrer (one-to-one) (aber nicht jeder Lehrer ist Klassleitung??)
                hat mehrere Übergreifungen mit anderen Schulkassen bei Fächern (many-to-many)
                ist Teil von mehreren Lehreinheiten (Relation nicht von hier ausgehend, many-to-one)
    """
    Name = models.CharField(max_length=20)
    HauptTandem = models.ForeignKey('Lehrer', on_delete=models.CASCADE, related_name='TandemKlassen')
    Klassenlehrer = models.OneToOneField('Lehrer', on_delete=models.CASCADE, related_name='HauptKlasse')
    Faecher = models.ManyToManyField('Schulfach', through = 'Lehrfaecher', through_fields = ('schulklasse','schulfach'))
    PartnerLehrer = models.ManyToManyField('Lehrer', through = 'Partner', through_fields=('schulklasse', 'lehrer'))
    Stundenzahlen = models.ManyToManyField('Tag', through = 'StundenzahlproTag', through_fields=('schulklasse', 'tag'))

    def __str__(self):
        return self.Name

class Partner(models.Model):
    """ Eine Model Klasse, um die Beziehungen zwischen einer Schulklasse und ihren Partnerlehrern zu simulieren
    """
    schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)
    lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)

class Uebergreifung(models.Model):
    """ Eine Model Klasse, um zu simulieren, dass bestimmte Fächer übergreifend statt finden müssen
    TODOTODOTODOTO
    Das stimmt so nicht???
    """
    schulklasse = models.ManyToManyField('Schulklasse')
    fach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} übergreifend für {1}".format(self.fach, self.schulklasse.order_by('Name'))

class Lehrer(models.Model):
    """ Ein normaler Lehrer
    Attribute: Name, Kurzname, Stundenzahl, Faecher
    Relationen: hat mehere Slots, in denen er belegt(nicht verfügbar) ist (many-to-many)
                kann mehrere Schulfächer unterrrichten (many-to-many)
                ist Teil mehrerer VorgabeEinheiten (many-to-one) (Relation nicht von hier ausgehend)
                ist Teil mehrerer Lehreinheiten (many-to-one) (Relation nicht von hier ausgehend)
                kann PartnerLehrer, HauptTandem oder Klassenlehrer von Schulklassen sein (Relationen nicht von hier ausgehend)
    """
    Name = models.CharField(max_length=50)
    Kurzname = models.CharField(max_length=10)
    Stundenzahl = models.IntegerField(default=0)
    Faecher = models.ManyToManyField('Schulfach', through ='Unterrricht', through_fields=('lehrer', 'fach'))
    NichtDa = models.ManyToManyField('Slot', through = 'LehrerBelegt', through_fields= ('lehrer', 'slot'))

    def __str__(self):
        return self.Name

class RaumBelegt(models.Model):
    """ Eine Model Klasse, um zu simulieren, wann ein Raum oder ein Lehrer belegt, also nicht verfügbar ist
    """
    raum = models.ForeignKey('Raum', on_delete=models.CASCADE)
    slot = models.ForeignKey('Slot', on_delete =models.CASCADE)

    def __str__(self):
        return "{0} nicht frei in {1}".format(self.raum, self.slot)

class LehrerBelegt(models.Model):
    """ Eine Model Klasse, um zu simulieren, wann ein Raum oder ein Lehrer belegt, also nicht verfügbar ist
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
    """ Eine Model Klasse, um zu simulieren, wann ein Raum oder ein Lehrer belegt, also nicht verfügbar ist
    """
    raum = models.ForeignKey('Raum', on_delete=models.CASCADE)
    schulfach = models.ForeignKey('Schulfach', on_delete =models.CASCADE)

    def __str__(self):
        return "{0} nutzbar für {1}".format(self.raum, self.schulfach)

class Slot(models.Model):
    """ Ein Slot im Stundenplan
    Attribute: timeslot
    Relationen: ist Teil von mehreren Lehreinheiten und VorgabeEinheiten (beide Relationen gehen nicht von hier aus)
                ist teil des Belegunsplans von Lehrern udn Räumen (berits dort als Relation engerichtet)

    """
    Tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    Stunde = models.ForeignKey('Stunde', on_delete=models.CASCADE)

    def __str__(self):
        return "Slot ({0},{1})".format(self.Tag, self.Stunde)

class Stunde(models.Model):
    Stunde = models.CharField(max_length=20)

    def __str__(self):
        return self.Stunde


class Schulfach(models.Model):
    """ Ein Schulfach der Schule
    Attribute: Name
    Relationen: hat eventuell mehrere parallel stattfindende Fächer (many-to-one)
                hat mehrere Raumtypen, in dem es stattfinden kann (many-to-many)(Relation geht von Raum aus)
                ist Teil mehrerer VorgabeEinheiten und Lehreinheiten (many-to-one) (Relationen gehen beide von sich aus)
                ist Teil mehrerer Übergreifungen (many-to-one) (Relation geht von Schulklasse aus)
                ist Teil mehrerer Lehrpläne (many-to-many) (Relation geht von Lehrplan aus)
                kann von einem Lehrer unterrrichtet werden (many-to-many) (Relation geht von Lerhrer aus)
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
    """ Eine Lehreinheit. Definition: Ist später Teil eines Stundenplan-slots, damit simuliert werden kann, wenn Fächerfür Slots geteilt sind
    Attribute: ??
    Relationen: hat genau ein Fach (many-to-one)
                hat genau einen Lehrer (many-to-one)
                hat genau eine Klasse (many-to-one)
                findet in genau einem Slot statt (many-to-one)
                ist Teil genau eines Stundenplans (many-to-one)
    """
    Schulfach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)
    Lehrerstundenplan = models.ForeignKey('Lehrerstundenplan', on_delete=models.CASCADE)
    Zeitslot = models.ForeignKey('Slot', on_delete=models.CASCADE)
    Klassenstundenplan = models.ForeignKey('Klassenstundenplan', on_delete=models.CASCADE)

    def __str__(self):
        return "LehrEinheit: {0}, {1}, {2}, {3}".format(self.Zeitslot, self.Lehrerstundenplan, self.Schulfach, self.Klassenstundenplan)

class Klassenstundenplan(models.Model):
    """ Ein Stundenplan. Hier werden Ergebnisse gespeichert
    Attribute: Klasse, Lehrer?
    Relationen: hat mehrere Lehreinheiten als Teil (Relation is in Lehreinheit)

    Wie mache ich das hier?
    """
    Schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)

    def __str__(self):
        return self.Schulklasse

class Lehrerstundenplan(models.Model):
    """ Ein Stundenplan. Hier werden Ergebnisse gespeichert
    Attribute: Klasse, Lehrer?
    Relationen: hat mehrere Lehreinheiten als Teil (Relation is in Lehreinheit)

    Wie mache ich das hier?
    """
    Lehrer = models.ForeignKey('Lehrer', on_delete=models.CASCADE)

    def __str__(self):
        return self.Lehrer

class VorgabeEinheit(models.Model):
    """ Eine Zeiteinheit für die Vorgaben
    Attribute: ?
    Relationen: ist Teil einer Gesamt-Vorgabe (many-to-one)
                hat maximal einen slot (many-to-one)
                hat maximal einen Lehrer (many-to-one)
                hat maximal ein Schulfach (many-to-one)
    """
    Zeitslot = models.ForeignKey('Slot', on_delete=models.CASCADE)
    Lehrperson = models.ForeignKey('Lehrer', blank=True, null=True, on_delete=models.CASCADE)
    Fach = models.ForeignKey('Schulfach', on_delete=models.CASCADE)
    Schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)

    def __str__(self):
        return "VorgabeEinheit: {0}, {1}, {2}, {3}".format(self.Zeitslot, self.Lehrperson, self.Fach, self.Schulklasse)

class Tag(models.Model):
    Tag = models.CharField(max_length=20)

    def __str__(self):
        return self.Tag

class StundenzahlproTag(models.Model):
    tag = models.ForeignKey('Tag', on_delete=models.CASCADE)
    schulklasse = models.ForeignKey('Schulklasse', on_delete=models.CASCADE)

    Stundenzahl = models.IntegerField()

    def __str__(self):
        return "Klasse {0} hat {1} Stunden am {2}".format(self.schulklasse,self.Stundenzahl, self.tag)



# Code aus dem alten model

# class Belegung(models.Model):
#     Zeitslots = ["Mo1", "Mo2", "Mo3", "Mo4", "Mo5", "Mo6"]
#     belegt = models.BooleanField(Zeitslots, default=False)
#     wert = models.CharField(max_length=20, default=20)
#
#     def __str__(self):
#         return self.wert
#
# class Room(models.Model):
#     Zeitslots = ["Mo1", "Mo2", "Mo3", "Mo4", "Mo5", "Mo6"]
#     # , Mo7, Mo8, Di1, Di2, Di3, Di4, Di5, Di6, Di7, Di8,
#     #             Mi1, Mi2, Mi3, Mi4, Mi5, Mi6, Mi7, Mi8,
#     #             Do1, Do2, Do3, Do4, Do5, Do6, Do7, Do8, Fr1, Fr2, Fr3, Fr4, Fr5, Fr6]
#     Name = models.CharField(max_length=200)
#     text = models.TextField()
#     belegung = models.ForeignKey(Belegung, on_delete=models.CASCADE, default=True)
#     #Hier eine funktion, die irgendwie zuordnet, wann ein Raum frei ist
#     def __str__(self):
#         return self.Name
#
# class Klasse(models.Model):
#     Name = models.CharField(max_length=100)
#     # ForeignKey zu allen Eigenschaften?
#     def __str__(self):
#         return self.Name
#
# class Teacher(models.Model):
#     Name = models.CharField(max_length=100)
#     Stunden = models.IntegerField(default= 0)
#     Fächer = models.TextField()
#     aktiv_seit = models.DateTimeField(blank=True, null=True)
#
#     def publish(self):
#         self.aktiv_seit = timezone.localtime(timezone.now()).date()
#         self.save()
#     def __str__(self):
#         return self.Name
#
# class Curriculum(models.Model):
#     Klasse = models.CharField(max_length=100)
#     Fach = models.TextField()
#     Zahl = models.IntegerField(default= 0)
#
#     def __str__(self):
#         return self.Klasse
#
# class ParallelSubject(models.Model):
#     #title = models.CharField(max_length=100)
#     Fach = models.TextField()
#
#     def __str__(self):
#         return self.Fach
#
# class MainTeacher(models.Model):
#     Klasse = models.CharField(max_length=100)
#     Klassenleitung = models.TextField()
#
#     def __str__(self):
#         return self.Klasse
#
# class Teacherunavailable(models.Model):
#     title = models.CharField(max_length=100)
#     text = models.TextField()
#     published_date = models.DateTimeField(blank=True, null=True)
#
#     def publish(self):
#         self.published_date = timezone.now()
#         self.save()
#     def __str__(self):
#         return self.title
#
# class Hoursperday(models.Model):
#     Klasse = models.CharField(max_length=100)
#     Stundenzahl = models.TextField()
#
#     def __str__(self):
#         return self.Klasse
#
# class Guideline(models.Model):
#     Klasse = models.CharField(max_length=100, default = "Keine Klasse")
#     text = models.TextField(default= "Keine Vorgaben")
#
#     def __str__(self):
#         return self.Klasse
