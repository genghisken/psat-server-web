
from django.utils.timezone import timedelta
from django.contrib.auth.models import Group
from django.db import models



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

