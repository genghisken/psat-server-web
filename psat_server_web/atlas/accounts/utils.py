import logging 

logger = logging.getLogger(__name__)

def needs_to_change_password(user):
    """
    Custom test to check if the user is logged in and has a specific attribute.
    """
    try:
        logger.debug(f"Checking if user {user.username} needs to change password.")
        logger.debug(f"User profile: {user.profile}")
        return user.profile.password_unuseable_fl
    except AttributeError:
        return False
