"""
Customise admin interface for Group model to include GroupProfile, so default 
expiry time for tokens can be set. 
"""
import logging

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.forms.models import ModelForm
from .models import GroupProfile, UserProfile


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

class GroupAdmin(BaseGroupAdmin):
    """ Customise admin interface for Group model to include GroupProfile, so 
    expiry time for tokens can be set. 
    """
    inlines = (GroupProfileInline,)
    
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
    
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 1
    form = AlwaysChangedModelForm
    
class UserAdmin(BaseUserAdmin):
    """ Customise admin interface for User model to include UserProfile, so
    unuseable_password flag can be set. 
    """
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)