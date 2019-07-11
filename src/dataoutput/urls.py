from django.urls import path
from . import views

urlpatterns = [
    path('ergebnisse_main/', views.output_main, name='output_main'),
    path('output_lehrer/', views.output_teacher, name='output_teacher'),
    path('output_klassen/', views.output_classes, name='output_classes'),
    path('klassenansicht/<klasse>/', views.class_detail, name='class_detail'),
    path('lehreransicht/<lehrer>/', views.teacher_detail, name='teacher_detail'),

]
