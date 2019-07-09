from django.urls import path
from . import views

urlpatterns = [
     path('datainput_main/', views.input_main, name='input_main'),
     path('raumverwaltung/', views.room_page, name='room_page'),
     path('lehrer/', views.teacher_page, name='teacher_page'),
     path('lehrplan/', views.curriculum_page, name='curriculum_page'),
     path('lehrerblocken/', views.unavailable_page, name='unavailable_page'),
     path('parallel/', views.parallel_page, name='parallel_page'),
     path('uebergreifend/', views.uebergreifend_page, name='uebergreifend_page'),
     path('klassleiter/', views.mainteacher_page, name='mainteacher_page'),
     path('stundenprotag/', views.hoursperday_page, name='hoursperday_page'),
     path('vorgaben/', views.guidelines_page, name='guidelines_page'),
]
