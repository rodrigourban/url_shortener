import secrets  # PEP506 recommends secrets instead of random
import string


def generate_key(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(
        secrets.choice(chars) for _ in range(length)
    )
