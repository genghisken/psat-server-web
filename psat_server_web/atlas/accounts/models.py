
from PIL import Image
from django.utils.timezone import timedelta
from django.contrib.auth.models import Group
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
import io

from .utils import bytes2string


class UserProfile(models.Model):
    """UserProfile.
    
    Extension of the User model to store additional information, such as token 
    expiration time and avatar image.
    """

    if settings.DEBUG:
        staticRoot = settings.STATICFILES_DIRS[0]
    else:
        staticRoot = settings.STATIC_ROOT
    
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
    image = models.ImageField(
        upload_to='profile_pics/',
        validators=[FileExtensionValidator(
            allowed_extensions=['gif', 'jpeg', 'jpg', 'png']
        )],
        blank=True,
        null=True,
        help_text='Optional. Upload a profile image (.gif, .png, .jpg).'
    )
    image_b64 = models.TextField(
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.image.path)
            imgByteArr = io.BytesIO()
            img.save(imgByteArr, format=img.format)
            self.image_b64 = bytes2string(imgByteArr.getvalue())
            super(UserProfile, self).save(*args, **kwargs)
  
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

