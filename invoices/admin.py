from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    search_fields = ('name', 'vat_id', 'billing_id', 'internal_notes')
    list_display = ('name', '_id', 'city', 'country',) 
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'email'), 
                ('billing_id', 'vat_id'),
                ('address', 'zip_code'),
                ('city', 'country'),
                ('bic', 'iban'),
            ),
        }),
    )

    def _id(self, obj):
        return obj.vat_id or obj.billing_id



@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    search_fields = ('name', 'vat_id', 'billing_id', 'internal_notes')
    list_display = ('name', '_id', 'city', 'country',) 
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'email'), 
                ('billing_id', 'vat_id'),
                ('address', 'zip_code'),
                ('city', 'country'),
            ),
        }),
        (None, {
            'fields': ('internal_notes', 'owner')
        })
    )

    def _id(self, obj):
        return obj.vat_id or obj.billing_id


class IssuedInvoiceResource(resources.ModelResource):


    def export(self, queryset=None, *args, **kwargs):
        queryset = IssuedInvoiceLine.objects.filter(invoice__in=queryset).select_related('invoice__client').order_by('invoice', 'pk')

        return super(IssuedInvoiceResource, self).export(queryset, *args, **kwargs)

    def get_field_name(self, field):
        if field.column_name.startswith('invoice__'):
            return field.column_name[len('invoice__'):]
        else:
            return 'invoice_line__%s' % field.column_name


    def before_save_instance(self, instance, using_transactions, dry_run):
        print(instance)
        print(0/0)

    class Meta:
        model = IssuedInvoiceLine
        fields = (
            'concept', 'quantity', 'unit_price', 'net', 'vat_rate', 'vat', 'amount',
            'invoice__date', 'invoice__series', 'invoice__number', 'invoice__irpf_rate', 'invoice__net', 'invoice__vat', 'invoice__irpf', 'invoice__amount',
            'invoice__client__name', 'invoice__client__billing_id', 'invoice__client__email', 'invoice__client__address', 'invoice__client__zip_code', 
            'invoice__client__city', 'invoice__client__country', 'invoice__client__vat_id'
        )
        

class IssuedInvoiceTrimesterFilter(admin.SimpleListFilter):
    title = 'Trimester'
    parameter_name = 'trimester'
    def lookups(self, request, model_admin):
        return ((i, 'T%d' % i) for i in range(1,4))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__month__gt=(int(self.value()) - 1) * 3, date__month__lte=(int(self.value()) * 3))
        return queryset


class IssuedInvoiceYearFilter(admin.SimpleListFilter):
    title = 'Year'
    parameter_name = 'year'
    def lookups(self, request, model_admin):
        from django.db.models.functions import ExtractYear
        return ((y, y) for y in IssuedInvoice.objects.annotate(year=ExtractYear('date')).values('year').order_by('-year').distinct().values_list('year', flat=True))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(date__year=int(self.value()))
        return queryset


class IssuedInvoiceLineInline(admin.TabularInline):
    model = IssuedInvoiceLine
    extra = 0


@admin.register(IssuedInvoice)
class IssuedInvoiceAdmin(ImportExportModelAdmin):
    date_hierarchy = 'date'
    list_display = ('date', 'series', 'number', 'country', 'billing_id', 'vat_id', 'name', 'net', 'vat', 'irpf', 'amount',)
    inlines = [ IssuedInvoiceLineInline ]
    readonly_fields = ('number', 'net', 'vat', 'irpf', 'amount',)
    raw_id_fields = ('owner',)
    #search_fields = ('user__first_name', 'user__last_name', 'user__email', 'name', 'address', 'city', 'billing_id', 'vat_id',)  
    list_filter = ('series', IssuedInvoiceTrimesterFilter, IssuedInvoiceYearFilter)
    resource_class = IssuedInvoiceResource
