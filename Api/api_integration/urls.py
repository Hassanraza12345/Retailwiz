from django.urls import path
from .views import *


urlpatterns = [
    path('',login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('home/',home, name='home'),
    path('register/',register, name='register'),
    path('inventory/',inventory, name='inventory'),
    path('customer/',customer, name='customer'),
    path('supplier/',supplier, name='supplier'),
    path('reports/',reports, name='reports'),
    path('reports/sales',sales, name='sales'),
    path('reports/profit',profit, name='profit'),
    path('profit_invoice/',profit_invoice, name='profit_invoice'),
    path('profit_category/',profit_category, name='profit_category'),
    path('generate_pdf/<str:pdf_type>/',generate_pdf, name='generate_pdf'),
    path('generate_csv/<str:pdf_type>/',generate_csv, name='generate_csv'),
    path('sales_invoice/',sales_invoice_list,name='sales_invoice_list'),
    path('sales_invoice/<str:ref_str>',sales_invoice_detail,name='sales_invoice_detail'),
]

