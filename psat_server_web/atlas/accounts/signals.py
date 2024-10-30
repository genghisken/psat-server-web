from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import GroupProfile

@receiver(post_save, sender=Group)
def create_group_profile(sender, instance, created, **kwargs):
    if created:
        new_profile, profile_created = GroupProfile.objects.get_or_create(
            group=instance
        )
        if profile_created:
            # If we created a new profile then set the group's profile to it
            instance.profile = new_profile 
            instance.save()