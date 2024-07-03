from django.urls import path

from .views import ipcalc
from .views import send_emails

urlpatterns = [
    path("calc_ip_address", ipcalc.SingleIPCalculatorAPIView.as_view()),
    path("batch_calc_ip_address", ipcalc.BatchIPCalculatorAPIView.as_view()),
    path("send_email", send_emails.EmailSenderView.as_view()),
]