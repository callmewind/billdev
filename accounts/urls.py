from django.urls import path, include
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
]
