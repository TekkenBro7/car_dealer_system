from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from users.models import User

signer = TimestampSigner()


def generate_password_reset_token(user: User) -> str:
    """
    Create a signed token containing the user's ID for password reset.
    """
    return signer.sign(str(user.pk))


def verify_password_reset_token(token: str, max_age: int = 60 * 60 * 24) -> int | None:
    """
    Verify the password reset token and return the user's ID if valid.

    Args:
        token (str): The token from the email link.
        max_age (int): Maximum token lifetime in seconds (default 24 hours).

    Returns:
        int | None: The user's ID if valid, otherwise None.
    """
    try:
        user_pk = signer.unsign(token, max_age=max_age)
        return int(user_pk)
    except (BadSignature, SignatureExpired):
        return None
