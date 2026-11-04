import re
import secrets
import string
from urllib.parse import urlparse

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 6
CUSTOM_CODE_RE = re.compile(r"^[A-Za-z0-9_-]{3,32}$")


def generate_code(length: int = CODE_LENGTH) -> str:
    """Cryptographically random short code, e.g. 'aZ3k9Q'."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def is_valid_url(url: str) -> bool:
    """Only allow http(s) URLs with a host (blocks javascript:, file:, etc.)."""
    if not isinstance(url, str) or len(url) > 2048:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def is_valid_custom_code(code: str) -> bool:
    return isinstance(code, str) and bool(CUSTOM_CODE_RE.match(code))
