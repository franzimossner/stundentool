from django.urls import path
from . import views

urlpatterns = [
    path('optimierungstart/', views.optimierung_main, name='optimierung_main'),
    path('datencheck/', views.datencheck, name='datencheck'),
    path('parameters/', views.parameters, name='parameters'),
    path('optimierung/', views.optimierung, name='optimierung'),

]
