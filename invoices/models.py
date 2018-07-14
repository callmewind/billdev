from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from localflavor.generic.models import BICField, IBANField
from django_countries.fields import CountryField
from datetime import date


class BillingInfo(models.Model):
    name = models.CharField(_('name'), max_length=300)
    billing_id = models.CharField(_('billing id'), max_length=50, blank=True)
    email = models.EmailField(_('email'), max_length=254)
    address = models.CharField(_('address'), max_length=500)
    zip_code = models.CharField(_('zip code'), max_length=50)
    city = models.CharField(_('city'), max_length=100)
    country = CountryField()
    vat_id = models.CharField(_('vat id'), max_length=50, blank=True)


    def clean(self):
        super().clean()
        if not self.vat_id and not self.billing_id:
            from django.core.exceptions import ValidationError
            raise ValidationError('You must fill either billing or vat id')
        import re
        self.vat_id = re.sub(r'[^A-Z0-9]', '', self.vat_id.upper())
        self.billing_id = re.sub(r'[^A-Z0-9]', '', self.billing_id.upper())

    def __str__(self):
        return self.name
    
    class Meta:
        abstract = True



class Client(BillingInfo):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, related_name='clients')
    internal_notes = models.TextField(_('description'), blank=True)



class BillingProfile(BillingInfo):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, models.CASCADE)
    bic = BICField(blank=True)
    iban = IBANField(blank=True)


    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_profile(sender, instance, created=False, **kwargs):
        if created:
            BillingProfile.objects.create(user=instance)



class IssuedInvoice(BillingInfo):
    date = models.DateField(_('date'), default=date.today)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, models.PROTECT)
    client = models.ForeignKey(Client, models.PROTECT, related_name='invoices')
    series = models.CharField(_('series'), max_length=20)
    number = models.PositiveIntegerField(_('number'), editable=False)
    irpf_rate = models.DecimalField(_('irpf rate'), max_digits=5, decimal_places=2, default=0)
    net = models.DecimalField(_('net'), max_digits=10, decimal_places=2, default=0, editable=False)
    vat = models.DecimalField(_('vat'), max_digits=10, decimal_places=2, default=0, editable=False)
    irpf = models.DecimalField(_('irpf'), max_digits=10, decimal_places=2, default=0, editable=False)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2, default=0, editable=False)



    def save(self, *args, **kwargs):
        if not self.number:
            from django.db.models import Max
            self.number = (IssuedInvoice.objects.filter(series=self.series).aggregate(Max('number'))['number__max'] or 0 ) + 1
        if self.pk:
            from django.db.models import Sum
            from django.db.models.functions import Coalesce
            totals = IssuedInvoiceLine.objects.filter(invoice=self).aggregate(net=Coalesce(Sum('net'), 0),
                vat=Coalesce(Sum('vat'), 0), amount=Coalesce(Sum('amount'), 0))
            self.net = totals['net']
            self.irpf = totals['net'] * (self.irpf_rate/100)
            self.vat = totals['vat']
            self.amount = totals['amount'] - self.irpf            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('invoices:issued-detail', kwargs={ 'pk' : self.pk })

    def __unicode__(self):
        return u'%s-%d %.2f€' % (self.series, self.number, self.amount,)

    class Meta:
        unique_together = (('series', 'number'),)



class IssuedInvoiceLine(models.Model):
    invoice = models.ForeignKey(IssuedInvoice, models.CASCADE, related_name='lines')
    concept = models.CharField(_('concept'), max_length=300)
    quantity = models.DecimalField(_('quantity'), max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(_('unit_price'), max_digits=10, decimal_places=2, help_text=_('Leave it blank for auto-calculate'), blank=True)
    net = models.DecimalField(_('net'), max_digits=10, decimal_places=2, help_text=_('Leave it blank for auto-calculate'), blank=True)
    vat_rate = models.DecimalField(_('vat rate'), max_digits=5, decimal_places=2)
    vat = models.DecimalField(_('vat'), max_digits=10, decimal_places=2, help_text=_('Leave it blank for auto-calculate'), blank=True)
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2, help_text=_('Leave it blank for auto-calculate'), blank=True)

    def save(self, *args, **kwargs):
        #Calculamos las cantidades q falten. Cantidad e iva siempre son obligatorios (si no a que jugamos), y al menos uno de (unit_price, net, amount)
        if not self.unit_price:
            if self.net:
                self.unit_price = self.net / self.quantity
            else:
                self.unit_price = (self.amount / (1 + self.vat_rate/100))/ self.quantity
        if not self.net:
            self.net = self.quantity * self.unit_price
        if not self.vat:
            self.vat = self.net * (self.vat_rate/100)
        if not self.amount:
            self.amount = self.net + self.vat
        super().save(*args, **kwargs)
        self.invoice.save()


    def __unicode__(self):
        return u'%s (x%d) %.2f€' % (self.concept, self.quantity, self.amount,)        

