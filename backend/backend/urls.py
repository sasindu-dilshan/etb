from django.contrib import admin
from django.urls import include, path, re_path
from common_routes.refreshTokens import refresh_token_fn
from user.views import CustomProviderAuthView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path("", include("etools.urls")),
    path("api/", include("djoser.urls")),
    path("api/", include("djoser.urls.jwt")),
    # re_path(r'^auth/', include('djoser.social.urls')),
    # re_path(r'^auth/', CustomProviderAuthView.as_view(), name='provider-auth'),
    path('auth/o/<provider>/', CustomProviderAuthView.as_view(), name='provider-auth'),
    path("api/invoice/", include('invoiceGenerator.urls')),
    path("api/user/", include('user.urls')),
    path("api/refresh/tokens/", refresh_token_fn, name="refresh_token_fn"),
    path("api/salarySlip/", include('salaryslip.urls')),
    path("api/services/", include('services.urls')),
    path("api/qr/", include('qrGenerator.urls')),
]
