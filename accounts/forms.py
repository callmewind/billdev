from django import forms
from .models import *
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), min_length=8 )

    class Meta:
        model = get_user_model()
        fields = ('first_name','last_name', 'email', )

    def clean_email( self ):
        if User.objects.filter(email=UserManager.normalize_email(self.cleaned_data['email'])).exists():
            raise forms.ValidationError(_('This email is already in use' ))
        return self.cleaned_data['email']

    def save(self):
        return User.objects.create_user(is_active=False, **self.cleaned_data)
