from django.urls import path
from . import views




urlpatterns = [
    path('', views.index),
    path('add/', views.add_salaryslip, name='add_salaryslip'),
    path('getAll/', views.get_all_salaryslips, name="get_all_salaryslips"),
    path('getOne/<str:salary_slip_id>', views.get_one_salary_slip, name="get_one_salary_slip"),
    path('update/<str:salary_slip_id>', views.update_salaryslip, name="update_salaryslip"),
    path('delete/<str:unique_uuid>/', views.delete_salaryslip, name='delete_salaryslip'),
]

""" 
complete end point examples

1. add new salarySlip    => http://localhost:8000/api/salarySlip/add/
2. getAll salarySlips    => http://localhost:8000/api/salarySlip/getAll/
3. getOne salarySlip     => http://localhost:8000/api/salarySlip/getOne/65e262e8e7238f1f11f7bb8e/(this is salarySlip ID)
4. delete one salarySlip => http://localhost:8000/api/salarySlip/delete/65e262f1e7238f1f11f7bb8f/
5. update salarySlip     => http://localhost:8000/api/salarySlip/update/65e262f1e7238f1f11f7bb8f/
6. get one salarySlip     => http://localhost:8000/api/salarySlip/getOne/65e262f1e7238f1f11f7bb8f/
"""