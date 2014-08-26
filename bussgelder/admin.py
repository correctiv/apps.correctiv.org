from django.contrib import admin

from .models import Fine, Organisation


class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'sum_fines')
    search_fields = ['name']


class FineAdmin(admin.ModelAdmin):
    list_display = ('original_name', 'amount', 'state', 'year')
    list_filter = ('state', 'department', 'year')
    search_fields = ['original_name']
    raw_id_fields = ('organisation',)


admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Fine, FineAdmin)
