from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
from .forms import *


class IssuedInvoiceMixin(LoginRequiredMixin):
    model = IssuedInvoice

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class IssuedList(IssuedInvoiceMixin, ListView):
    pass

class IssuedDetail(IssuedInvoiceMixin, DetailView):
    pass

class IssuedCreate(IssuedInvoiceMixin, CreateView):
    template_name = 'invoices/issuedinvoice_create.html'
    form_class = IssuedCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs