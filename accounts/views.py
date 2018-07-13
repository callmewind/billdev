from django.shortcuts import render
from django.views.generic.edit import CreateView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import RedirectView
from django.conf import settings
from .forms import *


class ActivateAccountTokenGenerator(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )


class SignUpView(CreateView):
    template_name = 'accounts/sign-up.html'
    form_class = SignUpForm

    def form_valid(self, form):
        from django.template.response import TemplateResponse
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.core.mail import send_mail
        from django.urls import reverse
        import urllib
        
        user = form.save()
        
        token_generator = ActivateAccountTokenGenerator()
        
        activation_link = self.request.build_absolute_uri(
            reverse('accounts:activate', kwargs={ 
                'uidb64' : urlsafe_base64_encode(force_bytes(user.pk)).decode(), 
                'token': token_generator.make_token(user) 
            })
        )
                
        context = {
            'user' : user,
            'activation_link' : activation_link
        }
        send_mail(
            _('Activate your account'), 
            activation_link, 
            'test@example.com',
            [ user.email ], 
            html_message=activation_link)
        #send_mail(user.site, 'guides/email/promo-confirm-email.html', user.email, _('Just one click to access to your Guide %(mobile_emoji)s'  % {'mobile_emoji': u"\U0001F4F2" }), context, user.web_language)
        return TemplateResponse(self.request, 'accounts/sign-up-confirm.html', { 'email': user.email })


class ActivateView(RedirectView):

    url = settings.LOGIN_REDIRECT_URL
    
    def dispatch(self, request, *args, **kwargs):
        from django.utils.encoding import force_text
        from django.utils.http import urlsafe_base64_decode
        from django.http import Http404
        from .models import User
        try:
            user = User.objects.get(pk=force_text(urlsafe_base64_decode(self.kwargs['uidb64'])))
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise Http404

        token_generator = ActivateAccountTokenGenerator()

        if request.user.is_authenticated:
            if user.pk != request.user.pk:
                raise Http404
        elif token_generator.check_token(user, self.kwargs['token']):
            from django.contrib.auth import login
            from django.contrib import messages

            user.is_active = True
            user.save()
            login(request, user, 'django.contrib.auth.backends.ModelBackend')
            messages.success(request, _('Your account has been activated. Welcome!'))
            return super(ActivateView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


