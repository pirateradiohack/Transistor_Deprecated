from django.urls import path

from .views import wifi_settings

urlpatterns = [
    path("wifi_settings", wifi_settings, name='wifi_settings'),
]
