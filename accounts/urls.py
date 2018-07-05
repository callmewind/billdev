from django.urls import path, include
from .views import *

app_name = 'accounts'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
]
