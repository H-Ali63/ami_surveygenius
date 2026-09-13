
from django.urls import path
from .views import capi_supercheck
from .a_app_views import a_app_supercheck

urlpatterns = [
    path('capi', capi_supercheck.as_view(), name='capi_supercheck'),
    path('a_app', a_app_supercheck.as_view(), name='a_app_supercheck')
    ]