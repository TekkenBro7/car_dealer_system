from django.core.signing import BadSignature, SignatureExpired, TimestampSigner

from users.models import User

signer = TimestampSigner()


def generate_username_token(user: User, new_username: str) -> str:
    """
    Creates a signed token to confirm the login change
    """
    data = f"{user.pk}:{new_username}"
    return signer.sign(data)


def verify_username_token(
    token: str, max_age: int = 60 * 60 * 24
) -> tuple[int | None, str | None]:
    """
    Verify an email confirmation token and return the user's (user_id, new_username) if valid.

    Args:
        token (str): The confirmation token from the email link.
        max_age (int, optional): Maximum token age in seconds (default: 24 hours).

    Returns:
        The user's (user_id, new_username) if the token is valid, otherwise None.
    """
    try:
        unsigned_data = signer.unsign(token, max_age=max_age)
        user_pk, new_username = unsigned_data.split(":", 1)
        return int(user_pk), new_username
    except (SignatureExpired, BadSignature, ValueError):
        return None, None
