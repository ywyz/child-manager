"""签名双提交 CSRF。"""

import base64
import hmac
import secrets
from hashlib import sha256


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def issue_csrf_token(signing_key: str) -> str:
    nonce = secrets.token_bytes(32)
    signature = hmac.new(signing_key.encode(), nonce, sha256).digest()
    return f"{_encode(nonce)}.{_encode(signature)}"


def verify_csrf_token(token: str, signing_key: str) -> bool:
    try:
        nonce_text, signature_text = token.split(".", 1)
        nonce = base64.urlsafe_b64decode(nonce_text + "=" * (-len(nonce_text) % 4))
        signature = base64.urlsafe_b64decode(signature_text + "=" * (-len(signature_text) % 4))
    except ValueError, TypeError:
        return False
    expected = hmac.new(signing_key.encode(), nonce, sha256).digest()
    return hmac.compare_digest(signature, expected)
