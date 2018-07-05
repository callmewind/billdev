from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model

class SignUpView(CreateView):
    model = get_user_model()
