import logging

from rest_framework.permissions import BasePermission, SAFE_METHODS


logger = logging.getLogger(__name__)

class HasReadAccess(BasePermission):
    def has_permission(self, request, view):
        # Allow all safe methods (GET, OPTIONS, HEAD)
        if request.method in SAFE_METHODS:
            return True

        # Allow POST if the user is authenticated
        return (request.user 
                and request.user.is_authenticated)


class HasWriteAccess(BasePermission):
    def has_permission(self, request, view):
        # Allow all safe methods (GET, OPTIONS, HEAD)
        if request.method in SAFE_METHODS:
            return True
        
        write_fl = False
        user = request.user
        # Retrieve the user's group and get the api write access flag from the 
        # group profile
        if user.groups.exists():
            try:
                group_profile = user.groups.first().profile
                write_fl = group_profile.api_write_access
            except AttributeError:
                # If the group has no profile, then there's something wrong with 
                # the database. This should be fixed by an administrator, but 
                # we don't need to block the user from accessing the API.
                msg = 'Could not authorise based on group: Group has no profile.'
                logger.error(msg)
                write_fl = False
        
        # Only allow POST to write endpoints if the user is authenticated and is
        # either in a writeable group or is a staff member
        return (request.user 
                and request.user.is_authenticated 
                and (write_fl or request.user.is_staff))