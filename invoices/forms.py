from django import forms
from .models import *

class IssuedCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


    def save(self, commit=True):
        invoice = super().save(commit=False)
        invoice.owner = self.user
        if commit:
            invoice.save()
            self.save_m2m()
        return invoice

    class Meta:
        model = IssuedInvoice
        exclude = ('owner', )