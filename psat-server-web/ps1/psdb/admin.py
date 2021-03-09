from psdb.models import TcsCatalogueTables
from psdb.models import TcsTransientObjects
from django.contrib import admin

class TcsObjectAdmin(admin.ModelAdmin):
    """TcsObjectAdmin.
    """

    fieldsets = [
        (None,               {'fields': ['id']}),
        ('Follow-up information', {'fields': ['external_reference_id'], 'classes': ['collapse']}),
    ]
    list_display = ('id', 'tcs_cmf_metadata_id','tcs_images_id', 'date_inserted', 'date_modified', 'object_classification', 'followup_priority', 'external_reference_id')
    search_fields = ['id']
    date_hierarchy = 'date_inserted'

admin.site.register(TcsTransientObjects, TcsObjectAdmin)
admin.site.register(TcsCatalogueTables)