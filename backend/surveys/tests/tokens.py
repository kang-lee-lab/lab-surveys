"""Signing helpers so the auth tests need no Auth0 tenant and no network.

A locally generated RSA key signs real RS256 tokens and the JWKS lookup is
stubbed to hand back the matching public key, which exercises the entire
validation path -- signature, iss, aud, exp, sub -- offline.
"""

import time
from contextlib import contextmanager
from unittest import mock

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
)

DOMAIN = "test-tenant.us.auth0.com"
AUDIENCE = "urn:lab-surveys-backend"
ISSUER = f"https://{DOMAIN}/"

# A kid the "tenant" publishes. Reused by the forged-signature test, which is
# what proves signatures are verified rather than headers merely parsed.
KID = "test-signing-key"


def _generate():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    return key, pem.decode()


TENANT_KEY, TENANT_PRIVATE_PEM = _generate()
FOREIGN_KEY, FOREIGN_PRIVATE_PEM = _generate()


class _StubJWKSClient:
    """Stands in for PyJWKClient, always returning the tenant's public key."""

    def __init__(self, error=None):
        self.error = error

    def get_signing_key_from_jwt(self, token):
        if self.error is not None:
            raise self.error
        return mock.Mock(key=TENANT_KEY.public_key())


@contextmanager
def stub_jwks(error=None):
    with mock.patch(
        "labsurveysbackend.auth0._jwks_client",
        return_value=_StubJWKSClient(error),
    ):
        yield


def make_token(private_pem=TENANT_PRIVATE_PEM, algorithm="RS256", **overrides):
    """A valid token by default; pass claims to override, or None to drop one."""
    now = int(time.time())
    claims = {
        "sub": "auth0|test-user",
        "iss": ISSUER,
        "aud": AUDIENCE,
        "iat": now,
        "exp": now + 300,
    }
    claims.update(overrides)
    claims = {key: value for key, value in claims.items() if value is not None}
    return jwt.encode(claims, private_pem, algorithm=algorithm, headers={"kid": KID})


def bearer(**overrides):
    return f"Bearer {make_token(**overrides)}"
