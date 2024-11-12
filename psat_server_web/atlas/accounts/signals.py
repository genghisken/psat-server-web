import logging

from django.db.models import signals 
from django.dispatch import receiver
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

@receiver(signals.post_save, sender=Group)
def create_group_profile(sender, instance, created, **kwargs):
    # NOTE (2024-11-12 JL): This function is no longer needed as we have instead 
    # solved the problem of duplicate GroupProfile creation by using the 
    # AlwaysChangedModelForm in the admin interface, but I'm leaving this here 
    # as a reference for future use of signals and logging.
    logger.debug('create_group_profile called')
    logger.debug('instance: %s', instance)
    logger.debug('created: %s', created)
    
    # Disconnect the signal so we don't get into a loop
    signals.post_save.disconnect(create_group_profile, sender=Group)
    
    if created:
        logger.debug('In created block')
        
    # Reconnect the signal once we're done
    signals.post_save.connect(create_group_profile, sender=Group)
    logger.debug('create_group_profile finished')