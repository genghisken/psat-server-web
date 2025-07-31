import logging
import base64

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


def bytes2string(bytes):
    """*convert byte to string and return*

    **Key Arguments:**

    - `bytes` -- the byte string to convert
    """
    base64_bytes = base64.b64encode(bytes)
    str = base64_bytes.decode('utf-8')
    return str


def string2bytes(str):
    """*convert string to bytes and return*

    **Key Arguments:**

    - `str` -- the str string to convert to string
    """
    base64_bytes = str.encode('utf-8')
    bytes = base64.decodebytes(base64_bytes)
    return bytes
