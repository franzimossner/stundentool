from django.urls import path
from . import views

urlpatterns = [
    path('ergebnisse_main/', views.output_main, name='output_main'),
    path('output_lehrer/', views.output_teacher, name='output_teacher'),
    path('output_klassen/', views.output_classes, name='output_classes'),
    path('klassenansicht/<klasse>/', views.class_detail, name='class_detail'),
    path('lehreransicht/<lehrer>/', views.teacher_detail, name='teacher_detail'),
    path('klassenansicht/<klasse>/<run>/excel', views.download_excel_1klasse_1run, name='download_excel_1klasse_1run'),
    path('klassenansicht/<run>/excel_alle', views.download_excel_data_Alleklassen, name='download_excel_data_Alleklassen'),
    path('lehreransicht/<lehrer>/<run>/excel', views.download_excel_1lehrer_1run, name='download_excel_1lehrer_1run'),
    path('lehreransicht/<run>/excel_alle', views.download_excel_data_Allelehrer, name='download_excel_data_Allelehrer'),
    #path('klassenansicht/<run>/pdf_alle', views.download_pdf_data_Alleklassen, name='download_pdf_data_Alleklassen'),



]
