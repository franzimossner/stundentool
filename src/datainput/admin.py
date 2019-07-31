from django.contrib import admin
from .models import Lehrer, Slot, Raum, VorgabeEinheit, Schulklasse, Nutzbar, StundenzahlproTag, Schulfach, Uebergreifung, Lehreinheit, LehrerBelegt, RaumBelegt, Unterrricht, Partner, Stunde, Tag, Lehrfaecher, OptimierungsErgebnis

# Register your models here.
admin.site.register(Lehrer)
admin.site.register(Slot)
admin.site.register(Raum)
admin.site.register(VorgabeEinheit)
admin.site.register(Schulklasse)
admin.site.register(Schulfach)
admin.site.register(Uebergreifung)
admin.site.register(Lehreinheit)
admin.site.register(LehrerBelegt)
admin.site.register(RaumBelegt)
admin.site.register(Unterrricht)
admin.site.register(Partner)
admin.site.register(Stunde)
admin.site.register(Tag)
admin.site.register(Lehrfaecher)
admin.site.register(StundenzahlproTag)
admin.site.register(Nutzbar)
admin.site.register(OptimierungsErgebnis)
