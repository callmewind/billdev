from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import *

class IssuedList(ListView):
    model = IssuedInvoice

class IssuedDetail(DetailView):
    model = IssuedInvoice