from django.contrib import admin
from .models import Lehrer, Slot, Raum, VorgabeEinheit, Schulklasse, StundenzahlproTag, Schulfach, Uebergreifung, Lehreinheit, Klassenstundenplan, Lehrerstundenplan, LehrerBelegt, RaumBelegt, Unterrricht, Partner, Stunde, Tag, Lehrfaecher

# Register your models here.
admin.site.register(Lehrer)
admin.site.register(Slot)
admin.site.register(Raum)
admin.site.register(VorgabeEinheit)
admin.site.register(Schulklasse)
admin.site.register(Schulfach)
admin.site.register(Uebergreifung)
admin.site.register(Lehreinheit)
admin.site.register(Klassenstundenplan)
admin.site.register(Lehrerstundenplan)
admin.site.register(LehrerBelegt)
admin.site.register(RaumBelegt)
admin.site.register(Unterrricht)
admin.site.register(Partner)
admin.site.register(Stunde)
admin.site.register(Tag)
admin.site.register(Lehrfaecher)
admin.site.register(StundenzahlproTag)