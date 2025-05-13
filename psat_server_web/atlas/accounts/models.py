
from django.utils.timezone import timedelta
from django.contrib.auth.models import Group
from django.db import models

class UserProfile(models.Model):
    """UserProfile.
    
    Extension of the User model to store additional information, such as token 
    expiration time.
    """
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    password_unuseable_fl = models.BooleanField(
        default=False,
        help_text='If true, password requires changing before login'
    )
    
    class Meta:
        """Meta.
        """
        app_label = 'accounts'
        managed = True
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        db_table = 'auth_user_profile'


class GroupProfile(models.Model):
    """GroupProfile.
    
    Extension of the Group model to store additional information, such as token 
    expiration time.
    """
    id = models.AutoField(primary_key=True)
    group = models.OneToOneField(
        Group, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    api_write_access = models.BooleanField(
        default=False,
        help_text='Does the group have write access to the API?'
    )
    token_expiration_time = models.DurationField(
        help_text='in days, default 1 day (24*60*60 seconds)',
        default=timedelta(days=1)
    )
    description = models.TextField(
        blank=True,
        help_text='What is the group for?'
    )
    
    class Meta:
        """Meta.
        """
        app_label = 'accounts'
        managed = True
        verbose_name = 'Group Profile'
        verbose_name_plural = 'Group Profiles'
        db_table = 'auth_group_profile'

