from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from users.models import User

signer = TimestampSigner()


def generate_email_token(user: User) -> str:
    """Creating a signed token with the user's ID"""
    return signer.sign(str(user.pk))


def verify_email_token(token: str, max_age: int = 60 * 60 * 24) -> int | None:
    """
    Verify an email confirmation token and return the user's ID if valid.

    Args:
        token (str): The confirmation token from the email link.
        max_age (int, optional): Maximum token age in seconds (default: 24 hours).

    Returns:
        The user's ID if the token is valid, otherwise None.
    """
    try:
        user_pk = signer.unsign(token, max_age=max_age)
        return int(user_pk)
    except (SignatureExpired, BadSignature):
        return None
