from django.db import models

# Create your models here.
class Parameters(models.Model):
    """Ein Modell, um alle Parameter speichern zu können
    """
    lehrerinKlasse = models.IntegerField()
    tandeminKlasse = models.IntegerField()
    partnerinKlasse = models.IntegerField()
    lehrerwechsel = models.IntegerField()
    sportunterricht = models.IntegerField()
    lehrerminimum = models.IntegerField()


    #solver = models.CharField(choices=[("Xpress",'Xpress'), ("Pyomo",'Pyomo')], max_length=20)

    def __str__(self):
        return "{0}, {1}, {2}, {3}, {4}, {5}".format(self.lehrerinKlasse, self.tandeminKlasse, self.partnerinKlasse, self.lehrerwechsel, self.sportunterricht, self.lehrerminimum)
