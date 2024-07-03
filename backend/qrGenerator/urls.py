from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('add/', views.add_new_qr, name='add_new_qr'),
    path('get/', views.get_all_qrs, name='get_all_qrs'),
    path('get/<str:qr_id>/', views.get_qr_by_id, name='get_qr_by_id'),
    path('update/<str:qr_id>/', views.update_qr_by_id, name='update_qr_by_id'),
    path('delete/<str:unique_uuid>/', views.delete_qr_by_id, name='delete_qr_by_id'),
]

""" 
1. add qr => http://localhost:8000/api/qr/add/
2. get all qrs => http://localhost:8000/api/qr/get/
3. get qr by id => http://localhost:8000/api/qr/get/60f9f2e0f9a3c7f5f6e8f4a3/
4. update qr by id => http://localhost:8000/api/qr/update/60f9f2e0f9a3c7f5f6e8f4a3/
5. delete qr by id => http://localhost:8000/api/qr/delete/uuid/
"""