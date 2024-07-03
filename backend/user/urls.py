from django.urls import path
from . import views

urlpatterns = [
    path('', views.index), # main endpoint
    path('register/', views.register, name='user_register'),
    path('login/', views.user_login, name="login_user"),
    path("info/", views.get_user_info, name="get_user_info"),
    path('account/update/', views.update_user_account, name="update_user_account"),
    path('account/delete/', views.delete_user_account, name="delete_user_account"),
    path('password/update/', views.update_password_only, name="update_password_only"),
    path('new/password/', views.update_password, name="update_password"),
    path('upgrade/pro/', views.upgrade_user_account_pro, name="upgrade_user_account_pro"),
    path('upgrade/premium/', views.upgrade_user_account_premium, name="upgrade_user_account_premium"),
    path('trial/pro/', views.activate_free_trial_pro, name="activate_free_trial_pro"),
    path('trial/premium/', views.activate_free_trial_premium, name="activate_free_trial_premium"),
]


""" 
1. register : http://localhost:8000/api/user/regiser/
2. login    : http://localhost:8000/api/user/login/
3. refresh tokens : http://localhost:8000/api/user/refresh/
4. update account : http://localhost:8000/api/user/account/update/
5. delete account : http://localhost:8000/api/user/account/delete/
6. update password only: http://localhost:8000/api/user/password/update/
7. upgrade to pro : http://localhost:8000/api/user/upgrade/pro/
8. upgrade to premium : http://localhost:8000/api/user/upgrade/premium/
9. activate free trial pro : http://localhost:8000/api/user/trial/pro/
10. activate free trial premium : http://localhost:8000/api/user/trial/premium/
11. get user info : http://localhost:8000/api/user/info/
12. update password : http://localhost:8000/api/user/new/password/
"""