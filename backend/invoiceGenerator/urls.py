from django.urls import path
from . import views




urlpatterns = [
    path('', views.index), # main endpoint
    path('add/', views.add_invoice, name='add_invoice'), # add invoice end point
    path('getAll/', views.get_all_invoices, name="get_all_invoices"), # get all invoices endpoint
    path('getOne/<str:invoice_id>', views.get_one_invoice, name="get_one_invoice"), # get one invoice by it's id endpoint
    path('update/<str:invoice_id>', views.update_invoice, name="update_invoice"),
    path('delete/<str:unique_uuid>/', views.delete_invoice, name='delete_invoice'), # delete invoice endpoint
]

""" 
complete end point examples

1. add new invoice    => http://localhost:8000/api/invoice/add/
2. getAll invoices    => http://localhost:8000/api/invoice/getAll
3. getOne invoice     => http://localhost:8000/api/invoice/getOne/65e262e8e7238f1f11f7bb8e(this is invoice ID)
4. delete one invoice => http://localhost:8000/api/invoice/delete/65e262f1e7238f1f11f7bb8f
5. update invoice     => http://localhost:8000/api/invoice/update/65e262f1e7238f1f11f7bb8f
"""