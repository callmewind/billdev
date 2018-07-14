from django.urls import path, include
from .views import *

app_name = 'invoices'

urlpatterns = [
    path('issued/', include([
        path('', IssuedList.as_view(), name='issued-list'),
        path('<int:pk>/', IssuedDetail.as_view(), name='issued-detail'),
    ]))
]
