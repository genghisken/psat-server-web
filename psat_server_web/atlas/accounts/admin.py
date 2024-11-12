"""
Customise admin interface for Group model to include GroupProfile, so default 
expiry time for tokens can be set. 
"""
import logging

from django.contrib import admin
from django.contrib.auth.models import Group
from django.forms.models import ModelForm
from .models import GroupProfile


logger = logging.getLogger(__name__)

class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        """ Should return True if data differs from initial. 
        By always returning true even unchanged inlines will get validated and saved.
        We need this because the GroupProfile needs to be created even if the default 
        values haven't been changed. 
        """
        return True

class GroupProfileInline(admin.StackedInline):
    model = GroupProfile
    can_delete = False
    extra = 1
    form = AlwaysChangedModelForm

class GroupAdmin(admin.ModelAdmin):
    inlines = (GroupProfileInline,)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)