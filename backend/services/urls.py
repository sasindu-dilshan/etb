from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('add/', views.add_tools_and_properties, name='add_tools_and_properties'),
    path('get/', views.get_all_tools, name='get_all_tools'),
    path('get/<str:tool_id>/', views.get_tool_by_id, name='get_tool_by_id'),
    path('update/<str:tool_id>/', views.update_tool_by_id, name='update_tool_by_id'),
    path('delete/<str:tool_id>/', views.delete_tool_by_id, name='delete_tool_by_id'),
    path('check_validity/', views.check_validity, name='check_validity')
]

""" 
1. add tool => http://localhost:8000/api/services/add/
2. get all tools => http://localhost:8000/api/services/get/
3. get tool by id => http://localhost:8000/api/services/get/60f9f2e0f9a3c7f5f6e8f4a3/
4. update tool by id => http://localhost:8000/api/services/update/60f9f2e0f9a3c7f5f6e8f4a3/
5. delete tool by id => http://localhost:8000/api/services/delete/60f9f2e0f9a3c7f5f6e8f4a3/
"""