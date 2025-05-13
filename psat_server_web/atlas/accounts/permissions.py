import logging 

from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)

def has_write_permissions(user: User) -> bool:
    """Check if the user has permission to edit observation data"""
    if not user.is_authenticated:
        logger.debug("User is not authenticated.")
        return False
    
    return user.has_perm('accounts.has_write_access') or user.is_staff or user.is_superuser


class GlobalPermissions(models.Model):
    """
    A dummy model used solely for global permissions.
    This model does not store any data, but is simply used to define
    global permissions for the application.
    """

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ('has_write_access', 'Write permission: can add and update observations'),
        )
