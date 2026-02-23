import base64
import json
import time
import hmac
import hashlib
from typing import Any


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def issue_token(secret: str, sub: str, role: str = "admin", ttl_seconds: int = 60 * 60 * 12) -> str:
    payload = {
        "sub": sub,
        "role": role,
        "exp": int(time.time()) + int(ttl_seconds),
        "iat": int(time.time()),
        "v": 1,
    }
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    sig = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    return f"v1.{payload_b64}.{sig_b64}"


def verify_token(secret: str, token: str) -> dict[str, Any]:
    try:
        prefix, payload_b64, sig_b64 = token.split(".", 2)
        if prefix != "v1":
            raise ValueError("bad token version")
        expected = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
        if not hmac.compare_digest(_b64url_encode(expected), sig_b64):
            raise ValueError("bad signature")
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("token expired")
        return payload
    except Exception as e:
        raise ValueError("invalid token") from e
